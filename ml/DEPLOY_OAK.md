# Deploying the Duplo block detector on the OAK-D Lite object tracker

Deploy model: `ml/runs/duplo_yolov8n_416/weights/deploy.pt`  (= `last.pt`, epoch 13)
- Architecture: **YOLOv8n** (smallest, fastest on the Myriad X VPU)
- Input: **416 x 416**, single class `block`
- We prefer **false negatives over false positives** → deploy with a higher
  confidence threshold. On the (deliberately harsh) augmented test set the model
  holds recall ≈ 0.90 from conf 0.2 up to 0.8; **conf ≈ 0.7–0.8** keeps recall high
  while cutting false positives. Push to 0.85+ for near-zero false positives at the
  cost of recall. Tune live against real OAK footage.
- NOT `best.pt`: the 7-image val set made Ultralytics mislabel the noisy epoch-1
  checkpoint as "best"; `last.pt` is better calibrated on the 231-image test set.

Already-built artifacts in `ml/runs/duplo_yolov8n_416/weights/`:
- `deploy.pt`   — PyTorch weights (the chosen checkpoint)
- `deploy.onnx` — ONNX, opset 12, 416×416
- `deploy_openvino_2022.1_6shave.blob` — compiled blob (FP16, 6 SHAVEs, scale=255
  + reversed input channels baked in)

> ⚠️ The bundled `.blob` is compiled straight from the Ultralytics ONNX, whose head
> is the raw YOLOv8 output. DepthAI's `YoloDetectionNetwork` decodes the head
> on-device and expects a matching layout/metadata. For a **guaranteed-correct**
> deploy, regenerate the blob + JSON with the Luxonis tool (step 1) which adapts the
> head and emits the right config. The bundled blob is fine for a `NeuralNetwork`
> node with host-side decoding, or as a starting point.

## 1. Get a `.blob` (+ metadata JSON)

The DepthAI `YoloDetectionNetwork` needs the YOLO head decoded on-device, which
requires a `.blob` plus a small JSON describing the head. Two ways:

### Recommended — Luxonis online tool
1. Go to <https://tools.luxonis.com>.
2. Upload `best.pt` (YOLOv8), set input size **416**, target **OAK-D Lite**
   (6 SHAVEs, OpenVINO FP16).
3. Download the produced `best.blob` **and** `best.json` (the JSON already has the
   correct `nn_config` / `mappings`: anchors are empty for anchor-free YOLOv8,
   `coordinates: 4`, `classes: 1`, `iou_threshold`, `confidence_threshold`).

### Alternative — local export
```bash
ml/.venv/bin/python ml/scripts/export_oak.py     # writes best.onnx (+ tries blob)
```
`export_oak.py` also attempts `blobconverter` (needs internet). If you go this
route you must still hand `YoloDetectionNetwork` the YOLOv8 metadata yourself
(below). The online tool is less error-prone.

## 2. Pipeline: ColorCamera → YoloDetectionNetwork → ObjectTracker

```python
import depthai as dai

NN_BLOB = "deploy_openvino_2022.1_6shave.blob"   # bundled, or your Luxonis-tool blob
LABELS  = ["block"]
CONF    = 0.7              # raise to suppress false positives (see eval sweep)

pipeline = dai.Pipeline()

cam = pipeline.create(dai.node.ColorCamera)
cam.setPreviewSize(416, 416)
cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
cam.setInterleaved(False)
cam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
cam.setFps(30)

detnn = pipeline.create(dai.node.YoloDetectionNetwork)
detnn.setBlobPath(NN_BLOB)
detnn.setConfidenceThreshold(CONF)
detnn.setNumClasses(1)
detnn.setCoordinateSize(4)
detnn.setAnchors([])             # YOLOv8 is anchor-free
detnn.setAnchorMasks({})
detnn.setIouThreshold(0.5)
cam.preview.link(detnn.input)

tracker = pipeline.create(dai.node.ObjectTracker)
tracker.setDetectionLabelsToTrack([0])           # track class 0 = block
tracker.setTrackerType(dai.TrackerType.ZERO_TERM_COLOR_HISTOGRAM)
tracker.setTrackerIdAssignmentPolicy(dai.TrackerIdAssignmentPolicy.SMALLEST_ID)
detnn.passthrough.link(tracker.inputTrackerFrame)
detnn.passthrough.link(tracker.inputDetectionFrame)
detnn.out.link(tracker.inputDetections)

xout = pipeline.create(dai.node.XLinkOut)
xout.setStreamName("tracklets")
tracker.out.link(xout.input)

with dai.Device(pipeline) as device:
    q = device.getOutputQueue("tracklets", 4, False)
    while True:
        for t in q.get().tracklets:
            roi = t.roi.denormalize(416, 416)
            print(t.id, t.status.name,
                  int(roi.x), int(roi.y), int(roi.width), int(roi.height))
```

### Notes
- **Color order / scale:** training images are BGR and the model expects pixels
  scaled to 0–1. The online tool bakes `--scale=255` + `reverse_input_channels`
  into the blob; if you build the blob yourself, match those optimizer params
  (see `export_oak.py`) and set the camera color order accordingly.
- **Tracker type:** `ZERO_TERM_COLOR_HISTOGRAM` is robust for distinctly coloured
  Duplo blocks. If CPU/VPU load matters more than ID stability, use
  `SHORT_TERM_IMAGELESS`.
- **Speed:** yolov8n @ 416 on OAK-D Lite runs comfortably in real time (~30 FPS
  camera-bound). Drop to 320 if you need more headroom (retrain at 320).
- **Fewer false positives:** raise `setConfidenceThreshold`. The eval sweep
  recommends the lowest conf that keeps precision ≥ 0.98 on the test set.
