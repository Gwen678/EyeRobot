#!/usr/bin/env python3
"""
Offline data augmentation for the Duplo-block detector.
Each technique is applied separately; flip_ud and flip_lr produce 1 variant each while all others produce n variants. Boxes are warped with their 4 corners and tiny or out-of-frame boxes are dropped.
"""
import cv2
import numpy as np

# box helpers

def _boxes_to_corners(boxes, w, h):
    """boxes: list of (cls,xc,yc,bw,bh) norm -> (classes, Nx4x2 pixel corners)."""
    classes, corners = [], []
    for cls, xc, yc, bw, bh in boxes:
        x0 = (xc - bw / 2) * w; y0 = (yc - bh / 2) * h
        x1 = (xc + bw / 2) * w; y1 = (yc + bh / 2) * h
        corners.append([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
        classes.append(cls)
    return classes, np.array(corners, dtype=np.float32).reshape(-1, 4, 2)


def _corners_to_boxes(classes, corners, w, h, min_frac=0.01, min_visible=0.15):
    """Axis-aligned bbox of (possibly warped) corners, clipped to frame.
    Drop boxes that are mostly outside or tiny."""
    out = []
    for cls, quad in zip(classes, corners):
        xs = quad[:, 0]; ys = quad[:, 1]
        x0, x1 = xs.min(), xs.max()
        y0, y1 = ys.min(), ys.max()
        full_area = max(1e-6, (x1 - x0) * (y1 - y0))
        cx0, cy0 = max(0, x0), max(0, y0)
        cx1, cy1 = min(w, x1), min(h, y1)
        if cx1 <= cx0 or cy1 <= cy0:
            continue
        vis_area = (cx1 - cx0) * (cy1 - cy0)
        if vis_area / full_area < min_visible:
            continue
        bw = (cx1 - cx0) / w; bh = (cy1 - cy0) / h
        if bw < min_frac or bh < min_frac:
            continue
        xc = (cx0 + cx1) / 2 / w; yc = (cy0 + cy1) / 2 / h
        out.append((cls, xc, yc, bw, bh))
    return out


def _warp_boxes(boxes, M, w, h, perspective=False):
    if not boxes:
        return []
    classes, corners = _boxes_to_corners(boxes, w, h)
    pts = corners.reshape(-1, 2)
    if perspective:
        pts_h = np.concatenate([pts, np.ones((pts.shape[0], 1), np.float32)], axis=1)
        warped = (M @ pts_h.T).T
        warped = warped[:, :2] / warped[:, 2:3]
    else:
        pts_h = np.concatenate([pts, np.ones((pts.shape[0], 1), np.float32)], axis=1)
        warped = (M @ pts_h.T).T
    warped = warped.reshape(-1, 4, 2)
    return _corners_to_boxes(classes, warped, w, h)


# photometric techniques (boxes unchanged)

def aug_hue(img, boxes, rng):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.int16)
    shift = rng.randint(8, 30) * rng.choice([-1, 1])
    hsv[:, :, 0] = (hsv[:, :, 0] + shift) % 180
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    return out, boxes


def aug_saturation(img, boxes, rng):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    f = rng.uniform(0.45, 1.6)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * f, 0, 255)
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    return out, boxes


def aug_brightness(img, boxes, rng):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    f = rng.uniform(0.55, 1.45)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * f, 0, 255)
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    return out, boxes


_BGR_PERMS = [(0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]  # 5 non-identity

def make_bgr_swap(idx):
    perm = _BGR_PERMS[idx % len(_BGR_PERMS)]
    def f(img, boxes, rng):
        return img[:, :, perm], boxes
    return f


# geometric techniques (boxes transformed)

_BORDER = cv2.BORDER_REFLECT_101

def aug_rotation(img, boxes, rng):
    h, w = img.shape[:2]
    ang = rng.uniform(-30, 30)
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, 1.0)
    out = cv2.warpAffine(img, M, (w, h), borderMode=_BORDER)
    return out, _warp_boxes(boxes, M, w, h)


def aug_translation(img, boxes, rng):
    h, w = img.shape[:2]
    tx = rng.uniform(-0.12, 0.12) * w
    ty = rng.uniform(-0.12, 0.12) * h
    M = np.array([[1, 0, tx], [0, 1, ty]], np.float32)
    out = cv2.warpAffine(img, M, (w, h), borderMode=_BORDER)
    return out, _warp_boxes(boxes, M, w, h)


def aug_scale(img, boxes, rng):
    h, w = img.shape[:2]
    s = rng.uniform(0.6, 1.45)
    M = cv2.getRotationMatrix2D((w / 2, h / 2), 0, s)
    out = cv2.warpAffine(img, M, (w, h), borderMode=_BORDER)
    return out, _warp_boxes(boxes, M, w, h)


def aug_shear(img, boxes, rng):
    h, w = img.shape[:2]
    sh = np.tan(np.deg2rad(rng.uniform(-15, 15)))
    sv = np.tan(np.deg2rad(rng.uniform(-15, 15)))
    M = np.array([[1, sh, -sh * w / 2], [sv, 1, -sv * h / 2]], np.float32)
    out = cv2.warpAffine(img, M, (w, h), borderMode=_BORDER)
    return out, _warp_boxes(boxes, M, w, h)


def aug_perspective(img, boxes, rng):
    h, w = img.shape[:2]
    d = rng.uniform(0.04, 0.10)  # max corner displacement as fraction
    src = np.array([[0, 0], [w, 0], [w, h], [0, h]], np.float32)
    off = (rng.uniform(-d, d, size=(4, 2)) * [w, h]).astype(np.float32)
    dst = src + off
    M = cv2.getPerspectiveTransform(src, dst)
    out = cv2.warpPerspective(img, M, (w, h), borderMode=_BORDER)
    return out, _warp_boxes(boxes, M, w, h, perspective=True)


def aug_flip_ud(img, boxes, rng):
    out = cv2.flip(img, 0)
    nb = [(c, xc, 1 - yc, bw, bh) for (c, xc, yc, bw, bh) in boxes]
    return out, nb


def aug_flip_lr(img, boxes, rng):
    out = cv2.flip(img, 1)
    nb = [(c, 1 - xc, yc, bw, bh) for (c, xc, yc, bw, bh) in boxes]
    return out, nb


# driver

def build_techniques(counts):
    """Return list of (suffix, fn). counts: dict technique-> n variants."""
    techs = []
    cont = {
        "hue": aug_hue, "sat": aug_saturation, "bri": aug_brightness,
        "rot": aug_rotation, "trans": aug_translation, "scale": aug_scale,
        "shear": aug_shear, "persp": aug_perspective,
    }
    for key, fn in cont.items():
        for i in range(counts.get(key, 0)):
            techs.append((f"{key}{i}", fn))
    # bgr swap: distinct permutations
    for i in range(counts.get("bgr", 0)):
        techs.append((f"bgr{i}", make_bgr_swap(i)))
    # deterministic flips: 1 each regardless
    if counts.get("flipud", 0):
        techs.append(("flipud", aug_flip_ud))
    if counts.get("fliplr", 0):
        techs.append(("fliplr", aug_flip_lr))
    return techs


def generate(img, boxes, counts, rng):
    """Yield (suffix, out_img, out_boxes) for every variant.
    Skips block-image variants that lose all their boxes."""
    has_box = len(boxes) > 0
    results = []
    for suffix, fn in build_techniques(counts):
        out_img, out_boxes = fn(img, list(boxes), rng)
        if has_box and len(out_boxes) == 0:
            continue  # don't turn a block image into a false negative
        results.append((suffix, out_img, out_boxes))
    return results
