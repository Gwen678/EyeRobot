import cv2
import glob
import os

IMG_DIR = "/home/eyerobot/EyeRobot/lego_dataset/images/train"
LBL_DIR = "/home/eyerobot/EyeRobot/lego_dataset/labels/train"

for img_path in glob.glob(IMG_DIR + "/*.jpg"):

    img = cv2.imread(img_path)
    h, w = img.shape[:2]

    label_path = img_path.replace("images/train", "labels/train").replace(".jpg", ".txt")

    if not os.path.exists(label_path):
        continue

    with open(label_path) as f:
        line = f.readline().strip().split()

    if len(line) != 5:
        continue

    _, xc, yc, bw, bh = map(float, line)

    x1 = int((xc - bw/2) * w)
    y1 = int((yc - bh/2) * h)
    x2 = int((xc + bw/2) * w)
    y2 = int((yc + bh/2) * h)

    cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), 2)

    cv2.imshow("check", img)
    cv2.waitKey(0)

cv2.destroyAllWindows()
