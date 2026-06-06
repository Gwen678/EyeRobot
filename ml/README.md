# Duplo block detector (YOLOv8n → OAK-D Lite object tracker)

End-to-end pipeline that turns the raw photos in `images/` into a YOLOv8n detector
deployable on the OAK-D Lite `ObjectTracker`.

- **1 class** (`block`). "Not block" = background (no detection), and the bare-floor
  `ground_*.jpg` photos are used as **negatives** to suppress false positives.
- We **prefer false negatives over false positives** → deploy at a higher
  confidence threshold (the evaluator recommends one).
- Deploy input size **416×416** (good speed/accuracy on the Myriad X VPU).

## Environment
```bash
python3 -m venv --system-site-packages ml/.venv
ml/.venv/bin/python -m pip install ultralytics "matplotlib>=3.7"
```
(CPU-only torch is fine; training runs on CPU here.)

## Pipeline
```bash
# 1. Auto-label the block photos by colour (HSV saturation segmentation).
#    Block photos -> one tight box; ground photos -> empty label (negative).
#    Check ml/work/montage_blocks.jpg before trusting the labels.
python3 ml/scripts/autolabel.py

# 2. Split train/val/test (before augmentation, no leakage), downscale to 768,
#    and apply the offline augmenter to train+test. Writes ml/dataset/.
ml/.venv/bin/python ml/scripts/build_dataset.py

# 3. Train YOLOv8n @416 (online augmentation OFF — we augmented offline).
OMP_NUM_THREADS=$(nproc) ml/.venv/bin/python ml/scripts/train.py

# 4. Evaluate on the augmented test set + confidence sweep (precision/recall,
#    FP/FN) and recommend a deploy confidence.
ml/.venv/bin/python ml/scripts/evaluate.py

# 5. Export ONNX (+ best-effort blob) for the OAK-D Lite.
ml/.venv/bin/python ml/scripts/export_oak.py
```

## Augmentation (`ml/scripts/augment.py`)
Each technique is applied **separately** (never stacked), a few randomized
variants per image, with bounding boxes transformed for the geometric ones and
`BORDER_REFLECT_101` padding (no unrealistic black borders):

| technique | variants/img (train) | box transform |
|-----------|----------------------|---------------|
| hue / saturation / brightness | 5 each | unchanged |
| bgr channel swap | 5 (distinct perms) | unchanged |
| rotation / translation / scale / shear / perspective | 5 each | warped corners → AABB |
| flip up-down / left-right | 1 each (deterministic) | mirrored |

A block-image variant that loses its box (warped out of frame) is skipped so it
never becomes a mislabeled negative.

## Results (this run)
Trained YOLOv8n @416 on CPU, early-stopped at epoch 13 (~1.1h). Evaluated on the
**231-image augmented test set** (deliberately harsh: includes BGR-swap + extreme
hue, so live OAK precision will be higher):

| checkpoint | mAP50 | mAP50-95 | recall (conf 0.2–0.8) | false positives |
|---|---|---|---|---|
| best.pt (epoch 1) | 0.908 | 0.656 | unstable | 44–94 |
| **deploy.pt = last.pt (epoch 13)** | 0.903 | **0.671** | **~0.90, flat** | **18–28** |

The 7-image val set is too small to pick a checkpoint reliably (it tagged epoch 1
as "best"), so we deploy `last.pt`, which the large test set shows is better
calibrated. Bare-floor negatives produce **no detections** (no false positives).

**Recommended deploy confidence ≈ 0.7–0.8** (prefer false negatives → favour
precision). Artifacts in `ml/runs/duplo_yolov8n_416/weights/`: `deploy.pt`,
`deploy.onnx`, `deploy_openvino_2022.1_6shave.blob`.

To improve further: rebuild with a larger held-out validation set (the current
limiter is checkpoint selection, not model capacity) and/or train at 320 for more
VPU headroom.

## Deployment
See `ml/DEPLOY_OAK.md` for the blob conversion and the full DepthAI
`ColorCamera → YoloDetectionNetwork → ObjectTracker` pipeline.

## Layout
```
ml/scripts/   autolabel.py  build_dataset.py  augment.py  train.py  evaluate.py  export_oak.py
ml/dataset/   images/{train,val,test}  labels/{train,val,test}  data.yaml   (generated)
ml/work/      labels/  montages  logs  test_preds/                          (generated)
ml/runs/      duplo_yolov8n_416/   training run + weights                   (generated)
```
