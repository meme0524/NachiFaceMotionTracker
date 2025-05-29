import socket
import time

# Unity側の受信設定に合わせる
UDP_IP = "127.0.0.1"     # 自分のPC（localhost）
UDP_PORT = 5005          # UnityのUDPReceiver.csで使っているポート番号

# UDPソケットの作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# テストメッセージを送信し続けるループ
try:
    while True:
        message = "eye:open,mouth:closed"   # Unityに送る文字列
        sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
        print(f"Sent: {message}")
        time.sleep(1)  # 1秒ごとに送信
except KeyboardInterrupt:
    print("\n送信を終了しました。")
finally:
    sock.close()
