# face_motion_tracker for Unity
**Webカメラで顔の動きをトラッキングして、Unityアバターに反映するプロジェクト**  
目の開閉（EAR）や口の開閉（MAR）をリアルタイムで検出し、UDPでUnityに送信します。

---

## ✅ 現在の進捗

- Webカメラから目の開閉（EAR）と口の開閉（MAR）をリアルタイムで検出
- UnityにUDPで状態（open/closed）を送信する機能を実装
- Unity側では UDPReceiver.cs により受信可能

---

## 🚀 使用技術

- Python 3.8+
  - OpenCV
  - MediaPipe
  - socket（UDP通信）
- Unity 2022.3.22f1（Built-in Render Pipeline）
  - C#（UDP受信処理）
  - VRChat SDK対応プロジェクトとして構成
- Git / GitHub（バージョン管理）

---

## 🔧 実行方法

### ▶ Python側

Webカメラが起動し、顔のランドマークが検出されます。
目の開閉状態（EAR）と口の開閉状態（MAR）が表示され、UDPで送信されます。
```powershell
python main.py

### ▶ Unity側
face_motion_receiver/Assets/Scripts/UDPReceiver.cs を GameObject にアタッチ

シーンを再生（Play）して、受信状態を確認

受信内容に応じて、アバターの表情制御などへ拡張可能
