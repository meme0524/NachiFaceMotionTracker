# 開発ログ：face_motion_tracker
## 2025-05-30
- `main.py` から UDP 通信による目・口の状態送信機能を実装（eye:open, mouth:closed の形式）
- Unity側に `UDPReceiver.cs` を作成し、リアルタイムでの受信に成功！
- `send_test.py` を作成し、Python単体でも通信テストが可能に
- `.gitignore` を整理し、Unity内の有料モデルや `.meta` ファイル、Scripts 以外を除外
- Unityプロジェクトは `face_motion_receiver/Assets/Scripts/` のみを Git 管理対象とした
- `README.md` の構成・実行方法セクションを整理し、プロジェクトの概要を明示

## 次やること
- Unityアバターのまばたき／口パクとの連携を実装
- Python 側で表情ステータス（例：normal, smile, talk 等）を送る機能を検討
- 受信データのログ保存や、Webカメラ切り替え設定を整備


## 2025-05-29
- PowerShellでGit使えるようになった
- GitHubリポジトリ作成完了
- .gitignore追加
- カメラ映像から目の開閉ができるようになった！

### ✨ 追記
- プロジェクト名を `face_motion_tracker` に変更
- ファイル構成を整理し、`main.py` / `detection/eye.py` に分割
- `detection/mouth.py` を新規作成し、口の開閉判定（MAR）を実装
- `main.py` に口の開閉状態を表示する処理を追加
- コード全体に丁寧なコメントを追加して可読性アップ

## 次やること
- Unityとの連携方法（UDPなど）を検討する
- モデルへの反映（まばたき・口パク）を試してみたい
- 表示の切り替えやログ出力の実装も検討する
