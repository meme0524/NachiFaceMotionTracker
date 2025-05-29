# This script tests the camera functionality using OpenCV.
# It captures video from the default camera and displays it in a window.
# If the ESC key is pressed, it exits the loop and closes the window.

# camera_test.py
import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("can't open camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow('camera test', frame)
    if cv2.waitKey(1) == 27:  # ESCキーで終了
        break

cap.release()
cv2.destroyAllWindows()
