"""Launch-time generation of YOLO configs (shared by lego_test.launch.py and eyerobot.launch.py).

Writes /tmp/eyerobot_yolo_nn.json and /tmp/eyerobot_camera_yolo.yaml from the
yolo_conf/yolo_input arguments so the blob path and preview size always match.
"""
import json
import os

import yaml
from ament_index_python.packages import get_package_share_directory

NN_CONFIG_PATH = "/tmp/eyerobot_yolo_nn.json"
CAMERA_YAML_PATH = "/tmp/eyerobot_camera_yolo.yaml"

# Tuned on the bench 2026-06-11 (current best.blob, 640x640 input).
# Edit here - these are not launch flags.
YOLO_CONF = 0.5
YOLO_INPUT = 640


def write_yolo_configs(conf=YOLO_CONF, size=YOLO_INPUT):
    """Write both config files and return CAMERA_YAML_PATH.

    conf: YOLO confidence threshold. size: blob input size in pixels.
    """
    blob = os.path.join(get_package_share_directory('perception'), 'models', 'best.blob')
    if not os.path.isfile(blob):
        raise RuntimeError(
            f"YOLO blob not found at {blob} — build the perception package "
            "(colcon build --packages-select perception)")

    # Decode profile for anchor-free YOLO: iou 0.5 = standard NMS.
    # Confidence is tuned for the blocks/lighting via the yolo_conf argument.
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
