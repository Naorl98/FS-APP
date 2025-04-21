import numpy as np
import cv2


def detect_visual_titles(gray_img, top_ratio=0.3):
    """
    Improved title detection based on:
    - Dark thick horizontal lines
    - Appearing at the top portion of the image
    - Height threshold to ignore short bold lines
    """
    h, w = gray_img.shape
    limit = int(h * top_ratio)
    min_height = 15
    proj = np.sum(gray_img[0:limit] < 100, axis=1)
    avg_proj = np.mean(proj)
    std_proj = np.std(proj)
    threshold = avg_proj + std_proj * 1.5
    titles = []
    in_block = False
    y1 = 0
    for y, val in enumerate(proj):
        if val > threshold:
            if not in_block:
                y1 = y
                in_block = True
        else:
            if in_block:
                y2 = y
                if (y2 - y1) > min_height:
                    titles.append((y1, y2))
                in_block = False
    return titles


def apply_highlight(image, regions, color=(0, 255, 255), alpha=0.4, margin=5):
    """
    Applies semi-transparent background highlight like a marker behind text.
    """
    overlay = image.copy()
    for y1, y2 in regions:
        y1 = max(0, y1 - margin)
        y2 = min(image.shape[0], y2 + margin)
        cv2.rectangle(overlay, (0, y1), (image.shape[1], y2), color, -1)
    return cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)


def color_name_to_bgr(color_name):
    colors = {
        "Yellow": (0, 255, 255),
        "Green": (0, 255, 0),
        "Blue": (255, 0, 0),
        "Pink": (255, 0, 255),
        "Cyan": (255, 255, 0)
    }
    return colors.get(color_name, (0, 255, 255))  # Default: Yellow
