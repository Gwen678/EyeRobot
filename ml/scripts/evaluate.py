#!/usr/bin/env python3
"""
Evaluate the trained detector on the augmented TEST split.

Two outputs:
  1. Standard Ultralytics metrics (mAP50, mAP50-95) via model.val(split='test').
  2. A confidence-threshold sweep with IoU>=0.5 matching against ground truth,
     reporting precision / recall / #false-positives / #false-negatives at each
     threshold. Because we prefer false negatives to false positives, we then
     recommend the LOWEST confidence whose precision >= TARGET_PRECISION (so we
     suppress false alarms while keeping as many true detections as possible).

Sample prediction images are written to ml/work/test_preds/.
"""
import os
import glob
import numpy as np
import cv2
from ultralytics import YOLO

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DS = os.path.join(ROOT, "ml", "dataset")
DATA = os.path.join(DS, "data.yaml")
WEIGHTS = os.path.join(ROOT, "ml", "runs", "duplo_yolov8n_416", "weights", "best.pt")
IMGSZ = 416
TARGET_PRECISION = 0.98   # we strongly prefer avoiding false positives


def load_gt(label_path, w, h):
    boxes = []
    if os.path.exists(label_path):
        for line in open(label_path):
            p = line.split()
            if len(p) == 5:
                _, xc, yc, bw, bh = map(float, p)
                boxes.append([(xc - bw / 2) * w, (yc - bh / 2) * h,
                              (xc + bw / 2) * w, (yc + bh / 2) * h])
    return np.array(boxes, dtype=np.float32).reshape(-1, 4)


def iou(a, b):
    ix0 = max(a[0], b[0]); iy0 = max(a[1], b[1])
    ix1 = min(a[2], b[2]); iy1 = min(a[3], b[3])
    iw = max(0, ix1 - ix0); ih = max(0, iy1 - iy0)
    inter = iw * ih
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.0


def main():
    model = YOLO(WEIGHTS)

    print("=" * 60)
    print("Ultralytics metrics on TEST split:")
    metrics = model.val(data=DATA, split="test", imgsz=IMGSZ,
                        project=os.path.join(ROOT, "ml", "runs"),
                        name="duplo_test_eval", exist_ok=True, plots=True, verbose=False)
    print(f"  mAP50     : {metrics.box.map50:.4f}")
    print(f"  mAP50-95  : {metrics.box.map:.4f}")
    print("=" * 60)

    # --- IoU-matched threshold sweep -----------------------------------
    imgs = sorted(glob.glob(os.path.join(DS, "images", "test", "*.jpg")))
    # collect (score, is_tp) over all images, plus per-image GT count
    dets = []          # (score, matched_bool)
    total_gt = 0
    for ip in imgs:
        img = cv2.imread(ip)
        h, w = img.shape[:2]
        lp = ip.replace("/images/", "/labels/").replace(".jpg", ".txt")
        gt = load_gt(lp, w, h)
        total_gt += len(gt)
        r = model.predict(ip, imgsz=IMGSZ, conf=0.001, verbose=False)[0]
        pred_boxes = r.boxes.xyxy.cpu().numpy() if r.boxes is not None else np.zeros((0, 4))
        scores = r.boxes.conf.cpu().numpy() if r.boxes is not None else np.zeros((0,))
        order = scores.argsort()[::-1]
        used = set()
        for i in order:
            best_j, best_iou = -1, 0.5
            for j in range(len(gt)):
                if j in used:
                    continue
                v = iou(pred_boxes[i], gt[j])
                if v >= best_iou:
                    best_iou, best_j = v, j
            if best_j >= 0:
                used.add(best_j)
                dets.append((float(scores[i]), True))
            else:
                dets.append((float(scores[i]), False))

    dets.sort(key=lambda x: -x[0])
    print(f"TEST images: {len(imgs)}  |  GT blocks: {total_gt}  |  raw dets: {len(dets)}")
    print(f"{'conf':>6} {'TP':>5} {'FP':>5} {'FN':>5} {'prec':>7} {'recall':>7} {'F1':>6}")
    sweep = [0.10, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
    rec_thr = None
    rows = []
    for t in sweep:
        tp = sum(1 for s, m in dets if s >= t and m)
        fp = sum(1 for s, m in dets if s >= t and not m)
        fn = total_gt - tp
        prec = tp / (tp + fp) if tp + fp else 1.0
        rec = tp / total_gt if total_gt else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        rows.append((t, tp, fp, fn, prec, rec, f1))
        print(f"{t:6.2f} {tp:5d} {fp:5d} {fn:5d} {prec:7.3f} {rec:7.3f} {f1:6.3f}")
        if prec >= TARGET_PRECISION and rec_thr is None:
            rec_thr = t

    print("=" * 60)
    if rec_thr is not None:
        r = next(x for x in rows if x[0] == rec_thr)
        print(f"Recommended deploy conf (precision>={TARGET_PRECISION}): {rec_thr:.2f}")
        print(f"  -> precision {r[4]:.3f}, recall {r[5]:.3f}, FP {r[2]}, FN {r[3]}")
    else:
        best = max(rows, key=lambda x: x[6])
        print(f"No threshold hit precision>={TARGET_PRECISION}; best-F1 conf {best[0]:.2f} "
              f"(prec {best[4]:.3f}, recall {best[5]:.3f})")

    # sample predictions for eyeballing
    out = os.path.join(ROOT, "ml", "work", "test_preds")
    os.makedirs(out, exist_ok=True)
    for ip in imgs[:16]:
        r = model.predict(ip, imgsz=IMGSZ, conf=(rec_thr or 0.25), verbose=False)[0]
        cv2.imwrite(os.path.join(out, os.path.basename(ip)), r.plot())
    print(f"Sample predictions -> {out}")


if __name__ == "__main__":
    main()
