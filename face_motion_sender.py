import cv2
import mediapipe as mp
import numpy as np
import socket
import json

from detection.eye import calculate_ear, LEFT_EYE_INDICES, RIGHT_EYE_INDICES
from detection.mouth import calculate_mar

# UDP設定
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# MediaPipe初期化
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)

# カメラ起動
cap = cv2.VideoCapture(0)

# --- キャリブレーション用変数 ---
calibrated       = False
sampling_state   = "open"        # "open" → "close" → "done"
frame_counter    = 0
SAMPLE_FRAMES    = 200             # 各状態で何フレームサンプリングするか
ear_open_list    = []
ear_close_list   = []
thr_left, thr_right = 0.0, 0.0

# 顔の角度取得
def get_face_angle(landmarks, w, h):
    left_eye  = landmarks[33]
    right_eye = landmarks[263]
    nose_tip  = landmarks[1]

    l = np.array([left_eye.x * w,  left_eye.y * h])
    r = np.array([right_eye.x * w, right_eye.y * h])
    n = np.array([nose_tip.x * w,  nose_tip.y * h])

    eye_line    = r - l
    nose_vector = n - (l + r) / 2

    yaw_rad   = np.arctan2(nose_vector[0], eye_line[0])
    yaw_deg   = np.degrees(yaw_rad)

    pitch_rad = np.arctan2(nose_vector[1], eye_line[0])
    pitch_deg = np.degrees(pitch_rad)

    return yaw_deg, pitch_deg

# メインループ
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("カメラから映像が取得できませんでした")
        break

    # ミラー反転して、ユーザー視点に合わせる
    frame = cv2.flip(frame, 1)
    rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            h, w, _   = frame.shape
            landmarks = face_landmarks.landmark

            # ランドマーク描画（デバッグ用）
            for i in LEFT_EYE_INDICES:
                x = int(landmarks[i].x * w)
                y = int(landmarks[i].y * h)
                cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)
            for i in RIGHT_EYE_INDICES:
                x = int(landmarks[i].x * w)
                y = int(landmarks[i].y * h)
                cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)

            # EARとMARによる状態検出
            ear_person_left  = calculate_ear(landmarks, RIGHT_EYE_INDICES, w, h)
            ear_person_right = calculate_ear(landmarks, LEFT_EYE_INDICES,  w, h)
            mar              = calculate_mar(landmarks, w, h)

            # --- キャリブレーション処理 ---
            if not calibrated:
                if sampling_state == "open":
                    ear_open_list.append(ear_person_left)
                    ear_open_list.append(ear_person_right)
                    frame_counter += 1
                    if frame_counter >= SAMPLE_FRAMES:
                        sampling_state = "close"
                        frame_counter  = 0
                        print("→ 開眼サンプル完了。続いて目を閉じてください。")
                    # キャリブレーション中は判定せず次フレームへ
                    continue

                if sampling_state == "close":
                    ear_close_list.append(ear_person_left)
                    ear_close_list.append(ear_person_right)
                    frame_counter += 1
                    if frame_counter >= SAMPLE_FRAMES:
                        # 閾値計算
                        open_mean  = np.mean(ear_open_list)
                        close_mean = np.mean(ear_close_list)
                        thr_left   = (open_mean + close_mean) / 2
                        thr_right  = thr_left
                        calibrated = True
                        print(f"→ キャリブレーション完了! threshold = {thr_left:.3f}")
                    continue

            # キャリブレーション後の判定
            eye_open_left  = int(ear_person_left  > thr_left)
            eye_open_right = int(ear_person_right > thr_right)
            mouth_open     = int(mar > 0.5)

            # 顔の角度取得
            yaw, pitch = get_face_angle(landmarks, w, h)

            # UDPで送信するデータ構築
            data = {
                "eye":   {"left": eye_open_left,  "right": eye_open_right},
                "mouth": mouth_open,
                "rotation": {"yaw": yaw, "pitch": pitch}
            }
            sock.sendto(json.dumps(data).encode(), (UDP_IP, UDP_PORT))

            # —— デバッグ表示 ——
            cv2.putText(frame,
                f"Left EAR : {ear_person_left:.2f} ({'Open' if eye_open_left else 'Closed'})",
                (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
            cv2.putText(frame,
                f"Right EAR: {ear_person_right:.2f} ({'Open' if eye_open_right else 'Closed'})",
                (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
            cv2.putText(frame,
                f"MAR      : {mar:.2f} ({'Open' if mouth_open else 'Closed'})",
                (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)
            cv2.putText(frame,
                f"Yaw  : {yaw:.1f}", (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,200,0), 2)
            cv2.putText(frame,
                f"Pitch: {pitch:.1f}", (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,200,0), 2)

    # ウィンドウ表示／終了判定
    cv2.putText(frame, "Press ESC to exit", (30, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 1)
    window_name = "Face Motion Tracker - Press ESC to exit"
    cv2.imshow(window_name, frame)

    if cv2.waitKey(1) & 0xFF == 27 or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
sock.close()
cv2.destroyAllWindows()
