#!/usr/bin/env python3
import sys
from pathlib import Path

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


def read_cpu_temp() -> float:
    """
    Returns the CPU temperature in °C.
    Works on all Raspberry Pi models where the kernel exposes
    /sys/class/thermal/thermal_zone0/temp.
    """
    temp_path = Path("/sys/class/thermal/thermal_zone0/temp")
    if temp_path.exists():
        # Value is in millidegrees (e.g. 45321 → 45.321 °C)
        return int(temp_path.read_text().strip()) / 1000.0
    else:
        # Fallback for very old images that may lack the file
        # Requires `vcgencmd` to be installed.
        import subprocess, shlex

        out = subprocess.check_output(shlex.split("vcgencmd measure_temp"))
        # vcgencmd outputs: temp=45.3'C
        return float(out.decode().split("=")[1].split("'")[0])


class TempWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pi Zero CPU Temperature")

        self.label = QLabel("", self)
        self.label.setStyleSheet("font-size: 28px;")

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(20, 20, 20, 20)

        # First update immediately
        self.update_temp()

        # Update every 1000 ms
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_temp)
        self.timer.start(1_000)

    def update_temp(self):
        temp_c = read_cpu_temp()
        self.label.setText(f"CPU Temperature: {temp_c:,.1f} °C")


def main():
    app = QApplication(sys.argv)
    window = TempWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
