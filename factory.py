# factory.py
from abc import ABC, abstractmethod
import time
from urllib.parse import quote_plus
import cv2

# -------------------------------
# Helper functions for RTSP URLs
# -------------------------------
def make_cpplus_rtsp_url(ip, username, password):
    return f"rtsp://{username}:{password}@{ip}:554/cam/realmonitor?channel=1&subtype=0"

def make_ipcam_rtsp_url(ip, username, password, path="stream1", port=554):
    u = quote_plus(username)
    p = quote_plus(password)
    return f"rtsp://{u}:{p}@{ip}:{port}/{path}"

# -------------------------------
# Abstract Product
# -------------------------------
class Camera(ABC):
    def __init__(self, ip, user, password):
        self.ip = ip
        self.user = user
        self.password = password
        self.stream_url = None

    @abstractmethod
    def connect(self): 
        pass

    @abstractmethod
    def get_feed(self): 
        pass

# -------------------------------
# Concrete Products
# -------------------------------
class ipcamera(Camera):
    def connect(self):
        print(f"Connecting to IP Camera")
        time.sleep(1)
        self.stream_url = make_ipcam_rtsp_url(self.ip, self.user, self.password)
        print(f"Connected successfully!")

    def get_feed(self):
        if not self.stream_url:
            print("❌ Not connected yet. Please connect first.")
            return

        cap = cv2.VideoCapture(self.stream_url)
        if not cap.isOpened():
            print(f"❌ Failed to open stream for {self.ip}")
            return

        print(f"📷 Streaming feed from IP Camera ({self.ip})...")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame.")
                break

            # Resize frame to 640x320
            frame = cv2.resize(frame, (640, 320))

            cv2.imshow(f"IP Camera {self.ip}", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

class cpplus(Camera):
    def connect(self):
        print(f"Connecting to CPPlus Camera")
        time.sleep(1)
        self.stream_url = make_cpplus_rtsp_url(self.ip, self.user, self.password)
        print(f"Connected successfully!")

    def get_feed(self):
        if not self.stream_url:
            print("❌ Not connected yet. Please connect first.")
            return

        cap = cv2.VideoCapture(self.stream_url)
        if not cap.isOpened():
            print(f"❌ Failed to open stream for {self.ip}")
            return

        print(f"📷 Streaming feed from CPPlus Camera ({self.ip})...")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame.")
                break

            # Resize frame to 640x320
            frame = cv2.resize(frame, (640, 320))

            cv2.imshow(f"CPPlus Camera {self.ip}", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

# -------------------------------
# Factory
# -------------------------------
class CameraFactory:
    @staticmethod
    def get_camera(camera_type, ip, user, password):
        if camera_type == "ipcamera":
            return ipcamera(ip, user, password)
        elif camera_type == "cpplus":
            return cpplus(ip, user, password)
        else:
            raise ValueError("Unknown camera type")
