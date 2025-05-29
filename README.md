# Eye Blink Project

**Webカメラで顔の動きをトラッキングして、Unityアバターに反映するプロジェクト**  
目の開閉（EAR）や口の開閉（MAR）をリアルタイムで検出し、UDPでUnityに送信します。

---
# プロジェクト構成
face_motion_tracker/
├── main.py # メインスクリプト（顔トラッキング + UDP送信）
├── send_test.py # UDP送信用の簡易テストスクリプト
├── detection/
│ ├── eye.py # 目の開閉度（EAR）の計算
│ └── mouth.py # 口の開閉度（MAR）の計算
├── face_motion_receiver/ # Unityプロジェクト（Assets/Scripts のみ Git管理）
└── ...

---

## ✅ 現在の進捗

- Webカメラから目の開閉（EAR）と口の開閉（MAR）をリアルタイムで検出
- UnityにUDPで状態（open/closed）を送信する機能を実装
- Unity側では UDPReceiver.cs により受信可能
- 有料モデルや不要ファイルは `.gitignore` によって安全に除外済み

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
