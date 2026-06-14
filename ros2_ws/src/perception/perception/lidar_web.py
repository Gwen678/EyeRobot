from flask import Flask, jsonify, render_template_string
from rplidar import RPLidar
import threading
import math
import time

app = Flask(__name__)

# Config
PORT = "/dev/ttyUSB0"   # change if needed
MAP_SIZE = 1600
SCALE = 20  # mm to pixels (adjust for your room size)

lidar = RPLidar(PORT)

lock = threading.Lock()
live_points = []

# Safe lidar init
def init_lidar():
    try:
        lidar.stop()
        lidar.disconnect()
    except:
        pass

    time.sleep(1)

    lidar.connect()
    lidar.start_motor()
    time.sleep(2)

# Lidar loop
def lidar_loop():
    global live_points

    while True:
        try:
            init_lidar()

            for scan in lidar.iter_scans():
                points = []

                for (_, angle, distance) in scan:

                    if 50 < distance < 8000:

                        rad = math.radians(angle)

                        x = distance * math.cos(rad)
                        y = distance * math.sin(rad)

                        px = int(x / SCALE + MAP_SIZE / 2)
                        py = int(y / SCALE + MAP_SIZE / 2)

                        if 0 <= px < MAP_SIZE and 0 <= py < MAP_SIZE:
                            points.append((px, py))

                with lock:
                    live_points = points

        except Exception as e:
            print("[LIDAR ERROR]", e)

            try:
                lidar.stop()
                lidar.disconnect()
            except:
                pass

            time.sleep(2)

# Thread start
threading.Thread(target=lidar_loop, daemon=True).start()

# API
@app.route("/data")
def data():
    with lock:
        return jsonify(live_points)

# Web UI
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>LiDAR Web</title>
<style>
body { margin:0; background:#111; text-align:center; }
canvas { background:white; display:block; margin:auto; }
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
    ctx.beginPath();
    ctx.arc(800,800,6,0,Math.PI*2);
    ctx.fill();

    // lidar points
    ctx.fillStyle = "black";
    for(let p of points){
        ctx.fillRect(p[0], p[1], 2, 2);
    }
}

async function loop(){
    try {
        const res = await fetch("/data");
        const data = await res.json();
        draw(data);
    } catch(e) {}

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

# Run
if __name__ == "__main__":
    print("Starting LiDAR Web UI...")
    app.run(host="0.0.0.0", port=5000, debug=False)
