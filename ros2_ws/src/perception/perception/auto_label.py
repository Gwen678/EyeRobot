import cv2
import os
import glob

# PATHS
IMG_DIR = "/home/eyerobot/EyeRobot/lego_dataset/images/train"
LABEL_DIR = "/home/eyerobot/EyeRobot/lego_dataset/labels/train"

os.makedirs(LABEL_DIR, exist_ok=True)

# PARAMS
MIN_AREA = 5000  # noise filter

# Loop over images
for img_path in glob.glob(IMG_DIR + "/*.jpg"):

    img = cv2.imread(img_path)
    if img is None:
        print("❌ skip", img_path)
        continue

    h, w = img.shape[:2]

    # Preprocessing
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    # Segmentation (lego vs background)
    mask = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31,
        5
    )

    # Clean noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=3)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)

    # Find contours
    result = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = result[-2]

    if len(contours) == 0:
        print("⚠️ no object:", img_path)
        continue

    # Keep only the biggest object
    c = max(contours, key=cv2.contourArea)

    area = cv2.contourArea(c)
    if area < MIN_AREA:
        print("⚠️ too small:", img_path)
        continue

    x, y, bw, bh = cv2.boundingRect(c)

    # YOLO format (normalized)
    xc = (x + bw / 2) / w
    yc = (y + bh / 2) / h
    nw = bw / w
    nh = bh / h

    label_line = f"0 {xc:.6f} {yc:.6f} {nw:.6f} {nh:.6f}"

    # Save label
    name = os.path.basename(img_path).replace(".jpg", ".txt")
    out_path = os.path.join(LABEL_DIR, name)

    with open(out_path, "w") as f:
        f.write(label_line + "\n")

    print("✔", img_path, "-> 1 box")
