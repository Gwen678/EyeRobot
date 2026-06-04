from flask import Flask, render_template_string, jsonify
from rplidar import RPLidar
import threading
import math

app = Flask(__name__)

# -----------------------
# CONFIG
# -----------------------
PORT = "/dev/ttyUSB1"
MAP_SIZE = 1600
SCALE = 20  # mm per pixel approx

lidar = RPLidar(PORT)

live_points = []
lock = threading.Lock()

# -----------------------
# LiDAR THREAD
# -----------------------
def lidar_loop():
    global live_points

    lidar.connect()
    lidar.start_motor()

    for scan in lidar.iter_scans():
        points = []

        for (_, angle, distance) in scan:
            if 50 < distance < 8000:

                rad = math.radians(angle)
                x = distance * math.cos(rad)
                y = distance * math.sin(rad)

                # convert to map coords (centered)
                px = int(x / SCALE + MAP_SIZE/2)
                py = int(y / SCALE + MAP_SIZE/2)

                points.append((px, py))

        with lock:
            live_points = points

threading.Thread(target=lidar_loop, daemon=True).start()

# -----------------------
# API
# -----------------------
@app.route("/data")
def data():
    with lock:
        return jsonify(live_points)

# -----------------------
# UI
# -----------------------
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>LiDAR Map</title>
<style>
body { margin:0; background:#111; text-align:center; }
canvas { background:white; }
</style>
</head>

<body>

<canvas id="c" width="1600" height="1600"></canvas>

<script>
const canvas = document.getElementById("c");
const ctx = canvas.getContext("2d");

function draw(points){
    ctx.clearRect(0,0,1600,1600);

    // robot center
    ctx.fillStyle = "red";
    ctx.fillRect(800,800,6,6);

    // lidar points
    ctx.fillStyle = "black";
    points.forEach(p => {
        ctx.fillRect(p[0], p[1], 2, 2);
    });
}

async function loop(){
    const res = await fetch("/data");
    const data = await res.json();
    draw(data);
    requestAnimationFrame(loop);
}

loop();
</script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

# -----------------------
# RUN
# -----------------------
app.run(host="0.0.0.0", port=5000)
