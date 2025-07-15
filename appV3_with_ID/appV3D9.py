#V1
#pwm frequency reduced 400 to 200
#Removed H button 
#Removed accumulated  count display.
#Password from 123 to 1121
#Shutdown pin logic from 1 to 0
#baud rate 9600 to 1200
#V2
#left and right movement form 25,75 and 150 to 12,40 and 75
#V3D1 14.02.2025
#zoom level to default when the horizontal or vertical flip button pressed.
#Right and left button are disabled until they complete their transmission.Same goes for PWM Pulse generation(RIGHT/LEFT) as well as UART signal (UP/DOWN)
#Added Radio buttons (L/R R/L) inside the CAL with password and added their swapping function.
#added 4 digit in transmition message for shutdowm indication. old message  f"U\r\n{a1}{b1}0001\r\n" new message f"U\r\n{a1}{b1}00010001\r\n"
#V3D2 17.02.2025
#UP DOWN key placement to be updated
#Shutdown, Saturation, Contrast, Sharpness, Brightness and Defaut button to be hidden
#Add Label as Direction: *L/R R/L
# L/R R/L selection to be made Non Volatile
#V3D3 19.02.2025
# Moved L/R R/L inside cal.It is coming out after setting corrected
# Left right Key during disabled condition also it accepts one key press corrected.
# frame rate form 1 to 3 in all locations picam2.set_controls({"FrameRate": 3})
#V3D4 20.02.2025
# Move zoom button below vertical flip
# add Label DIRECTION: .L/R R/L 
# Indicate E on the arror keys corrected
# Disable both left and right key to avoid multiple entries. 
#
#V3D5 01.03.2025
#Unhide Brightness Slider place below Zoom Key, Range Value 0-100 
#Suffix this value in serial data ex., from f"U\r\n{a1}{b1}00000000\r\n" to f"U\r\n{a1}{b1}000000000100\r\n"
#send this serial data when the slider moves to the new value
#
#add temperature indication
#!/usr/bin/python3
import subprocess
import requests
import init_node
import os
import sys
import re
import numpy as np
from gpiozero import PWMOutputDevice, DigitalOutputDevice,InputDevice
from time import sleep
import time
import serial
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal,QThread,QProcess,QEvent,QCoreApplication,QTimer
from PyQt5.QtGui import QIntValidator, QPixmap,QFont,QImage
import libcamera
import cv2
# # from picamera2 import Picamera2
from pathlib import Path
from picamera2.previews.qt import QPicamera2
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDesktopWidget,
                             QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QSlider, QSpinBox,
                             QVBoxLayout, QWidget,QGridLayout,QSizePolicy,QFileDialog,QLayout,QRadioButton)

# Define constants and variables
CAMERA_IP = "http://192.168.227.117:8000"  # Replace with your camera Pi's IP
SERIAL_PORT = '/dev/ttyS0'
BAUD_RATE = 1200 # Modify this value to define the baud rate
hflip=0
vflip=0
i=0
input_pin22 = 22
input_22= InputDevice(input_pin22)
input_pin = 10
pin_17 = 17
input_pin_left = 9
output_pin = 26 
stepper_enable_pin = 19
pwm_pin = 13 
a1 = None
b1 = None

input_device = InputDevice(input_pin)
input_17 = InputDevice(pin_17)
output_device = DigitalOutputDevice(output_pin)
stepper_enable = DigitalOutputDevice(stepper_enable_pin)
input_device_left = InputDevice(input_pin_left)
pwm = PWMOutputDevice(pwm_pin)
def request_callback(request):
    label.setText(''.join(f"{k}: {v}\n" for k, v in request.get_metadata().items()))

# def cleanup():
#     picam2.post_callback = None
def ensure_four_digits(input_string):
    digits = ''.join(filter(str.isdigit, input_string))
    
    # Check the length of the digits and add leading zeros if necessary
    if len(digits) < 4:
        digits = digits.zfill(4)
        
    return digits


class Shutdown_by_pin(QThread):
    def run(self):
        while True:
            if input_17.value == 1:
                shutdown_pi()
                time.sleep(0.1)

    try:
        log_file_path="buffer"
        if os.path.exists(log_file_path):
            os.remove(log_file_path)
            print(f"[INFO] Deleted buffer file: {log_file_path}")
    except Exception as e:
        print(f"[ERROR] Failed to delete buffer: {e}")
               

class SerialListener(QThread):
    new_data = pyqtSignal(str)  # Signal to update GUI

    def __init__(self, port=SERIAL_PORT, baudrate=9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.stack = []
        self.running = True
        self.log_file_path = "buffer"

        # Load previous values from file into stack
        self.restore_stack_from_buffer()
        print("[DEBUG] SerialListener object created")


    def restore_stack_from_buffer(self):
        try:
            with open(self.log_file_path, "r", encoding='utf-8') as f:
                content = f.read()
                self.stack = re.findall(r'\{(.*?)\}', content)
                print(f"[INFO] Restored {len(self.stack)} items from buffer")
        except FileNotFoundError:
            print("[INFO] No previous buffer file found. Starting fresh.")
            self.stack = []

    def run(self):
        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=0.1)
            print("[INFO] Serial listener started.")
            buffer = ""

            with open(self.log_file_path, "a", encoding='utf-8') as log_file:
                while self.running:
                    if ser.in_waiting:
                        data = ser.read(ser.in_waiting).decode(errors='ignore')
                        print(f"[DEBUG] Bytes waiting: {ser.in_waiting}")
                        buffer += data

                        # Log all raw data
                        log_file.write(data)
                        log_file.flush()
                        print(f"[DEBUG] Raw data: {repr(data)}")

                        # Handle "\r\r" to show last stored value
                        if "\r\r" in buffer:
                            print(f"[DEBUG] Current buffer: {repr(buffer)}")
                            buffer = buffer.replace("\r\r", "")
                            if self.stack:
                                last_value = self.stack[-1]
                                self.new_data.emit(f"{last_value}")
                                print(f"[INFO] Last stored value: {last_value}")
                                log_file.write(f"[READ STACK TOP] {last_value}\n")
                            else:
                                # self.new_data.emit("Stack is empty")
                                log_file.write("[STACK EMPTY]\n")

                        # Handle valid message: \r\n{value}\r\n
                        matches = re.findall(r'\r\n(\d+)\r\n', buffer)
                        for match in matches:
                            self.stack.append(match)
                            # self.new_data.emit(f"Received and stored: {match}")
                            print(f"[INFO] Stored: {match}")
                            log_file.write(f"[STORED] {match}\n")
                            log_file.flush()
                            buffer = buffer.replace(f"\r\n{match}\r\n", "")


                    time.sleep(0.05)

        except serial.SerialException as e:
            # self.new_data.emit(f"[ERROR] Serial error: {e}")
            with open(self.log_file_path, "a", encoding='utf-8') as log_file:
                log_file.write(f"[ERROR] {e}\n")

    def stop(self):
        self.running = False
        self.wait()
        print("[INFO] Serial listener stopped.")

