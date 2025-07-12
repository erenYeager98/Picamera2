# viewer_gui.py (runs on the Display Pi)
import sys
import cv2
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QSlider, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QObject
from io import BytesIO

CAMERA_IP = "http://192.168.227.117:8000"  # Replace with your camera Pi's IP

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        try:
            r = requests.get(f"{CAMERA_IP}/stream", stream=True)
            byte_buffer = b""
            for chunk in r.iter_content(chunk_size=1024):
                if not self._run_flag:
                    break
                byte_buffer += chunk
                a = byte_buffer.find(b'\xff\xd8')  # JPEG start
                b = byte_buffer.find(b'\xff\xd9')  # JPEG end
                if a != -1 and b != -1:
                    jpg = byte_buffer[a:b+2]
                    byte_buffer = byte_buffer[b+2:]
                    frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    if frame is not None:
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        h, w, ch = rgb.shape
                        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()
                        self.change_pixmap_signal.emit(img)
        except Exception as e:
            print("Streaming error:", e)

    def stop(self):
        self._run_flag = False
        self.wait()

class CameraViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Remote Camera Viewer")
        self.setFixedSize(850, 700)

        layout = QVBoxLayout()

        # Video feed display
        self.video_label = QLabel()
        self.video_label.setFixedSize(800, 600)
        layout.addWidget(self.video_label)

        # Controls
        controls_layout = QHBoxLayout()

        self.zoom_in_btn = QPushButton("Zoom In")
        self.zoom_out_btn = QPushButton("Zoom Out")
        self.flip_h_btn = QPushButton("Flip H")
        self.flip_v_btn = QPushButton("Flip V")
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(50)

        controls_layout.addWidget(self.zoom_in_btn)
        controls_layout.addWidget(self.zoom_out_btn)
        controls_layout.addWidget(self.flip_h_btn)
        controls_layout.addWidget(self.flip_v_btn)
        controls_layout.addWidget(QLabel("Brightness"))
        controls_layout.addWidget(self.brightness_slider)

        layout.addLayout(controls_layout)
        self.setLayout(layout)

        # Connect actions
        self.zoom_level = 1.0
        self.hflip = False
        self.vflip = False

        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.flip_h_btn.clicked.connect(self.flip_h)
        self.flip_v_btn.clicked.connect(self.flip_v)
        self.brightness_slider.valueChanged.connect(self.set_brightness)

        # Setup video thread
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    def update_image(self, img):
        self.video_label.setPixmap(QPixmap.fromImage(img))

    def zoom_in(self):
        self.zoom_level = min(4.0, self.zoom_level + 0.1)
        requests.post(f"{CAMERA_IP}/zoom", json={"level": self.zoom_level})

    def zoom_out(self):
        self.zoom_level = max(1.0, self.zoom_level - 0.1)
        requests.post(f"{CAMERA_IP}/zoom", json={"level": self.zoom_level})

    def flip_h(self):
        self.hflip = not self.hflip
        requests.post(f"{CAMERA_IP}/flip", json={"horizontal": self.hflip, "vertical": self.vflip})

    def flip_v(self):
        self.vflip = not self.vflip
        requests.post(f"{CAMERA_IP}/flip", json={"horizontal": self.hflip, "vertical": self.vflip})

    def set_brightness(self, value):
        requests.post(f"{CAMERA_IP}/brightness", json={"value": value})

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

if __name__ == '__main__':
    import numpy as np
    app = QApplication(sys.argv)
    viewer = CameraViewer()
    viewer.show()
    sys.exit(app.exec_())
