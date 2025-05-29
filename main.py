# main.py

# ----------- 必要なライブラリのインポート -----------
import cv2
import mediapipe as mp
import numpy as np
import socket  # ← UDP用モジュール追加


# 目のEAR計算用関数とランドマーク定義をインポート
from detection.eye import calculate_ear, LEFT_EYE_INDICES
from detection.mouth import calculate_mar  # 👈 口検出の関数も忘れずにインポート

# ----------- MediaPipeの初期化 -----------
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,  # 動画用モード（連続検出）
    max_num_faces=1           # 検出する顔は1つだけ
)

# ----------- カメラの起動 -----------
cap = cv2.VideoCapture(0)  # 0番カメラ（通常は内蔵カメラ）

# ----------- UDPソケットの設定 -----------
# Unity側の受信設定に合わせる
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# ----------- メインループ（毎フレーム処理）-----------
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("カメラから映像が取得できませんでした")
        break

    # 左右反転して自分と同じ向きに表示（ミラー）
    frame = cv2.flip(frame, 1)

    # BGR → RGB に変換（MediaPipeはRGBを要求）
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 顔ランドマークの検出
    results = face_mesh.process(rgb)

    # 検出された顔があれば処理
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            h, w, _ = frame.shape  # 画像サイズ取得

            # ----- 目の開閉状態（EAR）計算 -----
            ear = calculate_ear(face_landmarks.landmark, LEFT_EYE_INDICES, w, h)
            eye_status = "Closed" if ear < 0.2 else "Open"
            cv2.putText(frame, f"Eye: {eye_status} ({ear:.2f})", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0) if eye_status == "Open" else (0, 0, 255), 2)

            # ----- 口の開閉状態（MAR）計算 -----
            mar = calculate_mar(face_landmarks.landmark, w, h)
            mouth_status = "Open" if mar > 0.5 else "Closed"
            cv2.putText(frame, f"Mouth: {mouth_status} ({mar:.2f})", (30, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 255) if mouth_status == "Open" else (100, 100, 100), 2)
            
        message = f"eye:{eye_status.lower()},mouth:{mouth_status.lower()}"
        sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
        

    # ----------- ユーザー向けの案内表示 -----------
    cv2.putText(frame, "Press ESC to exit", (30, 130),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

    # ----------- ウィンドウ表示と終了処理 -----------
    window_name = "Face Motion Tracker - Press ESC to exit"
    cv2.imshow(window_name, frame)

    # ESCキーで終了 または ウィンドウの×が押されたら終了
    if cv2.waitKey(1) & 0xFF == 27:
        break
    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
        break

# ----------- 終了処理 -----------
cap.release()
sock.close()
cv2.destroyAllWindows()
