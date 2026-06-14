#!/usr/bin/env python3
"""
Train YOLOv8n on the offline-augmented Duplo dataset.
Online augmentation is disabled because data was already augmented offline; single class 'block' with background negatives to reduce false positives.
"""
import os
from ultralytics import YOLO

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "ml", "dataset", "data.yaml")

NO_AUG = dict(
    hsv_h=0.0, hsv_s=0.0, hsv_v=0.0, degrees=0.0, translate=0.0, scale=0.0,
    shear=0.0, perspective=0.0, flipud=0.0, fliplr=0.0, mosaic=0.0, mixup=0.0,
    cutmix=0.0, copy_paste=0.0, erasing=0.0, auto_augment=None,
)


def main():
    model = YOLO("yolov8n.pt")  # COCO-pretrained, used for transfer learning
    model.train(
        data=DATA,
        epochs=100,
        patience=20,
        imgsz=416,
        batch=16,
        device="cpu",
        workers=8,
        seed=1234,
        deterministic=True,
        project=os.path.join(ROOT, "ml", "runs"),
        name="duplo_yolov8n_416",
        exist_ok=True,
        plots=True,
        **NO_AUG,
    )
    print("Best weights:", os.path.join(ROOT, "ml", "runs",
          "duplo_yolov8n_416", "weights", "best.pt"))


if __name__ == "__main__":
    main()
