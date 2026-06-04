from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="lvis.yaml",
    epochs=1,
    imgsz=640,
    batch=8
)