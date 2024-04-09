# SPDX-FileCopyrightText: 2024 Sascha Brawer <sascha@brawer.ch>
# SPDX-License-Identifier: MIT

import cv2
import numpy as np


def classify(png):
    png_array = np.fromstring(png, dtype="uint8")
    gray = cv2.imdecode(png_array, cv2.IMREAD_GRAYSCALE)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    cv2.rectangle(thresh, (0, 0), (255, 255), 255, 1)
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS
    )
    cv2.imwrite("t.png", thresh)

    # Find the leaf contour (leaf = without holes) that is closest
    # to the image center at coordinate (128.0, 128.0).
    # That’s the one we want to classify.
    leaves = [i for i, h in enumerate(hierarchy[0]) if h[2] < 0]
    best, best_distance = None, 1e12
    for leaf in leaves:
        rect = cv2.boundingRect(contours[leaf])
        dx, dy = rect[0] + rect[2] / 2 - 128.0, rect[1] + rect[3] / 2 - 128.0
        distance = dx * dx + dy * dy
        if distance < best_distance:
            best, best_distance = leaf, distance
    if best is None:
        return None
    return classify_contour(thresh, contours, hierarchy, best)


def classify_contour(img, contours, hierarchy, c):
    contour = contours[c]
    white = (count_parents(hierarchy, c) % 2) == 0
    has_holes = hierarchy[0][c][2] >= 0
    parent_index = hierarchy[0][c][3]
    parent = contours[parent_index] if parent_index >= 0 else None
    x, y, r = contour_circle(contour)
    if white and not has_holes and between(r, 7.5, 15.5):
        pw, ph = cv2.minAreaRect(parent)[1]
        if pw > 150 or ph > 150:
            return "white_circle"
    if not white and not has_holes and between(r, 7.5, 9.5):
        return "black_dot"
    return None


# Given an OpenCV contour hierarchy, count how many parents
# the i-th contour has in that hierarchy.
def count_parents(hierarchy, i):
    num_parents = 0
    p = hierarchy[0][i][3]
    while p >= 0:
        num_parents += 1
        p = hierarchy[0][p][3]
    return num_parents


def between(val, lower, upper):
    return val is not None and val >= lower and val <= upper


def contour_circle(contour):
    x, y, w, h = cv2.boundingRect(contour)
    if w < 8 or w > 35 or h < 8 or h > 35:
        return None, None, None
    box = cv2.minAreaRect(contour)
    box_aspect_ratio = float(box[1][0]) / box[1][1]  # width/height
    if box_aspect_ratio < 0.75 or box_aspect_ratio > 1.25:
        return None, None, None
    (x, y), r = cv2.minEnclosingCircle(contour)
    return x, y, r