class SavingThread(QThread):
    finished2 = pyqtSignal()
    def run(self):
        while True:
            save_state()
            time.sleep(5)

# def set_txt_():
#     navigate_Buttons.txt_total_right_increment.setText("0")

def save_state():
        filePath="/home/camera1/resources/widget_state.txt"
        subprocess.run("clear", shell=True, capture_output=True, text=True)

        stateValue1 = "0"
        stateValue2 = "0"
        radio_state = "0"
        if repeat_circum.radio_rl.isChecked():
            radio_state = "1"
        if(image_Controls.hflip_btn.text()=="BACK TO NORMAL"):
            stateValue1 = "1"
        if(image_Controls.vflip_btn.text()=="BACK TO NORMAL"):
            stateValue2 = "1"
        state = [
            stateValue1,
            stateValue2,
            image_Controls.zoom_button.text(),
            repeat_circum.input_field1.text(),
            # repeat_circum.input_field2.text(),
            repeat_circum.gr_tc_input.text(),
            radio_state,
            str(image_Controls.brightness2.value())
            # navigate_Buttons.txt_total_right_increment.text()
        ]
        if(state[3]==""):
            state[3]=="0"
        if(state[4]==""):
            state[4]=="0"
        if(state[5]==""):
            state[5]=="0"
        if(state[6]==""):
            state[6]=="0"
        
        # if(state[5]==None):
        #     state[5]=="0"
        # if(state[6]==None):
        #     state[6]=="0"
        

        with open(filePath, 'w') as file:
            file.write('\n'.join(state))

def pop_error():
    app = QApplication(sys.argv)
    font = QFont()
    font.setPointSize(12)
    # Create the main window
    window = QWidget()
    window.setWindowTitle('Error')
    window.setWindowFlags(Qt.FramelessWindowHint)
    shutdown_btn = QPushButton("X")
    shutdown_btn.setFont(font)
    shutdown_btn.setFixedWidth(35)
    shutdown_btn.setFixedHeight(35)
    shutdown_btn.clicked.connect(shutdown_pi_without_saving)
    # Set up the layout and label
    layout = QVBoxLayout()
    label = QLabel(f"Camera Disconnected")

    # Customize the label if needed
    label.setWordWrap(True)

    # Add the label to the layout
    layout.addWidget(shutdown_btn)
    layout.addWidget(label)

    # Set the layout for the main window
    window.setLayout(layout)

    # Show the window
    window.show()

    # Run the application's main loop
    sys.exit(app.exec_())

