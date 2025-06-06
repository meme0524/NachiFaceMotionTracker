# detection/eye.py

import numpy as np

# MediaPipeの左目・右目の6点インデックス
LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]  # [p1, p2, p3, p4, p5, p6]
RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]

def calculate_ear(landmarks, eye_indices, image_width, image_height):
    coords = [
        np.array([landmarks[i].x * image_width, landmarks[i].y * image_height])
        for i in eye_indices
    ]
    p1, p2, p3, p4, p5, p6 = coords
    vertical = np.linalg.norm(p2 - p6) + np.linalg.norm(p3 - p5)
    horizontal = 2.0 * np.linalg.norm(p1 - p4)

    # 横方向の距離が0の場合は計算できないので0を返す
    if horizontal == 0:
        return 0.0

    ear = vertical / horizontal
    return ear
