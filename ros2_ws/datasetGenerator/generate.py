import os
import cv2
import numpy as np
import random

IMG_SIZE = 640
N_TRAIN = 2000
N_VAL = 400

OUT_DIR = "dataset"

def random_color():
    return (random.randint(50,255), random.randint(50,255), random.randint(50,255))

def create_background():
    img = np.ones((IMG_SIZE, IMG_SIZE, 3), dtype=np.uint8) * random.randint(200, 255)
    noise = np.random.randint(0, 20, (IMG_SIZE, IMG_SIZE, 3), dtype=np.uint8)
    return cv2.add(img, noise)

def draw_block(img):
    # random block size
    w = random.randint(60, 180)
    h = random.randint(40, 120)

    x = random.randint(0, IMG_SIZE - w)
    y = random.randint(0, IMG_SIZE - h)

    color = random_color()

    # rectangle (lego block)
    cv2.rectangle(img, (x, y), (x + w, y + h), color, -1)

    return x, y, w, h

def convert_yolo(x, y, w, h):
    xc = (x + w / 2) / IMG_SIZE
    yc = (y + h / 2) / IMG_SIZE
    wn = w / IMG_SIZE
    hn = h / IMG_SIZE
    return xc, yc, wn, hn

def generate(split, n):
    img_dir = f"{OUT_DIR}/images/{split}"
    lbl_dir = f"{OUT_DIR}/labels/{split}"

    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(lbl_dir, exist_ok=True)

    for i in range(n):
        img = create_background()

        num_blocks = random.randint(1, 5)
        labels = []

        for _ in range(num_blocks):
            x, y, w, h = draw_block(img)
            labels.append(convert_yolo(x, y, w, h))

        img_path = f"{img_dir}/{i}.jpg"
        lbl_path = f"{lbl_dir}/{i}.txt"

        cv2.imwrite(img_path, img)

        with open(lbl_path, "w") as f:
            for l in labels:
                f.write(f"0 {l[0]} {l[1]} {l[2]} {l[3]}\n")

if __name__ == "__main__":
    generate("train", N_TRAIN)
    generate("val", N_VAL)
    print("Dataset generated ✔")