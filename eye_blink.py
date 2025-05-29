# eye_blink.py

# このスクリプトは、MediaPipeのFaceMeshを使って目の瞬きを検出し、目のアスペクト比（EAR）を計算します。
# 実行すると、カメラ映像上に目の状態（開いているか閉じているか）を表示します。
# ウィンドウを閉じるには、ESCキーを押してください。

# 必要なライブラリをインポート
# 注意: このコードを実行するには、OpenCVとMediaPipeのライブラリが必要です。
# インストールは以下のコマンドで行えます。
# pip install opencv-python mediapipe numpy

# OpenCV,MediaPipe,NumPyをインポート
import cv2
import mediapipe as mp
import numpy as np

# MediaPipeのFaceMeshを初期化
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)
drawing_spec = mp.solutions.drawing_utils.DrawingSpec(thickness=1, circle_radius=1)

# 左目のランドマークインデックス（MediaPipeの仕様）
LEFT_EYE = [33, 160, 158, 133, 153, 144]  # [p1, p2, p3, p4, p5, p6]

# EAR (Eye Aspect Ratio) を計算する関数
def calculate_ear(landmarks, eye_indices, image_width, image_height):
    coords = []
    for idx in eye_indices:
        lm = landmarks[idx]
        coords.append(np.array([lm.x * image_width, lm.y * image_height]))

    # 各点の座標を取り出す
    p1, p2, p3, p4, p5, p6 = coords

    # 縦と横の距離を計算
    vertical = np.linalg.norm(p2 - p6) + np.linalg.norm(p3 - p5)
    horizontal = 2.0 * np.linalg.norm(p1 - p4)

    # EARを返す
    ear = vertical / horizontal
    return ear

# カメラ映像の取得開始
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 映像を左右反転して、RGBに変換
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 顔検出（MediaPipe）
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            h, w, _ = frame.shape

            # 左目のEARを計算
            ear = calculate_ear(face_landmarks.landmark, LEFT_EYE, w, h)

            # EARのしきい値：小さいほど目が閉じている
            threshold = 0.20
            status = "Closed" if ear < threshold else "Open"

            # 結果を画面に描画
            cv2.putText(frame, f"Eye: {status} ({ear:.2f})", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if status == "Open" else (0, 0, 255), 2)
            
            

    # 映像を表示
    cv2.imshow("Eye Blink Detection - press ESC to exit", frame)

    # ESCキーで終了
    if cv2.waitKey(1) & 0xFF == 27:
        break
    # ウィンドウが閉じられた場合も終了
    if cv2.getWindowProperty("Eye Blink Detection - press ESC to exit", cv2.WND_PROP_VISIBLE) < 1:
        break

# カメラ解放＆ウィンドウ閉じる
cap.release()
cv2.destroyAllWindows()
