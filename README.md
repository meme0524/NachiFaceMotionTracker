# Eye Blink Project

顔のトラッキングを使って、目が閉じているかどうかをリアルタイムで判定するアプリケーションです。  
MediaPipeとOpenCVを用いたPythonスクリプトで動作し、将来的にはUnityと連携し、3Dモデルに表情を反映させることを目指しています。

---

## ✅ 現在の進捗

- [x] Webカメラから顔を検出
- [x] EAR（Eye Aspect Ratio）による目の開閉判定
- [x] ESCキーでウィンドウを閉じられる
- [x] ウィンドウに案内メッセージを表示
- [ ] Unityとのリアルタイム連携（UDP通信）
- [ ] 3Dモデル（BlendShape）の制御

---

## 🚀 使用技術

- Python 3.x
- OpenCV
- MediaPipe
- NumPy
- Git / GitHub

---

## 🔧 実行方法

```bash
pip install opencv-python mediapipe numpy
python eye_blink.py
