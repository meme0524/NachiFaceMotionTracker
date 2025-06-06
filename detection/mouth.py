# detection/mouth.py

import numpy as np
# MediaPipeの口の6点インデックス
MOUTH_INDICES = [78, 81, 13, 311, 308, 402]

def calculate_mar(landmarks, image_width, image_height):
    """
    MAR: Mouth Aspect Ratio（口の開閉度）
    計算式: (上下内側距離 + 上下外側距離) / 左右端の距離
    """
    def to_np(idx):
        pt = landmarks[idx]
        return np.array([pt.x * image_width, pt.y * image_height])

    left = to_np(MOUTH_INDICES[0])
    top_in = to_np(MOUTH_INDICES[1])
    bottom_in = to_np(MOUTH_INDICES[2])
    right = to_np(MOUTH_INDICES[3])
    top_out = to_np(MOUTH_INDICES[4])
    bottom_out = to_np(MOUTH_INDICES[5])

    vertical = np.linalg.norm(top_in - bottom_in) + np.linalg.norm(top_out - bottom_out)
    horizontal = 2.0 * np.linalg.norm(left - right)

    # 左右端の距離が0の場合は計算できないので0を返す
    if horizontal == 0:
        return 0.0

    mar = vertical / horizontal
    return mar
