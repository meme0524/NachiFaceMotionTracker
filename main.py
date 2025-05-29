# main.py

import cv2
import mediapipe as mp
import numpy as np

from detection.eye import calculate_ear, LEFT_EYE_INDICES  # 分離したeye.pyを使う

# MediaPipeの初期化
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)

# カメラ起動
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("カメラから映像が取得できませんでした")
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            h, w, _ = frame.shape
            ear = calculate_ear(face_landmarks.landmark, LEFT_EYE_INDICES, w, h)
            eye_status = "Closed" if ear < 0.2 else "Open"

            cv2.putText(frame, f"Eye: {eye_status} ({ear:.2f})", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0) if eye_status == "Open" else (0, 0, 255), 2)

    # 案内表示
    cv2.putText(frame, "Press ESC to exit", (30, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

    # ウィンドウ名も設定
    window_name = "Face Motion Tracker - Press ESC to exit"
    cv2.imshow(window_name, frame)

    # 終了条件：ESCキーまたはウィンドウ×
    if cv2.waitKey(1) & 0xFF == 27:
        break
    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()
