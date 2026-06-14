#!/usr/bin/env python3
"""
Auto-label Duplo block images by colour using HSV saturation thresholding.
Outputs YOLO labels to ml/work/labels/; filenames starting with "ground" get empty label files.
"""
import os
import glob
import math
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IMG_DIR = os.path.join(ROOT, "images")
OUT_LBL = os.path.join(ROOT, "ml", "work", "labels")
WORK = os.path.join(ROOT, "ml", "work")
os.makedirs(OUT_LBL, exist_ok=True)

PROC_W = 720          # downscale width for segmentation (speed; box is normalised)
MIN_BLOB_FRAC = 0.004 # ignore colour specks smaller than this fraction of the image
PAD_FRAC = 0.02       # pad the final box by this fraction of image size
SAT_FLOOR = 45        # never threshold saturation below this (0-255)


def segment_box(img_bgr):
    """Return (xc, yc, w, h) normalised box of the block, or None on failure."""
    h0, w0 = img_bgr.shape[:2]
    scale = PROC_W / w0
    img = cv2.resize(img_bgr, (PROC_W, int(round(h0 * scale))), interpolation=cv2.INTER_AREA)
    h, w = img.shape[:2]

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    S = hsv[:, :, 1]
    S = cv2.GaussianBlur(S, (5, 5), 0)

    otsu, _ = cv2.threshold(S, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thr = max(otsu, SAT_FLOOR)
    mask = (S > thr).astype(np.uint8) * 255

    # close gaps between studs / adjacent bricks, then drop tiny noise
    k = max(3, int(0.015 * min(h, w)) | 1)
    close_k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    open_k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, open_k)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, close_k)

    # fill outer contours so neutral bricks enclosed by coloured ones are kept
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None
    img_area = float(h * w)
    big = [c for c in cnts if cv2.contourArea(c) >= MIN_BLOB_FRAC * img_area]
    if not big:
        # nothing big enough: fall back to the single largest contour
        big = [max(cnts, key=cv2.contourArea)]

    filled = np.zeros((h, w), np.uint8)
    cv2.drawContours(filled, big, -1, 255, thickness=cv2.FILLED)

    ys, xs = np.where(filled > 0)
    if xs.size == 0:
        return None
    x0, x1 = xs.min(), xs.max()
    y0, y1 = ys.min(), ys.max()

    # pad
    px = PAD_FRAC * w
    py = PAD_FRAC * h
    x0 = max(0, x0 - px); y0 = max(0, y0 - py)
    x1 = min(w - 1, x1 + px); y1 = min(h - 1, y1 + py)

    xc = (x0 + x1) / 2.0 / w
    yc = (y0 + y1) / 2.0 / h
    bw = (x1 - x0) / w
    bh = (y1 - y0) / h
    return (xc, yc, bw, bh)


def main():
    paths = sorted(glob.glob(os.path.join(IMG_DIR, "*.jpg")))
    blocks = [p for p in paths if not os.path.basename(p).lower().startswith("ground")]
    grounds = [p for p in paths if os.path.basename(p).lower().startswith("ground")]

    report = []
    thumbs = []  # (thumbnail_bgr, ok)
    failures = []

    for p in blocks:
        name = os.path.splitext(os.path.basename(p))[0]
        img = cv2.imread(p)
        box = segment_box(img)
        ok = box is not None
        with open(os.path.join(OUT_LBL, name + ".txt"), "w") as f:
            if ok:
                xc, yc, bw, bh = box
                f.write(f"0 {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")
        if not ok:
            failures.append(name)
        report.append(f"{name}\t{'OK' if ok else 'FAIL'}\t{box}")

        # thumbnail for montage
        th = 220
        sc = th / img.shape[0]
        thumb = cv2.resize(img, (int(img.shape[1] * sc), th))
        H, W = thumb.shape[:2]
        if ok:
            xc, yc, bw, bh = box
            x0 = int((xc - bw / 2) * W); y0 = int((yc - bh / 2) * H)
            x1 = int((xc + bw / 2) * W); y1 = int((yc + bh / 2) * H)
            cv2.rectangle(thumb, (x0, y0), (x1, y1), (0, 255, 0), 2)
        else:
            cv2.rectangle(thumb, (0, 0), (W - 1, H - 1), (0, 0, 255), 6)
        thumbs.append(thumb)

    # ground images get empty label files (negatives)
    for p in grounds:
        name = os.path.splitext(os.path.basename(p))[0]
        open(os.path.join(OUT_LBL, name + ".txt"), "w").close()

    # build montage(s): pad thumbs to common width, grid of 6 cols
    if thumbs:
        maxw = max(t.shape[1] for t in thumbs)
        cols = 6
        padded = []
        for t in thumbs:
            canvas = np.full((t.shape[0], maxw, 3), 30, np.uint8)
            canvas[:, : t.shape[1]] = t
            padded.append(canvas)
        rows = []
        for i in range(0, len(padded), cols):
            chunk = padded[i:i + cols]
            while len(chunk) < cols:
                chunk.append(np.full_like(padded[0], 30))
            rows.append(np.hstack(chunk))
        montage = np.vstack(rows)
        cv2.imwrite(os.path.join(WORK, "montage_blocks.jpg"), montage)

    with open(os.path.join(WORK, "autolabel_report.txt"), "w") as f:
        f.write("\n".join(report))

    print(f"Block images labeled: {len(blocks)}  (failures: {len(failures)})")
    if failures:
        print("FAILED:", ", ".join(failures))
    print(f"Ground negatives    : {len(grounds)}")
    print(f"Labels  -> {OUT_LBL}")
    print(f"Montage -> {os.path.join(WORK, 'montage_blocks.jpg')}")


if __name__ == "__main__":
    main()
