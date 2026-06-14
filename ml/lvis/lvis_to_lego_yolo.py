import os
import json
from tqdm import tqdm

# ======================
# CONFIG
# ======================
ANN_PATH = "lvis_v1_train.json"   # change si besoin
OUTPUT_DIR = "lego_yolo"

IMG_DIR = os.path.join(OUTPUT_DIR, "images")
LBL_DIR = os.path.join(OUTPUT_DIR, "labels")

os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(LBL_DIR, exist_ok=True)

# ======================
# LOAD LVIS
# ======================
print("Loading LVIS annotations...")

with open(ANN_PATH, "r") as f:
    data = json.load(f)

# ======================
# FIND LEGO CATEGORY IDS
# ======================
lego_cat_ids = []

for cat in data["categories"]:
    if "lego" in cat["name"].lower():
        lego_cat_ids.append(cat["id"])
        print("Found LEGO category:", cat["name"], cat["id"])

if not lego_cat_ids:
    print("No LEGO category found in LVIS!")
    exit()

# MAP IMAGE ID TO FILE INFO
img_map = {img["id"]: img for img in data["images"]}

# ======================
# GROUP ANNOTATIONS
# ======================
img_to_anns = {}

for ann in data["annotations"]:
    if ann["category_id"] in lego_cat_ids:
        img_to_anns.setdefault(ann["image_id"], []).append(ann)

print(f"Images with LEGO: {len(img_to_anns)}")

# ======================
# CONVERT TO YOLO
# ======================
count = 0

for img_id, anns in tqdm(img_to_anns.items()):
    img_info = img_map[img_id]

    width = img_info["width"]
    height = img_info["height"]

    label_file = os.path.join(LBL_DIR, f"{img_id}.txt")

    with open(label_file, "w") as f:
        for ann in anns:

            x, y, w, h = ann["bbox"]

            # YOLO format
            xc = (x + w / 2) / width
            yc = (y + h / 2) / height
            wn = w / width
            hn = h / height

            f.write(f"0 {xc} {yc} {wn} {hn}\n")

    count += 1

print("Done ✔")
print("Images converted:", count)
print("Dataset saved to:", OUTPUT_DIR)