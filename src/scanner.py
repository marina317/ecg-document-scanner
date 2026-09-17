import cv2 as cv
import numpy as np


def load_image(image_path):
    img = cv.imread(image_path)
    return img

def process_image(img):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    binary = cv.adaptiveThreshold(gray, 255,  # ✅ Pass gray not img
                                  cv.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv.THRESH_BINARY, 51, 10)
    return binary

def find_contours(binary):
    contours, _ = cv.findContours(binary, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    h, w = binary.shape  # ✅ Use binary.shape, not gray.shape
    total_area = h * w
    best_candidate = None

    # 1. Sort all contours from largest area to smallest  ✅ Indented!
    sorted_contours = sorted(contours, key=cv.contourArea, reverse=True)

    # 2. Inspect the top 20 candidates
    for i, c in enumerate(sorted_contours[:20]):
        area = cv.contourArea(c)

        if area < 0.15 * total_area:
            continue

        peri = cv.arcLength(c, True)
        approx = cv.approxPolyDP(c, 0.02 * peri, True)

        # ✅ Try convex hull as fallback
        if not (len(approx) == 4 and cv.isContourConvex(approx)):
            hull = cv.convexHull(c)
            peri = cv.arcLength(hull, True)
            approx = cv.approxPolyDP(hull, 0.02 * peri, True)

        if len(approx) == 4 and cv.isContourConvex(approx):
            best_candidate = approx
            break

    return best_candidate

def warp_document(img, corners):
    # Step 1: Reshape from (4, 1, 2) to (4, 2) for easier math
    pts = corners.reshape(4, 2).astype("float32")

    # Step 2: Order points consistently: TL, TR, BR, BL
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # TL: smallest x+y
    rect[2] = pts[np.argmax(s)]   # BR: largest x+y
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)] # TR: smallest y-x
    rect[3] = pts[np.argmax(diff)] # BL: largest y-x

    (tl, tr, br, bl) = rect

    # Step 3: Calculate output width (longest horizontal edge)
    width = max(
        int(np.linalg.norm(br - bl)),  # bottom edge length
        int(np.linalg.norm(tr - tl))   # top edge length
    )

    # Step 4: Calculate output height (longest vertical edge)
    height = max(
        int(np.linalg.norm(tr - br)),  # right edge length
        int(np.linalg.norm(tl - bl))   # left edge length
    )

    # Step 5: Define the destination flat rectangle (top-down view)
    dst = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")

    # Step 6: Compute 3x3 perspective transform matrix and warp
    M = cv.getPerspectiveTransform(rect, dst)
    warped = cv.warpPerspective(img, M, (width, height))

    return warped
