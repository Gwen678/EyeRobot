#!/usr/bin/env python3
"""
Export the trained YOLOv8n to formats usable on the OAK-D Lite object tracker.

Produces:
  * best.onnx          (opset 12, simplified, 416x416) - source for blob conversion
  * Optionally a .blob via blobconverter if it is installed and the Luxonis cloud
    is reachable (6 SHAVEs, matching the OAK-D Lite).

NOTE on the recommended path:
  DepthAI's YoloDetectionNetwork needs the YOLO head decoded with the right
  metadata (anchors/classes/iou/conf). The most robust way to get a deployable
  blob + JSON is the Luxonis online tool https://tools.luxonis.com (upload
  best.pt, pick OpenVINO + 6 shaves, target OAK-D Lite). The blobconverter path
  below works for a plain ONNX but you must still supply the YOLO metadata JSON
  to YoloDetectionNetwork (see ml/DEPLOY_OAK.md).
"""
import os
from ultralytics import YOLO

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUN = os.path.join(ROOT, "ml", "runs", "duplo_yolov8n_416")
# We deploy last.pt (epoch 13): the tiny 7-image val set made Ultralytics tag the
# noisy epoch-1 model as "best", but on the 231-image test set last.pt is better
# calibrated (stable recall, ~3x fewer false positives, tighter boxes).
import sys
WEIGHTS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RUN, "weights", "last.pt")
IMGSZ = 416


def main():
    model = YOLO(WEIGHTS)
    onnx_path = model.export(format="onnx", imgsz=IMGSZ, opset=12, simplify=True)
    print("ONNX exported:", onnx_path)

    # Best-effort blob conversion (needs internet + blobconverter)
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
