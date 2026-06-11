"""Launch-time generation of the onboard-YOLO configs (shared by
lego_test.launch.py and eyerobot.launch.py).

Two files are derived from the yolo_conf / yolo_input launch arguments and
written under /tmp at every launch, so the blob path always tracks the
perception package's install space and the RGB preview size always matches
the blob input (the driver hard-aborts on any mismatch):

  /tmp/eyerobot_yolo_nn.json      YoloDetectionNetwork config (decode
                                  metadata + absolute blob path)
  /tmp/eyerobot_camera_yolo.yaml  depthai_camera_yolo.yaml with the
                                  i_preview_* values rewritten to yolo_input
"""
import json
import os

import yaml
from ament_index_python.packages import get_package_share_directory

NN_CONFIG_PATH = "/tmp/eyerobot_yolo_nn.json"
CAMERA_YAML_PATH = "/tmp/eyerobot_camera_yolo.yaml"

# Tuned on the bench 2026-06-11 (current best.blob, 640x640 input). Edit
# HERE — these are deliberately not launch flags.
YOLO_CONF = 0.5
YOLO_INPUT = 640


def write_yolo_configs(conf=YOLO_CONF, size=YOLO_INPUT):
    """Write both files; returns CAMERA_YAML_PATH (the camera params_file).

    conf: YOLO confidence threshold (float).
    size: blob input size in pixels (640 for the current best.blob,
          416 for the compiled duplo_yolov8n_416 model).
    """
    blob = os.path.join(get_package_share_directory('perception'), 'models', 'best.blob')
    if not os.path.isfile(blob):
        raise RuntimeError(
            f"YOLO blob not found at {blob} — build the perception package "
            "(colcon build --packages-select perception)")

    # Decode profile: one set of values for any modern (anchor-free) YOLO
    # head; iou 0.5 = standard NMS, suppresses duplicate boxes on tight
    # block clusters. Confidence is tuned on OUR blocks/lighting via the
    # yolo_conf launch argument.
    config = {
        "model": {"zoo": "path", "model_name": blob},
        "nn_config": {
            "output_format": "detection",
            "NN_family": "YOLO",
            "input_size": f"{int(size)}x{int(size)}",
            "confidence_threshold": float(conf),
            "NN_specific_metadata": {
                "classes": 1,
                "coordinates": 4,
                "anchors": [],
                "anchor_masks": {},
                "iou_threshold": 0.5,
                "confidence_threshold": float(conf),
            },
        },
        "mappings": {"labels": ["block"]},
    }
    with open(NN_CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

    base = os.path.join(get_package_share_directory('manual_controller'),
                        'config', 'depthai_camera_yolo.yaml')
    with open(base) as f:
        params = yaml.safe_load(f)
    rgb = params['/**']['ros__parameters']['rgb']
    rgb['i_preview_size'] = int(size)
    rgb['i_preview_width'] = int(size)
    rgb['i_preview_height'] = int(size)
    with open(CAMERA_YAML_PATH, 'w') as f:
        yaml.safe_dump(params, f)
    return CAMERA_YAML_PATH
