
from flask import Flask, Response
import depthai as dai
import cv2

app = Flask(__name__)

# DepthAI pipeline
pipeline = dai.Pipeline()


cam = pipeline.create(dai.node.Camera)
cam.build()

video_out = cam.requestOutput((640, 640), dai.ImgFrame.Type.BGR888p)
queue = video_out.createOutputQueue()

# Device
with dai.Device() as device:
    device.start(pipeline)
    print("DepthAI + Flask ready")

# Frame generator
def generate_frames():
    while True:
        frame = queue.get().getCvFrame()
        cv2.putText(frame, "OAK STREAM LIVE", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# Routes
@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return """
    <html>
    <head><title>OAK Stream</title></head>
    <body style="background:black; text-align:center;">
        <h2 style="color:white;">🌐 OAK DepthAI Live Stream</h2>
        <img src="/video" width="900"/>
    </body>
    </html>
    """

# Run server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

