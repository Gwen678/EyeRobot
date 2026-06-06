#!/usr/bin/env python3
"""
Build the YOLO dataset:

  1. Split the 64 block + 7 ground images into train / val / test BEFORE any
     augmentation (so augmented copies of one photo never leak across splits).
  2. Downscale every image to a max side of 768 px (deploy size is 416; this keeps
     disk + training IO small while leaving headroom).
  3. Augment train and test with the offline augmenter (val stays clean originals
     for honest validation).

Layout produced under ml/dataset/:
  images/{train,val,test}/...   labels/{train,val,test}/...   data.yaml

Single class: 0 = block. Ground images carry empty label files (negatives) so the
model learns to NOT fire on bare floor -> fewer false positives.
"""
import os
import glob
import random
import shutil
import cv2
import numpy as np

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from augment import generate

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IMG_DIR = os.path.join(ROOT, "images")
LBL_DIR = os.path.join(ROOT, "ml", "work", "labels")
DS = os.path.join(ROOT, "ml", "dataset")

SEED = 1234
RESIZE_MAX = 768
JPEG_Q = 90

# split sizes
BLOCK_TEST, BLOCK_VAL = 10, 12     # rest -> train
GROUND_TEST, GROUND_VAL = 1, 2

COUNTS_TRAIN = dict(hue=5, sat=5, bri=5, rot=5, trans=5, scale=5, shear=5,
                    persp=5, bgr=5, flipud=1, fliplr=1)
COUNTS_TEST = dict(hue=2, sat=2, bri=2, rot=2, trans=2, scale=2, shear=2,
                   persp=2, bgr=2, flipud=1, fliplr=1)
# augment val too so the early-stopping metric is stable (val originals are still
# disjoint from train originals -> no leakage).
COUNTS_VAL = dict(hue=2, sat=2, bri=2, rot=2, trans=2, scale=2, shear=2,
                  persp=2, bgr=2, flipud=1, fliplr=1)


def read_label(name):
    p = os.path.join(LBL_DIR, name + ".txt")
    boxes = []
    if os.path.exists(p):
        for line in open(p):
            parts = line.split()
            if len(parts) == 5:
                c, xc, yc, w, h = parts
                boxes.append((int(c), float(xc), float(yc), float(w), float(h)))
    return boxes


def downscale(img):
    h, w = img.shape[:2]
    m = max(h, w)
    if m <= RESIZE_MAX:
        return img
    s = RESIZE_MAX / m
    return cv2.resize(img, (int(round(w * s)), int(round(h * s))), interpolation=cv2.INTER_AREA)


def write_sample(split, name, img, boxes):
    ip = os.path.join(DS, "images", split, name + ".jpg")
    lp = os.path.join(DS, "labels", split, name + ".txt")
    cv2.imwrite(ip, img, [cv2.IMWRITE_JPEG_QUALITY, JPEG_Q])
    with open(lp, "w") as f:
        for c, xc, yc, w, h in boxes:
            f.write(f"{c} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}\n")


def main():
    rng = random.Random(SEED)
    nprng = np.random.RandomState(SEED)

    paths = sorted(glob.glob(os.path.join(IMG_DIR, "*.jpg")))
    blocks = [os.path.splitext(os.path.basename(p))[0] for p in paths
              if not os.path.basename(p).lower().startswith("ground")]
    grounds = [os.path.splitext(os.path.basename(p))[0] for p in paths
               if os.path.basename(p).lower().startswith("ground")]
    rng.shuffle(blocks)
    rng.shuffle(grounds)

    split = {"train": [], "val": [], "test": []}
    split["test"] = blocks[:BLOCK_TEST] + grounds[:GROUND_TEST]
    split["val"] = blocks[BLOCK_TEST:BLOCK_TEST + BLOCK_VAL] + grounds[GROUND_TEST:GROUND_TEST + GROUND_VAL]
    split["train"] = blocks[BLOCK_TEST + BLOCK_VAL:] + grounds[GROUND_TEST + GROUND_VAL:]

    # fresh dirs
    if os.path.exists(DS):
        shutil.rmtree(DS)
    for s in ("train", "val", "test"):
        os.makedirs(os.path.join(DS, "images", s))
        os.makedirs(os.path.join(DS, "labels", s))

    stats = {}
    for s in ("train", "val", "test"):
        counts = {"train": COUNTS_TRAIN, "test": COUNTS_TEST, "val": COUNTS_VAL}[s]
        n_orig = n_aug = 0
        for name in split[s]:
            img = downscale(cv2.imread(os.path.join(IMG_DIR, name + ".jpg")))
            boxes = read_label(name)
            write_sample(s, name, img, boxes)
            n_orig += 1
            if counts:
                for suffix, aimg, aboxes in generate(img, boxes, counts, nprng):
                    write_sample(s, f"{name}__{suffix}", aimg, aboxes)
                    n_aug += 1
        stats[s] = (n_orig, n_aug)

    # data.yaml
    with open(os.path.join(DS, "data.yaml"), "w") as f:
        f.write(
            f"path: {DS}\n"
            "train: images/train\n"
            "val: images/val\n"
            "test: images/test\n\n"
            "names:\n  0: block\n"
        )

    print("Split (originals):")
    for s in ("train", "val", "test"):
        o, a = stats[s]
        print(f"  {s:5s}: {o:3d} originals + {a:5d} augmented = {o + a}")
    print(f"\nBlocks: train {len(blocks) - BLOCK_TEST - BLOCK_VAL}, "
          f"val {BLOCK_VAL}, test {BLOCK_TEST}")
    print(f"Ground negatives: train {len(grounds) - GROUND_TEST - GROUND_VAL}, "
          f"val {GROUND_VAL}, test {GROUND_TEST}")
    print(f"data.yaml -> {os.path.join(DS, 'data.yaml')}")


if __name__ == "__main__":
    main()
