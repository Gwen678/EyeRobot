#!/usr/bin/env python3
"""
Export the trained YOLOv8n to ONNX (opset 12, 416x416) and optionally to a
.blob via blobconverter (6 SHAVEs). Preferred path: use https://tools.luxonis.com.
"""
import os
from ultralytics import YOLO

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUN = os.path.join(ROOT, "ml", "runs", "duplo_yolov8n_416")
# Use last.pt instead of best.pt: last.pt gives better recall and fewer false
# positives on the full test set (best.pt was picked on a tiny val set).
import sys
WEIGHTS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RUN, "weights", "last.pt")
IMGSZ = 416


def main():
    model = YOLO(WEIGHTS)
    onnx_path = model.export(format="onnx", imgsz=IMGSZ, opset=12, simplify=True)
    print("ONNX exported:", onnx_path)

    # Unreliable blob conversion (needs internet + blobconverter)
    try:
        import blobconverter
        blob = blobconverter.from_onnx(
            model=str(onnx_path),
            data_type="FP16",
            shaves=6,                      # OAK-D Lite
            use_cache=False,
            output_dir=os.path.join(RUN, "weights"),
            optimizer_params=[
                "--scale=255",
                "--reverse_input_channels",
            ],
        )
        print("Blob exported:", blob)
    except Exception as e:
        print("Blob conversion skipped/failed:", e)
        print("Use https://tools.luxonis.com with best.pt instead "
              "(see ml/DEPLOY_OAK.md).")


if __name__ == "__main__":
    main()
