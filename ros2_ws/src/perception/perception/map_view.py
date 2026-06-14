import numpy as np
import math
import random
from rplidar import RPLidar
import time

# Config
PORT = "/dev/ttyUSB0"

MAP_SIZE = 1600
SCALE = 0.005  # 5mm per pixel
N_PARTICLES = 150

lidar = RPLidar(PORT)

# Map (binary: obstacle=1)
import cv2
map_img = cv2.imread("/home/eyerobot/EyeRobot/ros2_ws/maps/map.png", 0)
_, map_bin = cv2.threshold(map_img, 100, 1, cv2.THRESH_BINARY_INV)

# Particles
particles = []

def init_particles():
    global particles
    particles = []

    for _ in range(N_PARTICLES):
        particles.append([
            random.uniform(-2, 2),   # x (m)
            random.uniform(-2, 2),   # y
            random.uniform(0, 360)   # theta
        ])

init_particles()

# Scan
def get_scan():
    lidar.connect()
    lidar.start_motor()
    time.sleep(2)

    for scan in lidar.iter_scans():
        return [(a, d) for (_, a, d) in scan if d > 50]

# Score particle
def score_particle(p, scan):
    x, y, theta = p
    score = 0

    for angle, dist in scan:

        a = math.radians(angle + theta)

        wx = x + dist * math.cos(a)
        wy = y + dist * math.sin(a)

        mx = int(wx / SCALE + MAP_SIZE/2)
        my = int(wy / SCALE + MAP_SIZE/2)

        if 0 <= mx < MAP_SIZE and 0 <= my < MAP_SIZE:

            if map_bin[my, mx] == 1:
                score += 1
            else:
                score -= 1

    return score

# Resample
def resample(particles, weights):
    new_particles = []

    weights = np.array(weights)
    weights = np.maximum(weights, 1e-6)
    weights /= np.sum(weights)

    idx = np.random.choice(len(particles), N_PARTICLES, p=weights)

    for i in idx:
        x, y, t = particles[i]

        # noise
        x += random.uniform(-0.05, 0.05)
        y += random.uniform(-0.05, 0.05)
        t += random.uniform(-2, 2)

        new_particles.append([x, y, t])

    return new_particles

# Localization loop
def run():

    global particles

    while True:

        scan = get_scan()

        weights = []

        for p in particles:
            w = score_particle(p, scan)
            weights.append(w)

        particles = resample(particles, weights)

        best = particles[np.argmax(weights)]

        print("BEST:", best)

run()