def load_state():
        filePath = '/home/camera1/resources/widget_state.txt'
        subprocess.run("clear", shell=True, capture_output=True, text=True)

        try:
            # Read the state from the file
            with open(filePath, 'r') as file:
                
                state = file.readlines()
                print(state)
                if(state[0].strip()=="1"):
                    image_Controls.hflip_btn.click()
                if(state[1].strip()=="1"):
                    image_Controls.vflip_btn.click()
                if(state[2].strip()=="2X"):
                    image_Controls.zoom_button.click()
                if(state[2].strip()=="3X"):
                    image_Controls.zoom_button.click()
                    image_Controls.zoom_button.click()
                if(state[2].strip()=="4X"):
                    image_Controls.zoom_button.click()
                    image_Controls.zoom_button.click()
                    image_Controls.zoom_button.click()
                if(state[2].strip()=="5X"):
                    image_Controls.zoom_button.click()
                    image_Controls.zoom_button.click()
                    image_Controls.zoom_button.click()
                    image_Controls.zoom_button.click()
                repeat_circum.input_field1.setText(str(state[3].strip()))
                repeat_circum.gr_tc_input.setText(str(state[4].strip()))
                if(state[5].strip()=="1"):
                    repeat_circum.radio_rl.click()
                else:
                    repeat_circum.radio_lr.click()
                image_Controls.setValue_brightness(int(state[6].strip())) if not state[6].strip() == "0" else None

                # if(len(state)==5):
                #     state.append("0")
                # navigate_Buttons.txt_total_right_increment.setText(str(state[5].strip()))
                # navigate_Buttons.txt_total_increment.setText("0")

                
        except FileNotFoundError:
            pass
        a=str(ensure_four_digits(repeat_circum.input_field1.text()))
        a1=a
        b=str(ensure_four_digits(repeat_circum.gr_tc_input.text()))
        b1=b
        c=str(ensure_four_digits(str(image_Controls.brightness2.value())))
        c1=c
        formatted_message = f"U\r\n{a1}{b1}00000000{c1}\r\n"
        ser = serial.Serial(
            port='/dev/ttyS0', 
            baudrate=1200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

        # Open the serial port if it's not already open
        if not ser.is_open:
            ser.open()

        # Send the formatted message
        ser.write(formatted_message.encode())

        # Close the serial port
        ser.close()

class controlSlider(QWidget):
    def __init__(self, box_type=float):
        super().__init__()
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setSingleStep(1)
        self.slider.setValue(50)  # Set default to 50

        if box_type == float:
            self.box = QDoubleSpinBox()
            self.box.setDecimals(2)  # Optional: Keep precision for float
        else:
            self.box = QSpinBox()

        self.box.setRange(0, 100)
        self.box.setSingleStep(1)
        self.box.setValue(50)  # Set default to 50

        self.valueChanged = self.box.valueChanged
        self.valueChanged.connect(lambda: self.setValue(self.value()))
        self.slider.valueChanged.connect(self.updateValue)

        self.layout.addWidget(self.box)
        self.layout.addWidget(self.slider)

        self.precision = self.box.singleStep()

    def updateValue(self):
        self.blockAllSignals(True)
        if self.box.value() != self.slider.value() * self.precision:
            self.box.setValue(self.slider.value() * self.precision)
        self.blockAllSignals(False)
        self.valueChanged.emit(self.value())

    def setSingleStep(self, val):
        self.box.setSingleStep(val)
        self.precision = val

    def setValue(self, val, emit=False):
        self.blockAllSignals(True)
        if val is None:
            val = 0
        self.box.setValue(val)
        self.slider.setValue(int(val / self.precision))
        self.blockAllSignals(False)
        if emit:
            self.valueChanged.emit(self.value())

    def setMinimum(self, val):
        self.box.setMinimum(val)
        self.slider.setMinimum(int(val / self.precision))

    def setMaximum(self, val):
        self.box.setMaximum(val)
        self.slider.setMaximum(int(val / self.precision))

    def blockAllSignals(self, y):
        self.box.blockSignals(y)
        self.slider.blockSignals(y)

    def value(self):
        return self.box.value()

class controlSlider_2(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 100)  # Set range 1 - 100
        self.slider.setSingleStep(1)  # Move in steps of 1
        self.slider.setValue(50)  # Default value

        self.box = QSpinBox()  # Use integer-based spin box
        self.box.setRange(1, 100)  # Set same range as slider
        self.box.setSingleStep(1)
        self.box.setValue(50)  # Default value

        self.valueChanged = self.box.valueChanged
        self.valueChanged.connect(self.syncSlider)
        self.slider.valueChanged.connect(self.syncBox)

        self.layout.addWidget(self.box)
        self.layout.addWidget(self.slider)

    def syncSlider(self):
        self.slider.setValue(self.box.value())

    def syncBox(self):
        self.box.setValue(self.slider.value())

    def value(self):
        return self.box.value()
    def setValue(self, val):
        self.box.setValue(val)
    def setValueSlider(self,val):
        self.slider.setValue(val)

    
class logControlSlider(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.slider = QSlider(Qt.Horizontal)
        self.box = QDoubleSpinBox()

        self.valueChanged = self.box.valueChanged
        self.valueChanged.connect(lambda: self.setValue(self.value()))
        self.slider.valueChanged.connect(self.updateValue)

        #self.layout.addWidget(self.box)
        self.layout.addWidget(self.slider)

        self.precision = self.box.singleStep()
        self.slider.setSingleStep(1)
        self.minimum = 0.0
        self.maximum = 2.0

    @property
    def points(self):
        return int(1.0 / self.precision) * 2

    def boxToSlider(self, val=None):
        if val is None:
            val = self.box.value()
        if val == 0:
            return 0
        else:
            center = self.points // 2
            scaling = center / np.log2(self.maximum)
            return round(np.log2(val) * scaling) + center

    def sliderToBox(self, val=None):
        if val is None:
            val = self.slider.value()
        if val == 0:
            return 0
        else:
            center = self.points // 2
            scaling = center / np.log2(self.maximum)
            return round(2**((val - center) / scaling), int(-np.log10(self.precision)))

    def updateValue(self):
        self.blockAllSignals(True)
        if self.box.value() != self.sliderToBox():
            self.box.setValue(self.sliderToBox())
        self.blockAllSignals(False)
        self.valueChanged.emit(self.value())

    def redrawSlider(self):
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.points)
        self.slider.setValue(self.boxToSlider())

    def setSingleStep(self, val):
        self.box.setSingleStep(val)
        self.precision = val

    def setValue(self, val, emit=False):
        self.blockAllSignals(True)
        self.box.setValue(val)
        self.redrawSlider()
        self.blockAllSignals(False)
        if emit:
            self.valueChanged.emit(self.value())

    def setMinimum(self, val):
        self.box.setMinimum(val)
        self.minimum = val
        self.redrawSlider()

    def setMaximum(self, val):
        self.box.setMaximum(val)
        self.maximum = val
        self.redrawSlider()

    def blockAllSignals(self, y):
        self.box.blockSignals(y)
        self.slider.blockSignals(y)

    def value(self):
        return self.box.value()

def shutdown_pi():
        stepper_enable.off()
        # Execute save before shutdown!
        save_state()
        a=str(ensure_four_digits(repeat_circum.input_field1.text()))
        a1=a
        b=str(ensure_four_digits(repeat_circum.gr_tc_input.text()))
        b1=b
        c=str(ensure_four_digits(str(image_Controls.brightness2.value())))
        c1=c
        formatted_message = f"U\r\n{a1}{b1}00010001{c1}\r\n"
        ser = serial.Serial(
            port='/dev/ttyS0', 
            baudrate=1200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

        # Open the serial port if it's not already open
        if not ser.is_open:
            ser.open()

        # Send the formatted message
        ser.write(formatted_message.encode())

        # Close the serial port
        ser.close()

        subprocess.run("clear",shell=True,capture_output=True,text=True)
        subprocess.run("killall openbox",shell=True,capture_output=True,text=True) 
        subprocess.run("killall pigpiod",shell=True,capture_output=True,text=True) 
        #subprocess.run("killall app",shell=True,capture_output=True,text=True) 
        command = "shutdown -h now"
        # To shutdown raspberry
        subprocess.run(command, shell=True, capture_output=True, text=True)
        
def shutdown_pi_without_saving():
    subprocess.run("clear", shell=True, capture_output=True, text=True)
    subprocess.run("killall openbox",shell=True,capture_output=True,text=True)
    subprocess.run("killall pigpiod",shell=True,capture_output=True,text=True)
    #subprocess.run("killall app",shell=True,capture_output=True,text=True) 
    command = "shutdown -h now"
    # Execute save before shutdown!
    # To shutdown raspberry
    subprocess.run(command, shell=True, capture_output=True, text=True)

class Navigate_Buttons(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        font = QFont()
        font.setPointSize(16)
        font2 = QFont()
        font2.setPointSize(12)
        self.current_value = self.load_middle_value()
        self.increment_value = self.load_middle_value()
        self.total_increment = 0
        self.total_increment_right = 0
        self.btn_up = QPushButton('↑', self)
        self.btn_up.setFont(font)
        self.btn_down = QPushButton('↓', self)
        self.btn_down.setFont(font)
        self.btn_left = QPushButton('←', self)
        self.btn_right = QPushButton('→', self)
        self.btn_left.setFont(font)
        self.btn_right.setFont(font)
        self.btn_middle = QPushButton(str(self.current_value), self)
        self.btn_middle.setFont(font2)
        self.btn_up.clicked.connect(self.upButtonClicked)
        self.btn_down.clicked.connect(self.downButtonClicked)
        self.btn_left.clicked.connect(self.leftButtonClicked)
        self.btn_right.clicked.connect(self.rightButtonClicked)
        self.btn_middle.clicked.connect(self.middleButtonClicked)
        btn_size = 60
        self.btn_up.setFixedSize(btn_size, btn_size)
        self.btn_down.setFixedSize(btn_size, btn_size)
        self.btn_left.setFixedSize(btn_size, btn_size)
        self.btn_right.setFixedSize(btn_size, btn_size)
        self.btn_middle.setFixedSize(btn_size, btn_size)
        grid = QGridLayout()
        grid.addWidget(self.btn_up, 0, 0)
        grid.addWidget(self.btn_left, 1, 0)
        grid.addWidget(self.btn_middle, 1, 1)
        grid.addWidget(self.btn_down, 0, 2)
        grid.addWidget(self.btn_right, 1, 2)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(0)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(grid)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        self.setLayout(vbox)
        self.layout().setSizeConstraint(QLayout.SetFixedSize)
        self.setContentsMargins(0, 0, 0, 0)
        self.adjustSize()
        self.show()

    def load_middle_value(self):
        if os.path.exists('/home/camera1/resources/middle_value.txt'):
            with open('/home/camera1/resources/middle_value.txt', 'r') as file:
                return int(file.read())
        else:
            return 25

    def save_middle_value(self):
        with open('/home/camera1/resources/middle_value.txt', 'w') as file:
            file.write(str(self.current_value))

    def upButtonClicked(self):
        self.btn_up.setEnabled(False)
        a = str(ensure_four_digits(repeat_circum.input_field1.text()))
        a1 = a
        b = str(ensure_four_digits(repeat_circum.gr_tc_input.text()))
        b1 = b
        c=str(ensure_four_digits(str(image_Controls.brightness2.value())))
        formatted_message = f"U\r\n{a1}{b1}00010000{c}\r\n"
        ser = serial.Serial(
            port='/dev/ttyS0',
            baudrate=1200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

        if not ser.is_open:
            ser.open()

        ser.write(formatted_message.encode())
        ser.close()
        QTimer.singleShot(2000, lambda: self.btn_up.setEnabled(True))

    def downButtonClicked(self):
        self.btn_down.setEnabled(False)
        a = str(ensure_four_digits(repeat_circum.input_field1.text()))
        a1 = a
        b = str(ensure_four_digits(repeat_circum.gr_tc_input.text()))
        b1 = b
        c=str(ensure_four_digits(str(image_Controls.brightness2.value())))
        formatted_message = f"U\r\n{a1}{b1}00020000{c}\r\n"
        ser = serial.Serial(
            port='/dev/ttyS0',
            baudrate=1200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

        if not ser.is_open:
            ser.open()

        ser.write(formatted_message.encode())
        ser.close()
        QTimer.singleShot(2000, lambda: self.btn_down.setEnabled(True))

    def leftButtonClicked(self):
        self.btn_left.setEnabled(False)
        self.btn_right.setEnabled(False)
        middle_btn_value = int(self.btn_middle.text())
        time_to_sleep = 0
        if middle_btn_value == 12:
            time_to_sleep = 0.2
        elif middle_btn_value == 40:
            time_to_sleep = 0.6
        elif middle_btn_value == 75:
            time_to_sleep = 1.2

        if input_device_left.value == 0:
            if self.total_increment_right - self.increment_value >= 0:
                self.total_increment_right -= self.increment_value
            else:
                self.total_increment_right = 0

            self.btn_left.setText("←")
            QCoreApplication.processEvents()
            output_device.off()
            stepper_enable.on()
            pwm.frequency = 200
            pwm.value = 0.5

            check_interval = 0.05
            elapsed_time = 0

            while elapsed_time < time_to_sleep:
                sleep(check_interval)
                elapsed_time += check_interval

                if input_device_left.value == 1:
                    pwm.value = 0
                    stepper_enable.off()
                    self.btn_left.setText("E")
                    break
            else:
                pwm.value = 0
                stepper_enable.off()
        else:
            self.btn_left.setText("E")

        if input_device.value == 0:
            self.btn_right.setText("→")
        time_to_pause = int(time_to_sleep * 500)
        QTimer.singleShot(time_to_pause, lambda: (self.btn_left.setEnabled(True), self.btn_right.setEnabled(True)))

    def rightButtonClicked(self):
        self.btn_right.setEnabled(False)
        self.btn_left.setEnabled(False)
        middle_btn_value = int(self.btn_middle.text())
        time_to_sleep = 0
        if middle_btn_value == 12:
            time_to_sleep = 0.2
        elif middle_btn_value == 40:
            time_to_sleep = 0.6
        elif middle_btn_value == 75:
            time_to_sleep = 1.2

        try:
            if input_device.value == 0:
                self.total_increment_right += self.increment_value
                self.btn_right.setText("→")
                QCoreApplication.processEvents()
                output_device.on()
                stepper_enable.on()
                pwm.frequency = 200
                pwm.value = 0.5
                check_interval = 0.05
                elapsed_time = 0

                while elapsed_time < time_to_sleep:
                    sleep(check_interval)
                    elapsed_time += check_interval

                    if input_device.value == 1:
                        pwm.value = 0
                        stepper_enable.off()
                        self.btn_right.setText("E")
                        break
                else:
                    pwm.value = 0
                    stepper_enable.off()
            else:
                self.btn_right.setText("E")
        except KeyboardInterrupt:
            pwm.value = 0
            stepper_enable.off()

        if input_device_left.value == 0:
            self.btn_left.setText("←")
        time_to_pause = int(time_to_sleep * 500)
        QTimer.singleShot(time_to_pause, lambda: (self.btn_left.setEnabled(True), self.btn_right.setEnabled(True)))

    def right_function_with_left_ui_update(self):
        self.btn_right.setEnabled(False)
        self.btn_left.setEnabled(False)
        middle_btn_value = int(self.btn_middle.text())
        time_to_sleep = 0
        if middle_btn_value == 12:
            time_to_sleep = 0.2
        elif middle_btn_value == 40:
            time_to_sleep = 0.6
        elif middle_btn_value == 75:
            time_to_sleep = 1.2

        try:
            if input_device.value == 0:
                self.total_increment_right += self.increment_value
                self.btn_left.setText("←")
                QCoreApplication.processEvents()
                output_device.on()
                stepper_enable.on()
                pwm.frequency = 200
                pwm.value = 0.5
                check_interval = 0.05
                elapsed_time = 0

                while elapsed_time < time_to_sleep:
                    sleep(check_interval)
                    elapsed_time += check_interval

                    if input_device.value == 1:
                        pwm.value = 0
                        stepper_enable.off()
                        self.btn_left.setText("E")
                        break
                else:
                    pwm.value = 0
                    stepper_enable.off()
            else:
                self.btn_left.setText("E")
        except KeyboardInterrupt:
            pwm.value = 0
            stepper_enable.off()

        if input_device_left.value == 0:
            self.btn_right.setText("→")
        time_to_pause = int(time_to_sleep * 1000)
        QTimer.singleShot(time_to_pause, lambda: (self.btn_left.setEnabled(True), self.btn_right.setEnabled(True)))

    def left_function_with_right_ui_update(self):
        self.btn_left.setEnabled(False)
        self.btn_right.setEnabled(False)
        middle_btn_value = int(self.btn_middle.text())
        time_to_sleep = 0
        if middle_btn_value == 12:
            time_to_sleep = 0.2
        elif middle_btn_value == 40:
            time_to_sleep = 0.6
        elif middle_btn_value == 75:
            time_to_sleep = 1.2

        if input_device_left.value == 0:
            if self.total_increment_right - self.increment_value >= 0:
                self.total_increment_right -= self.increment_value
            else:
                self.total_increment_right = 0

            self.btn_right.setText("→")
            QCoreApplication.processEvents()
            output_device.off()
            stepper_enable.on()
            pwm.frequency = 200
            pwm.value = 0.5

            check_interval = 0.05
            elapsed_time = 0

            while elapsed_time < time_to_sleep:
                sleep(check_interval)
                elapsed_time += check_interval

                if input_device_left.value == 1:
                    pwm.value = 0
                    stepper_enable.off()
                    self.btn_right.setText("E")
                    break
            else:
                pwm.value = 0
                stepper_enable.off()
        else:
            self.btn_right.setText("E")

        if input_device.value == 0:
            self.btn_left.setText("←")
        time_to_pause = int(time_to_sleep * 1000)
        QTimer.singleShot(time_to_pause, lambda: (self.btn_left.setEnabled(True), self.btn_right.setEnabled(True)))

    def swap_buttons(self):
        self.btn_left.clicked.disconnect()
        self.btn_right.clicked.disconnect()
        self.btn_left.clicked.connect(self.right_function_with_left_ui_update)
        self.btn_right.clicked.connect(self.left_function_with_right_ui_update)

    def reset_buttons(self):
        self.btn_left.clicked.disconnect()
        self.btn_right.clicked.disconnect()
        self.btn_left.clicked.connect(self.leftButtonClicked)
        self.btn_right.clicked.connect(self.rightButtonClicked)

    def middleButtonClicked(self):
        if self.current_value == 12:
            self.current_value = 40
            self.increment_value = 40
        elif self.current_value == 40:
            self.current_value = 75
            self.increment_value = 75
        else:
            self.current_value = 12
            self.increment_value = 12

        self.btn_middle.setText(str(self.current_value))
        self.save_middle_value()

#Zoom Class
class ZoomDisplay(QWidget):
    updated = pyqtSignal()

    def __init__(self):
        font = QFont()
        font.setPointSize(12)
        super().__init__()
        self.setMinimumSize(201, 151)
        # _, full_img, _ = picam2.camera_controls['ScalerCrop']
        self.scale = 200 / full_img[2]
        self.zoom_level_ = 1.0
        self.max_zoom = 7.0
        self.zoom_step = 0.1
        self.zoom_button = QPushButton("ZOOM")
        self.zoom_button.setFont(font)
        self.zoom_button.setFixedHeight(30)
        self.zoom_button.clicked.connect(self.toggle_zoom_func)
        layout = QVBoxLayout()
        layout.addWidget(self.zoom_button)
        self.setLayout(layout)
        self.setContentsMargins(0,0,0,0)
    def toggle_zoom_func(self):
        if self.zoom_button.text()=="ZOOM":
            self.zoom_level=2.0
            self.setZoom
            self.zoom_button.setText("2X")
        elif self.zoom_button.text()=="2X":
            self.zoom_level=3.0
            self.setZoom
            self.zoom_button.setText("3X")
        elif self.zoom_button.text()=="3X":
            self.zoom_level=4.0
            self.setZoom
            self.zoom_button.setText("4X")
        elif self.zoom_button.text()=="4X":
            self.zoom_level=5.0
            self.setZoom
            self.zoom_button.setText("5X")
        elif self.zoom_button.text()=="5X":
            self.zoom_level=1.0
            self.setZoom
            self.zoom_button.setText("ZOOM")
    
    @property
    def zoom_level(self):
        return self.zoom_level_

    @zoom_level.setter
    def zoom_level(self, val):
        if val != self.zoom_level:
            self.zoom_level_ = val
            self.setZoom()

    def setZoomLevel(self, val):
        self.zoom_level = val

    def setZoom(self):
        global scaler_crop
        if self.zoom_level < 1:
            self.zoom_level = 1.0
        if self.zoom_level > self.max_zoom:
            self.zoom_level = self.max_zoom
        factor = 1.0 / self.zoom_level
        # _, full_img, _ = picam2.camera_controls['ScalerCrop']
        current_center = (scaler_crop[0] + scaler_crop[2] // 2, scaler_crop[1] + scaler_crop[3] // 2)
        w = int(factor * full_img[2])
        h = int(factor * full_img[3])
        x = current_center[0] - w // 2
        y = current_center[1] - h // 2
        new_scaler_crop = [x, y, w, h]
        new_scaler_crop[1] = max(new_scaler_crop[1], full_img[1])
        new_scaler_crop[1] = min(new_scaler_crop[1], full_img[1] + full_img[3] - new_scaler_crop[3])
        new_scaler_crop[0] = max(new_scaler_crop[0], full_img[0])
        new_scaler_crop[0] = min(new_scaler_crop[0], full_img[0] + full_img[2] - new_scaler_crop[2])
        scaler_crop = tuple(new_scaler_crop)
        # picam2.controls.ScalerCrop = scaler_crop
        self.update()

class Repeat_Circum(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.onboard_process = None
        self.submit_clicked = False

    def initUI(self):
        layout = QFormLayout()
        font = QFont()
        font.setPointSize(12)
        self.state_file = "/home/camera1/resources/widget_state.txt"
        self.max_temp = self._load_max()
        # Repeat Row
        self.label1 = QLabel("REPEAT:")
        self.label1.setFont(font)
        self.input_field1 = QLineEdit()
        self.input_field1.setFont(font)
        self.input_field1.setFixedWidth(55)
        self.input_field1.installEventFilter(self)

        # Checkbox
        self.checkbox = QCheckBox("CAL")
        self.checkbox.setFont(font)
        self.checkbox.stateChanged.connect(self.toggle_password_row)
        self.checkbox.stateChanged.connect(self.change_logo)
        self.current_label = QLabel("Temp Now: --°C");    
        self.current_label.setFont(font)
        self.max_label     = QLabel(f"Max Temp: {self.max_temp:.2f}°C"); 
        self.max_label.setFont(font)
        
        layout.addRow(self.checkbox)

        self.timer = QTimer()
        self.timer.timeout.connect(self._update)
        self.timer.start(1000)


        # Direction Label and Radio Buttons
        self.direction_label = QLabel("DIRECTION:")
        self.direction_label.setFont(font)
        self.radio_lr = QRadioButton("L/R")
        self.radio_rl = QRadioButton("R/L")
        self.radio_lr.setFont(font)
        self.radio_rl.setFont(font)
        self.radio_lr.toggled.connect(self.on_lr_selected)
        self.radio_rl.toggled.connect(self.on_rl_selected)
        self.direction_label.hide()
        self.radio_lr.hide()
        self.radio_rl.hide()

        direction_layout = QHBoxLayout()
        direction_layout.addWidget(self.direction_label)
        direction_layout.addWidget(self.radio_lr)
        direction_layout.addWidget(self.radio_rl)

        # Password Row (Initially Hidden)
        self.password_label = QLabel("PASSWORD:")
        self.password_label.setFont(font)
        self.password_input = QLineEdit()
        self.password_input.setFont(font)
        self.password_input.setFixedWidth(55)
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        validator = QIntValidator(400, 1500, self)
        self.input_field1.setValidator(validator)
        self.password_input.installEventFilter(self)
        self.password_button = QPushButton("AUTHORIZE")
        self.password_button.clicked.connect(self.check_password)
        self.password_label.hide()
        self.password_input.hide()
        self.password_button.hide()
        layout.addRow(self.password_label, self.password_input)
        layout.addWidget(self.password_button)
        layout.addRow(self.label1, self.input_field1)
        self.label1.hide()
        self.input_field1.hide()
        self.current_label.hide()
        self.max_label.hide()
        # GR TC Row (Initially Hidden)
        self.gr_tc_label = QLabel("GR TC:")
        self.gr_tc_label.setFont(font)
        self.gr_tc_input = QLineEdit()
        self.gr_tc_input.setFont(font)
        self.gr_tc_input.setFixedWidth(55)
        
        # Initializing components
        layout.addRow(self.gr_tc_label, self.gr_tc_input)
        layout.addWidget(self.current_label)
        layout.addWidget(self.max_label)
        layout.addRow(direction_layout)
        
        self.label = QLabel(self)

        pixmap = QPixmap("/home/camera1/resources/logo.png") 

        self.label.setPixmap(pixmap)

        self.label.resize(pixmap.width(), pixmap.height())
        layout.addRow(self.label)

        self.gr_tc_label.hide()
        self.gr_tc_input.hide()
        self.gr_tc_input.installEventFilter(self)
        self.setLayout(layout)
        self.gr_tc_input.setValidator(validator)
        self.setWindowTitle('QFormLayout Example')
        self.setGeometry(300, 300, 300, 200)
        layout.setContentsMargins(0, 0, 0, 0)
        self._update()

        

    def read_cpu_temp(self) -> float:
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


    def _load_max(self):
        if not os.path.exists(self.state_file):
            return 0.0
        lines = open(self.state_file).read().splitlines()
        if len(lines) >= 8:
            try:
                return float(lines[7])
            except:
                pass
        return 0.0

    def _save_max(self):
        # load existing lines
        lines = []
        if os.path.exists(self.state_file):
            lines = open(self.state_file).read().splitlines()
        # pad out to 8 lines
        while len(lines) < 8:
            lines.append("")
        # update line 8 (index 7)
        lines[7] = f"{self.max_temp:.2f}"
        with open(self.state_file, "w") as f:
            f.write("\n".join(lines))

    def _update(self):
        t = self.read_cpu_temp()
        if t is None:
            return
        self.current_label.setText(f"Temp Now: {t:,.2f}°C")
        if t > self.max_temp:
            self.max_temp = t
            self.max_label.setText(f"Max Temp: {t:.2f}°C")
            self._save_max()

    def validate_input_repeat(self):
        try:
            value = int(self.input_field1.text())
            if value is None:
                self.input_field1.setText("0")
        except ValueError:
            self.input_field1.setText("0")
        QCoreApplication.processEvents()

    def on_lr_selected(self):
        if self.radio_lr.isChecked():
            navigate_Buttons.reset_buttons()

    def on_rl_selected(self):
        if self.radio_rl.isChecked():
            navigate_Buttons.swap_buttons()

    def validate_input_grtc(self):
        try:
            value = int(self.gr_tc_input.text())
            if value < 1:
                self.gr_tc_input.setText("1")
            elif value > 100:
                self.gr_tc_input.setText("100")
        except ValueError:
            self.gr_tc_input.setText("0")

    def get_value_repeat(self):
        return self.input_field1.text()

    def eventFilter(self, source, event):
        if event.type() == QEvent.FocusIn and source in [self.input_field1, self.password_input, self.gr_tc_input]:
            self.open_onboard()
        return super(Repeat_Circum, self).eventFilter(source, event)

    def open_onboard(self):
        screen_geometry = QDesktopWidget().screenGeometry()
        screen_width = screen_geometry.width()
        onboard_width = 1000
        pos = self.input_field1.mapToGlobal(self.input_field1.rect().topLeft())
        x = pos.x() + 248
        y = pos.y() - 20
        size_onboard = "220x200"
        self.onboard_process = QProcess(self)
        self.onboard_process.start("onboard", ["-l", "Compact", "-x", str(x), "-y", str(y), "-s", str(size_onboard)])

    def toggle_password_row(self, state):
        if state == Qt.Checked:
            self.password_label.show()
            self.password_input.show()
            self.password_button.show()
        else:
            self.password_label.hide()
            self.password_input.hide()
            self.password_button.hide()
            self.gr_tc_label.hide()
            self.gr_tc_input.hide()
            self.label1.hide()
            self.input_field1.hide()
            self.direction_label.hide()
            self.radio_lr.hide()
            self.radio_rl.hide()
            self.password_input.setText("")
            self.current_label.hide()
            self.max_label.hide()
            if not self.submit_clicked:
                self.password_button.setEnabled(True)

    def change_logo(self):
        global i
        i += 1
        if i % 2 != 0:
            pixmap1 = QPixmap("/home/camera1/resources/logo_mini.png")
            self.label.setPixmap(pixmap1)
            self.label.resize(pixmap1.width(), pixmap1.height())
        else:
            pixmap = QPixmap("/home/camera1/resources/logo.png")
            self.label.setPixmap(pixmap)
            self.label.resize(pixmap.width(), pixmap.height())

    def check_password(self):
        password = self.password_input.text()
        if password == "1121":
            self.gr_tc_label.show()
            self.gr_tc_input.show()
            self.label1.show()
            self.input_field1.show()
            self.direction_label.show()
            self.radio_lr.show()
            self.radio_rl.show()
            self.current_label.show()
            self.max_label.show()
            self.submit_clicked = True
        else:
            self.gr_tc_label.hide()
            self.gr_tc_input.hide()
            self.direction_label.hide()
            self.radio_lr.hide()
            self.radio_rl.hide()
            self.label1.hide()
            self.input_field1.hide()
            self.current_label.hide()
            self.max_label.hide()


class Image_Controls(QWidget):
    def __init__(self):
        super().__init__()
        font = QFont()
        font.setPointSize(12)
        self.zoom_level_ = 1.0
        self.max_zoom = 7.0
        self.zoom_step = 0.1
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        self.ccm = QDoubleSpinBox()
        # self.ccm.valueChanged.connect(self.img_update)
        self.saturation = logControlSlider()
        # self.saturation.valueChanged.connect(self.img_update)
        self.saturation.setSingleStep(0.1)
        self.hflip_btn = QPushButton("HORIZONTAL FLIP")
        self.hflip_btn.setFont(font)
        self.hflip_btn.setFixedHeight(30)
        self.shutdown_btn = QPushButton("X")
        self.shutdown_btn.setFont(font)
        self.shutdown_btn.setFixedWidth(35)
        self.shutdown_btn.setFixedHeight(35)
        self.shutdown_btn.clicked.connect(shutdown_pi)
        self.hflip_btn.clicked.connect(self.toggle_function_h)
        self.vflip_btn = QPushButton("VERTICAL FLIP")
        self.vflip_btn.setFont(font)
        self.vflip_btn.setFixedHeight(30)
        self.vflip_btn.clicked.connect(self.toggle_function_v)
        self.zoom_button = QPushButton("ZOOM")
        self.zoom_button.setFont(font)
        self.zoom_button.setFixedHeight(30)
        self.zoom_button.clicked.connect(self.toggle_zoom_func)
        self.contrast = logControlSlider()
        # self.contrast.valueChanged.connect(self.img_update)
        self.contrast.setSingleStep(0.1)
        self.sharpness = logControlSlider()
        # self.sharpness.valueChanged.connect(self.img_update)
        self.sharpness.setSingleStep(0.1)
        self.brightness2 = controlSlider_2()
        self.brightness = controlSlider()
        # self.brightness.valueChanged.connect(self.img_update)   
        self.brightness.setSingleStep(0.1)
        # self.brightness2.valueChanged.connect(self.send_signal)   
        # self.brightness.sliderReleased.connect(self.send_signal)
        self.brightness2.slider.sliderReleased.connect(self.send_signal)


        self.reset_button = QPushButton("DEFAULT")
        self.reset_button.setFont(font)
        self.reset_button.setFixedHeight(30)
        # self.reset_button.clicked.connect(self.reset)
        self.reset_button.clicked.connect(save_state)
        # self.reset()
        # self.img_update()
        self.spacer_label = QLabel("")
        self.spacer_label2 = QLabel("")
        self.layout.addRow(self.spacer_label, QLabel(""))
        self.layout.addRow(self.spacer_label2, QLabel(""))
        self.layout.addRow(self.hflip_btn)
        self.layout.addRow(self.vflip_btn)
        self.layout.addRow(self.zoom_button)  
        saturation_label = QLabel("SATURATION")
        saturation_label.setFont(font)
        contrast_label = QLabel("CONTRAST")
        contrast_label.setFont(font)
        sharpness_label = QLabel("SHARPNESS")
        sharpness_label.setFont(font)
        brightness_label = QLabel("BRIGHTNESS")
        brightness_label.setFont(font)
        self.layout.addRow(brightness_label, self.brightness2)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.mvm_label = QLabel("MPM: --")
        self.mvm_label.setFont(font)
        self.layout.addRow(self.mvm_label)

        self.serial_thread = SerialListener(port=SERIAL_PORT, baudrate=9600)  # Adjust port as needed
        self.serial_thread.new_data.connect(self._update_from_serial)
        self.serial_thread.start()

    def _update_from_serial(self, data):
        self.mvm_label.setText(f"MPM: {data}")

    def toggle_function_h(self):
        if self.hflip_btn.text() == "HORIZONTAL FLIP":
            self.hflip_btn.setText("BACK TO NORMAL")
            self.on_hflip_clicked()
            self.zoom_button.setText("ZOOM")
        else:
            self.hflip_btn.setText("HORIZONTAL FLIP")
            self.on_hflip_unclicked()
            self.zoom_button.setText("ZOOM")

    def toggle_function_v(self):
        if self.vflip_btn.text() == "VERTICAL FLIP":
            self.vflip_btn.setText("BACK TO NORMAL")
            self.on_vflip_clicked()
            self.zoom_button.setText("ZOOM")
        else:
            self.vflip_btn.setText("VERTICAL FLIP")
            self.on_vflip_unclicked()
            self.zoom_button.setText("ZOOM")

    def toggle_zoom_func(self):
        if self.zoom_button.text() == "ZOOM":
            # self.zoom_level = 2.0
            # self.setZoom()
            requests.post(f"{CAMERA_IP}/zoom", json={"level": 2.0})
            self.zoom_button.setText("2X")
        elif self.zoom_button.text() == "2X":
            requests.post(f"{CAMERA_IP}/zoom", json={"level": 3.0})
            self.zoom_button.setText("3X")
        elif self.zoom_button.text() == "3X":
            requests.post(f"{CAMERA_IP}/zoom", json={"level": 4.0})
            self.zoom_button.setText("4X")
        elif self.zoom_button.text() == "4X":
            requests.post(f"{CAMERA_IP}/zoom", json={"level": 5.0})
            self.zoom_button.setText("5X")
        elif self.zoom_button.text() == "5X":
            requests.post(f"{CAMERA_IP}/zoom", json={"level": 1.0})
            self.zoom_button.setText("ZOOM")
    
    def on_hflip_clicked(self):
        global hflip
        hflip = 1
        self.hflip_btn.setEnabled(True)
        # picam2.stop()
        # preview_config = picam2.create_preview_configuration()
        # preview_config["transform"] = libcamera.Transform(hflip=hflip, vflip=vflip)
        # picam2.configure(preview_config)
        # picam2.set_controls({"FrameRate": 3})
        # picam2.start()

    def on_hflip_unclicked(self):
        global hflip
        hflip = 0
        self.hflip_btn.setEnabled(True)
        # picam2.stop()
        # preview_config = picam2.create_preview_configuration()
        # preview_config["transform"] = libcamera.Transform(hflip=hflip, vflip=vflip)
        # picam2.configure(preview_config)
        # picam2.set_controls({"FrameRate": 3})
        # picam2.start()

    def on_vflip_clicked(self):
        global vflip
        vflip = 1
        self.vflip_btn.setEnabled(True)
        # picam2.stop()
        # preview_config = picam2.create_preview_configuration()
        # preview_config["transform"] = libcamera.Transform(hflip=hflip, vflip=vflip)
        # picam2.configure(preview_config)
        # picam2.set_controls({"FrameRate": 3})
        # picam2.start()

    def on_vflip_unclicked(self):
        global vflip
        vflip = 0
        self.vflip_btn.setEnabled(True)
        # picam2.stop()
        # preview_config = picam2.create_preview_configuration()
        # preview_config["transform"] = libcamera.Transform(hflip=hflip, vflip=vflip)
        # picam2.configure(preview_config)
        # picam2.set_controls({"FrameRate": 3})
        # picam2.start()

    @property
    def img_dict(self):
        return {
            "Saturation": self.saturation.value(),
            "Contrast": self.contrast.value(),
            "Sharpness": self.sharpness.value(),
            "Brightness": self.brightness.value(),
        }

    @property
    def zoom_level(self):
        return self.zoom_level_

    @zoom_level.setter
    def zoom_level(self, val):
        if val != self.zoom_level:
            self.zoom_level_ = val
            self.setZoom()

    def setZoomLevel(self, val):
        self.zoom_level = val

    def setZoom(self):
        global scaler_crop
        if self.zoom_level < 1:
            self.zoom_level = 1.0
        if self.zoom_level > self.max_zoom:
            self.zoom_level = self.max_zoom
        factor = 1.0 / self.zoom_level
        # _, full_img, _ = picam2.camera_controls['ScalerCrop']
        current_center = (scaler_crop[0] + scaler_crop[2] // 2, scaler_crop[1] + scaler_crop[3] // 2)
        w = int(factor * full_img[2])
        h = int(factor * full_img[3])
        x = current_center[0] - w // 2
        y = current_center[1] - h // 2
        new_scaler_crop = [x, y, w, h]
        new_scaler_crop[1] = max(new_scaler_crop[1], full_img[1])
        new_scaler_crop[1] = min(new_scaler_crop[1], full_img[1] + full_img[3] - new_scaler_crop[3])
        new_scaler_crop[0] = max(new_scaler_crop[0], full_img[0])
        new_scaler_crop[0] = min(new_scaler_crop[0], full_img[0] + full_img[2] - new_scaler_crop[2])
        scaler_crop = tuple(new_scaler_crop)
        # picam2.controls.ScalerCrop = scaler_crop
        self.update()
    
    def send_signal(self):
        a=str(ensure_four_digits(repeat_circum.input_field1.text()))
        a1=a
        b=str(ensure_four_digits(repeat_circum.gr_tc_input.text()))
        b1=b
        c=str(ensure_four_digits(str(self.brightness2.value())))
        c1=c    
        formatted_message = f"U\r\n{a1}{b1}000000000100{c1}\r\n"
        ser = serial.Serial(
            port='/dev/ttyS0', 
            baudrate=1200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        if not ser.is_open:
            ser.open()
        ser.write(formatted_message.encode())
        print("sent message:", formatted_message)
        ser.close()
    
    def setValue_brightness(self, value):
        self.brightness2.setValueSlider(value)

    # Initialize the Main window with the defined widgets.




# try:
    # picam2 = Picamera2()
# except Exception:
#     pop_error()
#     sys.exit()
# picam2.post_callback = request_callback
# picam2.configure(picam2.create_preview_configuration(main={"size": (800, 600)}))
app = QApplication([])
# _, scaler_crop, _ = picam2.camera_controls['ScalerCrop']
repeat_circum = Repeat_Circum()
image_Controls= Image_Controls()
video_label = QLabel()
video_label.setMinimumSize(960, 700)
# qpicamera2 = QPicamera2(video_label, width=800, height=600)
tabs = QVBoxLayout()
# zoomDisplay = ZoomDisplay()
# zoomDisplay.setContentsMargins(0,0,0,0)
navigate_Buttons = Navigate_Buttons()
label = QLabel()
checkbox = QCheckBox("Set Overlay", checked=False)
window = QWidget()
window.setWindowTitle("Qt Picamera2 App")
label.setFixedWidth(400)
label.setAlignment(QtCore.Qt.AlignTop)
layout_h = QHBoxLayout()
layout_v = QVBoxLayout()
image_Controls.setFixedHeight(280)
# zoomDisplay.setFixedHeight(40)
# navigate_Buttons.setFixedHeight(250)
# navigate_Buttons.setFixedWidth(240)
image_Controls.setContentsMargins(0,0,0,0)
tabs.setSpacing(0)

tabs.addWidget(image_Controls)
# tabs.addWidget(zoomDisplay)
tabs.addWidget(navigate_Buttons,alignment=Qt.AlignCenter)
repeat_circum.setContentsMargins(0, 0, 0, 0)

tabs.addWidget(repeat_circum)
layout_h.addLayout(tabs)
layout_h.addWidget(video_label)

# layout_h.addWidget(video_label,4)
zoom_level = 1.0
hflip = False
vflip = False

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


def update_image(img):
    video_label.setPixmap(QPixmap.fromImage(img))

thread = VideoThread()
thread.change_pixmap_signal.connect(update_image)
thread.start()


layout_h.setContentsMargins(0,0,0,0)
window.resize(1600, 1000)
window.setLayout(layout_h)
# picam2.set_controls({"FrameRate": 3})
# picam2.start()

def turn_off_wifi_bluetooth():
    subprocess.run("sudo ifconfig wlan0 down", shell=True, capture_output=True, text=True)
    subprocess.run("sudo hciconfig hci0 down", shell=True, capture_output=True, text=True)

if __name__ == '__main__':
    # window.setWindowFlags(Qt.FramelessWindowHint)
    window.showMaximized()
    # serial_thread = SerialThread()
    # serial_thread_home = SerialThread_Home()
    serialListener = SerialListener()
    # init_node.main()
    serialListener.start()
    # serial_thread.start()
    savingThread = SavingThread()
    # savingThread.start()
    load_state()
    #turn_off_wifi_bluetooth()
    shutdown_by_pin =Shutdown_by_pin()
    shutdown_by_pin.start()
    app.exec()
    # picam2.stop()
