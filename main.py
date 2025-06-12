# main.py

# ----------- 必要なライブラリのインポート -----------
import cv2
import mediapipe as mp
import numpy as np

# 目のEAR計算用関数とランドマーク定義をインポート
from detection.eye import calculate_ear, LEFT_EYE_INDICES, RIGHT_EYE_INDICES
from detection.mouth import calculate_mar  # 👈 口検出の関数も忘れずにインポート

# ----------- MediaPipeの初期化 -----------
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,  # 動画用モード（連続検出）
    max_num_faces=1           # 検出する顔は1つだけ
)

# ----------- カメラの起動 -----------
cap = cv2.VideoCapture(0)  # 0番カメラ（通常は内蔵カメラ）

# ----------- キャリブレーション用変数 -----------
calibrated = False
sampling_state = "eye_open"  # eye_open -> eye_close -> mouth_open -> done
frame_counter = 0
SAMPLE_FRAMES = 100
ear_open_left = []
ear_close_left = []
ear_open_right = []
ear_close_right = []
mar_open_list = []
mar_close_list = []
thr_left = 0.2
thr_right = 0.2
thr_mar = 0.5

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
            left_ear = calculate_ear(face_landmarks.landmark,
                                     LEFT_EYE_INDICES, w, h)
            right_ear = calculate_ear(face_landmarks.landmark,
                                      RIGHT_EYE_INDICES, w, h)

            # ----- 口の開閉状態（MAR）計算 -----
            mar = calculate_mar(face_landmarks.landmark, w, h)

            # ----- キャリブレーション処理 -----
            if not calibrated:
                if sampling_state == "eye_open":
                    ear_open_left.append(left_ear)
                    ear_open_right.append(right_ear)
                    mar_close_list.append(mar)
                    frame_counter += 1
                    cv2.putText(frame, "Calibrating: keep eyes OPEN", (30, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                    if frame_counter >= SAMPLE_FRAMES:
                        sampling_state = "eye_close"
                        frame_counter = 0
                        print("→ 開眼サンプル完了。続いて目を閉じてください。")
                    continue

                if sampling_state == "eye_close":
                    ear_close_left.append(left_ear)
                    ear_close_right.append(right_ear)
                    mar_close_list.append(mar)
                    frame_counter += 1
                    cv2.putText(frame, "Calibrating: keep eyes CLOSED", (30, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                    if frame_counter >= SAMPLE_FRAMES:
                        sampling_state = "mouth_open"
                        frame_counter = 0
                        print("→ 目閉じサンプル完了。続いて口を開いてください。")
                    continue

                if sampling_state == "mouth_open":
                    mar_open_list.append(mar)
                    frame_counter += 1
                    cv2.putText(frame, "Calibrating: open mouth", (30, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                    if frame_counter >= SAMPLE_FRAMES:
                        thr_left = (np.mean(ear_open_left) + np.mean(ear_close_left)) / 2
                        thr_right = (np.mean(ear_open_right) + np.mean(ear_close_right)) / 2
                        thr_mar = (np.mean(mar_open_list) + np.mean(mar_close_list)) / 2
                        calibrated = True
                        print(
                            f"→ キャリブレーション完了! eye_left={thr_left:.3f} eye_right={thr_right:.3f} mouth={thr_mar:.3f}"
                        )
                    continue

            # ----- キャリブレーション後の判定 -----
            left_status = "Closed" if left_ear < thr_left else "Open"
            right_status = "Closed" if right_ear < thr_right else "Open"
            mouth_status = "Open" if mar > thr_mar else "Closed"

            cv2.putText(frame, f"Left Eye: {left_status} ({left_ear:.2f})", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0) if left_status == "Open" else (0, 0, 255), 2)
            cv2.putText(frame, f"Right Eye: {right_status} ({right_ear:.2f})", (30, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0) if right_status == "Open" else (0, 0, 255), 2)
            cv2.putText(frame, f"Mouth: {mouth_status} ({mar:.2f})", (30, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 255) if mouth_status == "Open" else (100, 100, 100), 2)

    # ----------- ユーザー向けの案内表示 -----------
    cv2.putText(frame, "Press ESC to exit", (30, 170),
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
cv2.destroyAllWindows()