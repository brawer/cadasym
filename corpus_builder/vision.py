# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 Sascha Brawer

import os

import cv2
import numpy
import pdf2image


DEBUG_CONTOURS = True


def find_symbols(pdf):
    scan_id = os.path.basename(pdf).split(".")[0]
    png_path = pdf + ".png"
    if not os.path.exists(png_path):
        pages = pdf2image.convert_from_path(
            pdf, dpi=600, single_file=True, use_pdftocairo=True, thread_count=4
        )
        img = numpy.array(pages[0])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.imwrite(png_path, img)
    img = cv2.imread(png_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    if DEBUG_CONTOURS:
        cv2.imwrite(f"{scan_id}.thresh.png", thresh)
        contours_img = numpy.full(
            (img.shape[0], img.shape[1], 3), fill_value=255, dtype=numpy.uint8
        )

    (roi_left, roi_top), (roi_right, roi_bottom) = find_roi(thresh)
    if DEBUG_CONTOURS:
        cv2.rectangle(
            contours_img,
            (roi_left, roi_top),
            (roi_right, roi_bottom),
            (0x22, 0x22, 0x22),
            3,
        )
    roi = thresh[roi_top:roi_bottom, roi_left:roi_right]
    contours, hierarchy = cv2.findContours(
        roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS
    )
    symbols = []
    for i, contour in enumerate(contours):
        has_holes = hierarchy[0][i][2] >= 0
        white = (count_parents(hierarchy, i) % 2) == 0
        black = not white
        x, y, radius = contour_circle(contour)
        parent = hierarchy[0][i][3]
        sym, color, thickness = None, (0xAA, 0xAA, 0xAA), 1
        if not has_holes and radius is not None:
            x = int(x + roi_left + 0.5)
            y = int(y + roi_top + 0.5)
            if black and 7 <= radius <= 30:
                sym, color, thickness = "D", (0xFF, 0x22, 0x22), -1
            elif white and 7 <= radius <= 30:
                sym, color, thickness = "E", (0x22, 0x66, 0xFF), -1
        if sym is not None:
            symbols.append((sym, x, y))
        if DEBUG_CONTOURS:
            cv2.drawContours(
                contours_img,
                [contour],
                0,
                color=color,
                thickness=thickness,
                lineType=cv2.LINE_AA,
                offset=(roi_left, roi_top),
            )
    symbols.sort(key=lambda s: (s[0], s[1] * s[1] + s[2] * s[2]))
    result = []
    for sym, x, y in symbols:
        sym_id = f"{scan_id}_{x}_{y}"
        sym_img = crop(img, x, y, 256)
        if sym_img.shape[0] != 256 or sym_img.shape[1] != 256:
            continue
        _, png = cv2.imencode(".png", sym_img)
        result.append((sym_id, png.tobytes()))
        # cv2.imwrite(f'symbol_{sym_id}.png', sym_img)
    if DEBUG_CONTOURS:
        contours_img = cv2.cvtColor(contours_img, cv2.COLOR_BGR2RGB)
        cv2.imwrite(f"{scan_id}.contours.png", contours_img)
    return result


def find_roi(thresh):
    """Find the Region of Interest in a scanned cadastre plan."""
    height, width = thresh.shape[:2]
    # Sometimes the first page is actually two A4 pages scanned to
    # a single A3 image. In that case, we're only interested in the
    # left half of the A3 sheet because that is where the plan is.
    if width > 6000:
        width = int(width / 2)

    top = 700
    for y in range(700):
        if numpy.count_nonzero(thresh[y, :width]) > width - 5:
            top = y
    bottom = height - 1100
    for y in range(height - 1100, height):
        if numpy.count_nonzero(thresh[y, :1800]) == 1800:
            bottom = y
            break

    limit = bottom - top - 5
    num_white_pixels = numpy.count_nonzero(thresh[top:bottom, 0:width], axis=0)
    left = 0
    for x in range(0, 400):
        if num_white_pixels[x] < limit:
            left = x
            break
    right = width
    for x in range(width - 1, width - 400, -1):
        if num_white_pixels[x] < limit:
            right = x
            break
    return (left, top), (right, bottom)


# Given an OpenCV contour hierarchy, count how many parents
# the i-th contour has in that hierarchy.
def count_parents(hierarchy, i):
    num_parents = 0
    p = hierarchy[0][i][3]
    while p >= 0:
        num_parents += 1
        p = hierarchy[0][p][3]
    return num_parents


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


def crop(img, x, y, size):
    x0, x1 = int(x - size / 2), int(x + size / 2)
    y0, y1 = int(y - size / 2), int(y + size / 2)
    return img[y0:y1, x0:x1]
