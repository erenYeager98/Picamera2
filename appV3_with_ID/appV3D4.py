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
# Indicate E on the number instead of arror keys, Since while swaping key function it is not alternatng.
# Disable both left and right key to avoid multiple entries.Since l/r selection not taking multiple entries but r/l selection takes multiple entries. 
#
#!/usr/bin/python3
import subprocess
import os
import sys

import numpy as np
from gpiozero import PWMOutputDevice, DigitalOutputDevice,InputDevice
from time import sleep
import time
import serial
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal,QThread,QProcess,QEvent,QCoreApplication,QTimer
from PyQt5.QtGui import QIntValidator, QPixmap,QFont
import libcamera
from picamera2 import Picamera2
from picamera2.previews.qt import QPicamera2
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDesktopWidget,
                             QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QSlider, QSpinBox,
                             QVBoxLayout, QWidget,QGridLayout,QSizePolicy,QFileDialog,QLayout,QRadioButton)

# Define constants and variables
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

def cleanup():
    picam2.post_callback = None
def ensure_four_digits(input_string):
    digits = ''.join(filter(str.isdigit, input_string))
    
    # Check the length of the digits and add leading zeros if necessary
    if len(digits) < 4:
        digits = digits.zfill(4)
        
    return digits


class Shutdown_by_pin(QThread):
    def run(self):
        while True:
            if input_17.value == 0:
                shutdown_pi()
                time.sleep(0.1)
               

#class SerialThread_Home(QThread):
#    finished1 = pyqtSignal()

#    def run(self):
#        if input_device_left.value == 0:
#            if output_device == 0:
#                output_device.on()
#            pwm.frequency = 800
#            pwm.value = 0.5
            
#            total_sleep_time = 12
#            check_interval = 0.05  # Check every 0.05 seconds
#            elapsed_time = 0
            
#            while elapsed_time < total_sleep_time:
#                sleep(check_interval)
#                elapsed_time += check_interval
#                
#                if input_device_left.value == 1:
#                    pwm.value = 0
#                    #navigate_Buttons.set_text()
#                    #self.btn_left.setText("E")
#                    break
#            else:
#                pwm.value = 0
#        else:
#            output_device.off()
#            pwm.value = 0
#            #navigate_Buttons.set_text()            
#            #self.finished1.emit()
        
#        if(input_device.value==0):
#            self.btn_right.setText("→")

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
            zoomDisplay.zoom_button.text(),
            repeat_circum.input_field1.text(),
            # repeat_circum.input_field2.text(),
            repeat_circum.gr_tc_input.text(),
            radio_state
            # navigate_Buttons.txt_total_right_increment.text()
        ]
        if(state[3]==""):
            state[3]=="0"
        if(state[4]==""):
            state[4]=="0"
        if(state[5]==""):
            state[5]=="0"

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
                if(state[0].strip()=="1"):
                    image_Controls.hflip_btn.click()
                if(state[1].strip()=="1"):
                    image_Controls.vflip_btn.click()
                if(state[2].strip()=="2X"):
                    zoomDisplay.zoom_button.click()
                if(state[2].strip()=="3X"):
                    zoomDisplay.zoom_button.click()
                    zoomDisplay.zoom_button.click()
                if(state[2].strip()=="4X"):
                    zoomDisplay.zoom_button.click()
                    zoomDisplay.zoom_button.click()
                    zoomDisplay.zoom_button.click()
                if(state[2].strip()=="5X"):
                    zoomDisplay.zoom_button.click()
                    zoomDisplay.zoom_button.click()
                    zoomDisplay.zoom_button.click()
                    zoomDisplay.zoom_button.click()
                repeat_circum.input_field1.setText(str(state[3].strip()))
                repeat_circum.gr_tc_input.setText(str(state[4].strip()))
                if(state[5].strip()=="1"):
                    repeat_circum.radio_rl.click()
                else:
                    repeat_circum.radio_lr.click()

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
        formatted_message = f"U\r\n{a1}{b1}00000000\r\n"
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
        if box_type == float:
            self.box = QDoubleSpinBox()
        else:
            self.box = QSpinBox()

        self.valueChanged = self.box.valueChanged
        self.valueChanged.connect(lambda: self.setValue(self.value()))
        self.slider.valueChanged.connect(self.updateValue)

        # self.layout.addWidget(self.box)
        self.layout.addWidget(self.slider)

        self.precision = self.box.singleStep()
        self.slider.setSingleStep(1)

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
        formatted_message = f"U\r\n{a1}{b1}00010001\r\n"
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

# class Navigate_Buttons(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()

#     def initUI(self):
#         font = QFont()
#         font.setPointSize(16)
#         font2 =QFont()
#         font2.setPointSize(12)
#         self.current_value = self.load_middle_value()  
#         self.increment_value = self.load_middle_value()  
#         self.total_increment = 0 
#         self.total_increment_right = 0
#         self.btn_up = QPushButton('↑', self)
#         self.btn_up.setFont(font)
#         self.btn_down = QPushButton('↓', self)
#         self.btn_down.setFont(font)
#         self.btn_left = QPushButton('←', self)
#         self.btn_right = QPushButton('→', self)
#         self.btn_left.setFont(font)
#         self.btn_right.setFont(font)
#         self.btn_middle = QPushButton(str(self.current_value), self)
#         self.btn_middle.setFont(font2)
#         # self.txt_total_increment = QLineEdit(self)
#         # self.txt_total_increment.setReadOnly(True)
#         # self.txt_total_increment.setAlignment(Qt.AlignCenter)
#         # self.txt_total_increment.setFixedWidth(35)  
#         # self.txt_total_increment.setFixedHeight(30)
#         # self.txt_total_right_increment = QLineEdit(self)
# #        self.home_btn = QPushButton("H")
# #        self.home_btn.setFont(font)
#         # self.txt_total_right_increment.setReadOnly(True)
#         # self.txt_total_right_increment.setAlignment(Qt.AlignCenter)
#         # self.txt_total_right_increment.setFixedWidth(35)
#         # self.txt_total_right_increment.setFixedHeight(30)
#         # self.txt_total_increment.setFont(font2)
#         # self.txt_total_right_increment.setFont(font2)
#         self.btn_up.clicked.connect(self.upButtonClicked)
#         self.btn_down.clicked.connect(self.downButtonClicked)
#         self.btn_left.clicked.connect(self.leftButtonClicked)
#         self.btn_right.clicked.connect(self.rightButtonClicked)
#         self.btn_middle.clicked.connect(self.middleButtonClicked)
# #        self.home_btn.clicked.connect(self.trigger_home_pulses)
#         btn_size = 60
#         self.btn_up.setFixedSize(btn_size, btn_size)
#         self.btn_down.setFixedSize(btn_size, btn_size)
#         self.btn_left.setFixedSize(btn_size, btn_size)
#  #       self.home_btn.setFixedSize(btn_size, btn_size)
#         self.btn_right.setFixedSize(btn_size, btn_size)
#         # self.txt_total_increment.setFixedSize(btn_size,btn_size)
#         # self.txt_total_right_increment.setFixedSize(btn_size,btn_size)
#         self.btn_middle.setFixedSize(btn_size, btn_size)
#         grid = QGridLayout()
#         grid.addWidget(self.btn_up, 0, 0)
#         grid.addWidget(self.btn_left, 1, 0)
#         grid.addWidget(self.btn_middle, 1, 1)
#         grid.addWidget(self.btn_down, 0, 2)
#         grid.addWidget(self.btn_right, 1, 2)
#         # grid.addWidget(self.txt_total_right_increment,0,2)
# #        grid.addWidget(self.home_btn,2,0)
#         grid.setContentsMargins(0,0,0,0)
#         grid.setSpacing(0)

#         hbox = QHBoxLayout()
#         # hbox.addWidget(self.txt_total_increment)
#         hbox.setContentsMargins(0,0,0,0)
#         hbox.setSpacing(0)

#         vbox = QVBoxLayout()
#         vbox.addLayout(hbox)
#         vbox.addLayout(grid)
#         vbox.setContentsMargins(0,0,0,0)
#         vbox.setSpacing(0)
#         self.setLayout(vbox)
#         self.layout().setSizeConstraint(QLayout.SetFixedSize)
#         self.setContentsMargins(0,0,0,0)
#         self.adjustSize()
#         self.show()
        
#     def set_text(self):
#         # self.txt_total_right_increment.setText("")
#         self.total_increment_right = 0

# #    def trigger_home_pulses(self):
# #        # Start separate thread for pulse generation due to program being stuck while generating.
# #        serial_thread_home.start()

#     def load_middle_value(self):
#         if os.path.exists('/home/camera1/resources/middle_value.txt'):
#             with open('/home/camera1/resources/middle_value.txt', 'r') as file:
#                 return int(file.read())
#         else:
#             return 25

#     def save_middle_value(self):
#         with open('/home/camera1/resources/middle_value.txt', 'w') as file:
#             file.write(str(self.current_value))

#     def upButtonClicked(self):
#         self.btn_up.setEnabled(False)
#         # if(self.total_increment+self.increment_value <= int(repeat_circum.input_field1.text())):
#         #     self.total_increment += self.increment_value
#             # self.txt_total_increment.setText(str(self.total_increment))
#         a=str(ensure_four_digits(repeat_circum.input_field1.text()))
#         a1=a
#         b=str(ensure_four_digits(repeat_circum.gr_tc_input.text()))
#         b1=b
#         formatted_message = f"U\r\n{a1}{b1}00010000\r\n"
#         ser = serial.Serial(
#             port='/dev/ttyS0', 
#             baudrate=1200,
#             parity=serial.PARITY_NONE,
#             stopbits=serial.STOPBITS_ONE,
#             bytesize=serial.EIGHTBITS,
#             timeout=1
#         )

#         # Open the serial port if it's not already open
#         if not ser.is_open:
#             ser.open()

#         # Send the formatted message
#         ser.write(formatted_message.encode())

#         # Close the serial port
#         ser.close()
#         QTimer.singleShot(2000, lambda: self.btn_up.setEnabled(True))

#     def downButtonClicked(self):
#         self.btn_down.setEnabled(False)
#         # if self.total_increment - self.increment_value >= 0:
#         #     self.total_increment -= self.increment_value
#         # else:
#         #     self.total_increment = 0
#         a=str(ensure_four_digits(repeat_circum.input_field1.text()))
#         a1=a
#         b=str(ensure_four_digits(repeat_circum.gr_tc_input.text()))
#         b1=b
#         formatted_message = f"U\r\n{a1}{b1}00010000\r\n"
#         ser = serial.Serial(
#             port='/dev/ttyS0', 
#             baudrate=1200,
#             parity=serial.PARITY_NONE,
#             stopbits=serial.STOPBITS_ONE,
#             bytesize=serial.EIGHTBITS,
#             timeout=1
#         )

#         # Open the serial port if it's not already open
#         if not ser.is_open:
#             ser.open()

#         # Send the formatted message
#         ser.write(formatted_message.encode())

#         # Close the serial port
#         ser.close()
#         QTimer.singleShot(2000, lambda: self.btn_down.setEnabled(True))

#         # self.txt_total_increment.setText(str(self.total_increment))

#     def leftButtonClicked(self):
#         self.btn_left.setEnabled(False)
#         self.btn_right.setEnabled(False)
#         print("left function")
#         middle_btn_value = int(self.btn_middle.text())
#         time_to_sleep = 0
#         if middle_btn_value == 12:
#             time_to_sleep = 0.2
#         elif middle_btn_value == 40:
#             time_to_sleep = 0.6
#         elif middle_btn_value == 75:
#             time_to_sleep = 1.2
        
#         # if(self.txt_total_right_increment.text()==""):
#         #     self.total_increment_right = 0
#         # else:
#         #     self.total_increment_right = int(self.txt_total_right_increment.text())
#         if input_device_left.value == 0:
#             if self.total_increment_right - self.increment_value >= 0:
#                 self.total_increment_right -= self.increment_value
#             else:
#                 self.total_increment_right = 0
            
#             # Set the text field before triggering the PWM pulses
#             # self.txt_total_right_increment.setText(str(self.total_increment_right))
#             self.btn_left.setText("←")
#             QCoreApplication.processEvents()
#             output_device.off()
#             stepper_enable.on() 
#             pwm.frequency = 200
#             pwm.value = 0.5  
            
#             check_interval = 0.05  # Check every 0.05 seconds
#             elapsed_time = 0
            
#             while elapsed_time < time_to_sleep:
#                 sleep(check_interval)
#                 elapsed_time += check_interval
                
#                 if input_device_left.value == 1:
#                     pwm.value = 0
#                     stepper_enable.off()
#                     self.btn_left.setText("E")
#                     break
#             else:
#                 pwm.value = 0
#                 stepper_enable.off()
#         else:
#             self.btn_left.setText("E")
        
#         if(input_device.value==0):
#             self.btn_right.setText("→")
#         time_to_pause=int(time_to_sleep*1000)
#         QTimer.singleShot(time_to_pause, lambda: (self.btn_left.setEnabled(True),self.btn_right.setEnabled(True)))

#     def leftButtonClicked_but_its_right_now(self):
#         self.btn_left.setEnabled(False)
#         self.btn_right.setEnabled(False)
#         print("left function")
#         middle_btn_value = int(self.btn_middle.text())
#         time_to_sleep = 0
#         if middle_btn_value == 12:
#             time_to_sleep = 0.2
#         elif middle_btn_value == 40:
#             time_to_sleep = 0.6
#         elif middle_btn_value == 75:
#             time_to_sleep = 1.2
        
#         # if(self.txt_total_right_increment.text()==""):
#         #     self.total_increment_right = 0
#         # else:
#         #     self.total_increment_right = int(self.txt_total_right_increment.text())
#         if input_device_left.value == 0:
#             if self.total_increment_right - self.increment_value >= 0:
#                 self.total_increment_right -= self.increment_value
#             else:
#                 self.total_increment_right = 0
            
#             # Set the text field before triggering the PWM pulses
#             # self.txt_total_right_increment.setText(str(self.total_increment_right))
#             self.btn_right.setText("→")
#             QCoreApplication.processEvents()
#             output_device.off()
#             stepper_enable.on() 
#             pwm.frequency = 200
#             pwm.value = 0.5  
            
#             check_interval = 0.05  # Check every 0.05 seconds
#             elapsed_time = 0
            
#             while elapsed_time < time_to_sleep:
#                 sleep(check_interval)
#                 elapsed_time += check_interval
                
#                 if input_device_left.value == 1:
#                     pwm.value = 0
#                     stepper_enable.off()
#                     self.btn_right.setText("E")
#                     break
#             else:
#                 pwm.value = 0
#                 stepper_enable.off()
#         else:
#             self.btn_right.setText("E")
        
#         if(input_device.value==0):
#             self.btn_right.setText("→")
#         time_to_pause=int(time_to_sleep*1000)
#         QTimer.singleShot(time_to_pause, lambda: (self.btn_left.setEnabled(True),self.btn_right.setEnabled(True)))

    

#     def rightButtonClicked(self):
#         self.btn_right.setEnabled(False)
#         self.btn_left.setEnabled(False)
#         print("right function")
#         middle_btn_value = int(self.btn_middle.text())
#         time_to_sleep =0
#         if (middle_btn_value==12):
#             time_to_sleep = 0.2
#         elif (middle_btn_value==40):
#             time_to_sleep = 0.6
#         elif (middle_btn_value==75):
#             time_to_sleep = 1.2
#         # if(self.txt_total_right_increment.text()==""):
#         #     self.total_increment_right = 0
#         # else:
#         #     self.total_increment_right = int(self.txt_total_right_increment.text())


#         try:
#             if input_device.value == 0:
#                 self.total_increment_right += self.increment_value
#                 # self.txt_total_right_increment.setText(str(self.total_increment_right))
#                 self.btn_right.setText("→")
#                 QCoreApplication.processEvents()
#                 output_device.on()
#                 stepper_enable.on()
#                 pwm.frequency = 200
#                 pwm.value = 0.5
#                 check_interval = 0.05  # Check every 0.05 seconds
#                 elapsed_time = 0

#                 while elapsed_time < time_to_sleep:
#                     sleep(check_interval)
#                     elapsed_time += check_interval

#                     if input_device.value == 1:
#                         pwm.value = 0
#                         stepper_enable.off()
#                         self.btn_right.setText("E")
#                         break
#                 else:
#                     pwm.value = 0
#                     stepper_enable.off() 
#             else:
#                 self.btn_right.setText("E")
#         except KeyboardInterrupt:
#             pwm.value = 0
#             stepper_enable.off()

#         if(input_device_left.value==0):
#             self.btn_left.setText("←")
#         time_to_pause=int(time_to_sleep*1000)
#         QTimer.singleShot(time_to_pause, lambda: (self.btn_left.setEnabled(True), self.btn_right.setEnabled(True)))

   
#     def swap_buttons(self):
#         self.btn_left.clicked.disconnect()
#         self.btn_right.clicked.disconnect()
#         self.btn_left.clicked.connect(self.rightButtonClicked)
#         self.btn_right.clicked.connect(self.leftButtonClicked_but_its_right_now)

#     def reset_buttons(self):
#         self.btn_left.clicked.disconnect()
#         self.btn_right.clicked.disconnect()
#         self.btn_left.clicked.connect(self.leftButtonClicked)
#         self.btn_right.clicked.connect(self.rightButtonClicked)
            
    
#     def middleButtonClicked(self):
#         # Program to toggle between middle values
#         if self.current_value == 12:
#             self.current_value = 40
#             self.increment_value = 40
#         elif self.current_value == 40:
#             self.current_value = 75
#             self.increment_value = 75
#         else:
#             self.current_value = 12
#             self.increment_value = 12
            
#         self.btn_middle.setText(str(self.current_value))

#         # Save the current value to file
#         self.save_middle_value()

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
        formatted_message = f"U\r\n{a1}{b1}00010000\r\n"
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
        formatted_message = f"U\r\n{a1}{b1}00010000\r\n"
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
        time_to_pause = int(time_to_sleep * 1000)
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
        time_to_pause = int(time_to_sleep * 1000)
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
        _, full_img, _ = picam2.camera_controls['ScalerCrop']
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
        _, full_img, _ = picam2.camera_controls['ScalerCrop']
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
        picam2.controls.ScalerCrop = scaler_crop
        self.update()

# class Repeat_Circum(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()
#         self.onboard_process = None
#         self.submit_clicked = False

#     def initUI(self):
#         layout = QFormLayout()
#         font = QFont()
#         font.setPointSize(12)
#         # Repeat Row
#         self.label1 = QLabel("REPEAT:")
#         self.label1.setFont(font)
#         self.input_field1 = QLineEdit()
#         self.input_field1.setFont(font)
#         self.input_field1.setFixedWidth(55)
#         self.input_field1.installEventFilter(self)
#         # self.input_field1.editingFinished.connect(self.validate_input_repeat)

#         # Circum Row
#         # label2 = QLabel("CIRCUM:")
#         # label2.setFont(font)
#         # self.input_field2 = QLineEdit()
#         # self.input_field2.setFont(font)
#         # self.input_field2.setFixedWidth(55)
#         # layout.addRow(label2, self.input_field2)
#         # self.input_field2.installEventFilter(self)
#         # self.input_field2.editingFinished.connect(self.validate_input_circum)


#         # Checkbox
#         self.checkbox = QCheckBox("CAL")
#         self.checkbox.setFont(font)
#         self.checkbox.stateChanged.connect(self.toggle_password_row)
#         self.checkbox.stateChanged.connect(self.change_logo)
#         layout.addRow(self.checkbox)

#         self.radio_lr = QRadioButton("L/R")
#         self.radio_rl = QRadioButton("R/L")
#         self.radio_lr.setFont(font)
#         self.radio_rl.setFont(font)
#         self.radio_lr.toggled.connect(self.on_lr_selected)
#         self.radio_rl.toggled.connect(self.on_rl_selected)
#         self.radio_lr.hide()
#         self.radio_rl.hide()


#         # Password Row (Initially Hidden)
#         self.password_label = QLabel("PASSWORD:")
#         self.password_label.setFont(font)
#         self.password_input = QLineEdit()
#         self.password_input.setFont(font)
#         self.password_input.setFixedWidth(55)
#         self.password_input.setPlaceholderText("Enter Password")
#         self.password_input.setEchoMode(QLineEdit.Password)
#         validator = QIntValidator(400, 1500, self)
#         self.input_field1.setValidator(validator)
#         self.password_input.installEventFilter(self)
#         # self.input_field2.setValidator(validator)
#         self.password_button = QPushButton("AUTHORIZE")
#         self.password_button.clicked.connect(self.check_password)
#         self.password_label.hide()
#         self.password_input.hide()
#         self.password_button.hide()
#         layout.addRow(self.password_label, self.password_input)
#         layout.addWidget(self.password_button)
#         layout.addRow(self.label1, self.input_field1)
#         self.label1.hide()
#         self.input_field1.hide()

#         # GR TC Row (Initially Hidden)
#         self.gr_tc_label = QLabel("GR TC:")
#         self.gr_tc_label.setFont(font)
#         self.gr_tc_input = QLineEdit()
#         self.gr_tc_input.setFont(font)
#         self.gr_tc_input.setFixedWidth(55)
        
#         # Initializing components
#         layout.addRow(self.gr_tc_label, self.gr_tc_input)
#         layout.addRow(self.radio_lr,self.radio_rl)
#          # Create a QLabel widget
#         self.label = QLabel(self)

#         # Load the image using QPixmap
#         pixmap = QPixmap("/home/camera1/resources/logo.png")  # Update this with your image path

#         # Set the QPixmap to the QLabel
#         self.label.setPixmap(pixmap)

#         # Optionally, adjust the size of the QLabel to the size of the image
#         self.label.resize(pixmap.width(), pixmap.height())
#         layout.addRow(self.label)

#         self.gr_tc_label.hide()
#         self.gr_tc_input.hide()
#         self.gr_tc_input.installEventFilter(self)
#         self.setLayout(layout)
#         self.gr_tc_input.setValidator(validator)
#         self.setWindowTitle('QFormLayout Example')
#         self.setGeometry(300, 300, 300, 200)
#         layout.setContentsMargins(0, 0, 0, 0)


#     def validate_input_repeat(self):
#         try:
#             value = int(self.input_field1.text())

#             if(value==None):
#                 self.input_field1.setText("0")

#         except ValueError:
#             self.input_field1.setText("0")

#         QCoreApplication.processEvents()

#     # def validate_input_circum(self):
#     #     try:
#     #         value = int(self.input_field2.text())
#     #         if value < 100:
#     #             self.input_field2.setText("100")
#     #         elif value > 1500:
#     #             self.input_field2.setText("1500")
#     #     except ValueError:
#     #         self.input_field2.setText("0")


#     def on_lr_selected(self):
#         if self.radio_lr.isChecked():
#             navigate_Buttons.reset_buttons()

#     def on_rl_selected(self):
#         if self.radio_rl.isChecked():
#             navigate_Buttons.swap_buttons()


#     def validate_input_grtc(self):
#         try:
#             value = int(self.gr_tc_input.text())
#             if value < 1:
#                 self.gr_tc_input.setText("1")
#             elif value > 100:
#                 self.gr_tc_input.setText("100")
#         except ValueError:
#             self.gr_tc_input.setText("0")

#     def get_value_repeat(self):
#         return self.input_field1.text()

#     # def get_value_circum(self):
#     #     return self.input_field2.text()

#     def eventFilter(self, source, event):
#         if event.type() == QEvent.FocusIn and source in [self.input_field1,self.password_input,self.gr_tc_input]:
#             self.open_onboard()
#         return super(Repeat_Circum, self).eventFilter(source, event)
#     def open_onboard(self):
#         # Close any existing instance of Onboard
#         # if self.onboard_process is not None:
#         #     self.onboard_process.terminate()
#         #     self.onboard_process.waitForFinished()
#         screen_geometry = QDesktopWidget().screenGeometry()
#         screen_width = screen_geometry.width()
#         onboard_width = 1000  
#         pos = self.input_field1.mapToGlobal(self.input_field1.rect().topLeft())

#         # Onboard geometry parameters
#         x = pos.x() + 248
#         y = pos.y() - 20
#         size_onboard = "220x200"
#         # x_pos = screen_width - onboard_width
#         # y_pos = 400 # previous Configuration
        
#         # Open Onboard with the specified layout and position
#         self.onboard_process = QProcess(self)
#         self.onboard_process.start("onboard", ["-l", "Compact", "-x", str(x), "-y", str(y), "-s", str(size_onboard)])
#     def toggle_password_row(self, state):
#         if state == Qt.Checked:
#             self.password_label.show()
#             self.password_input.show()
#             self.password_button.show()
#         else:
#             self.password_label.hide()
#             self.password_input.hide()
#             self.password_button.hide()
#             self.gr_tc_label.hide()
#             self.gr_tc_input.hide()
#             self.label1.hide()
#             self.input_field1.hide()
#             self.radio_lr.hide()
#             self.radio_rl.hide()
#             self.password_input.setText("")
#             if not self.submit_clicked:
#                 self.password_button.setEnabled(True)
#     def change_logo(self):
#         global i
#         i+=1
#         if(i%2!=0):
#             pixmap1 = QPixmap("/home/camera1/resources/logo_mini.png")
#             self.label.setPixmap(pixmap1)
#             self.label.resize(pixmap1.width(), pixmap1.height())
#         else:
#             pixmap = QPixmap("/home/camera1/resources/logo.png")
#             self.label.setPixmap(pixmap)
#             self.label.resize(pixmap.width(),pixmap.height())

#     def check_password(self):
#         password = self.password_input.text()
#         if password == "1121":
#             self.gr_tc_label.show()
#             self.gr_tc_input.show()
#             self.label1.show()
#             self.input_field1.show()
#             self.radio_lr.show()
#             self.radio_rl.show()

#             self.submit_clicked = True
#         else:
#             self.gr_tc_label.hide()
#             self.gr_tc_input.hide()
#             self.radio_lr.hide()
#             self.radio_rl.hide()
#             self.label1.hide()
#             self.input_field1.hide()
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
        layout.addRow(self.checkbox)

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

        # GR TC Row (Initially Hidden)
        self.gr_tc_label = QLabel("GR TC:")
        self.gr_tc_label.setFont(font)
        self.gr_tc_input = QLineEdit()
        self.gr_tc_input.setFont(font)
        self.gr_tc_input.setFixedWidth(55)
        
        # Initializing components
        layout.addRow(self.gr_tc_label, self.gr_tc_input)
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
            self.submit_clicked = True
        else:
            self.gr_tc_label.hide()
            self.gr_tc_input.hide()
            self.direction_label.hide()
            self.radio_lr.hide()
            self.radio_rl.hide()
            self.label1.hide()
            self.input_field1.hide()

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
        self.ccm.valueChanged.connect(self.img_update)
        self.saturation = logControlSlider()
        self.saturation.valueChanged.connect(self.img_update)
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
        self.contrast.valueChanged.connect(self.img_update)
        self.contrast.setSingleStep(0.1)
        self.sharpness = logControlSlider()
        self.sharpness.valueChanged.connect(self.img_update)
        self.sharpness.setSingleStep(0.1)
        self.brightness = controlSlider()
        self.brightness.setSingleStep(0.1)
        self.brightness.valueChanged.connect(self.img_update)
        self.reset_button = QPushButton("DEFAULT")
        self.reset_button.setFont(font)
        self.reset_button.setFixedHeight(30)
        self.reset_button.clicked.connect(self.reset)
        self.reset_button.clicked.connect(save_state)
        self.reset()
        self.img_update()
        self.spacer_label = QLabel("")
        self.spacer_label2 = QLabel("")
        self.layout.addRow(self.spacer_label, QLabel(""))
        self.layout.addRow(self.spacer_label2, QLabel(""))
        self.layout.addRow(self.hflip_btn)
        self.layout.addRow(self.vflip_btn)
        self.layout.addRow(self.zoom_button)  # Add zoom button here
        saturation_label = QLabel("SATURATION")
        saturation_label.setFont(font)
        contrast_label = QLabel("CONTRAST")
        contrast_label.setFont(font)
        sharpness_label = QLabel("SHARPNESS")
        sharpness_label.setFont(font)
        brightness_label = QLabel("BRIGHTNESS")
        brightness_label.setFont(font)
        self.layout.setContentsMargins(0, 0, 0, 0)

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
            self.zoom_level = 2.0
            self.setZoom()
            self.zoom_button.setText("2X")
        elif self.zoom_button.text() == "2X":
            self.zoom_level = 3.0
            self.setZoom()
            self.zoom_button.setText("3X")
        elif self.zoom_button.text() == "3X":
            self.zoom_level = 4.0
            self.setZoom()
            self.zoom_button.setText("4X")
        elif self.zoom_button.text() == "4X":
            self.zoom_level = 5.0
            self.setZoom()
            self.zoom_button.setText("5X")
        elif self.zoom_button.text() == "5X":
            self.zoom_level = 1.0
            self.setZoom()
            self.zoom_button.setText("ZOOM")

    def on_hflip_clicked(self):
        global hflip
        hflip = 1
        self.hflip_btn.setEnabled(True)
        picam2.stop()
        preview_config = picam2.create_preview_configuration()
        preview_config["transform"] = libcamera.Transform(hflip=hflip, vflip=vflip)
        picam2.configure(preview_config)
        picam2.set_controls({"FrameRate": 3})
        picam2.start()

    def on_hflip_unclicked(self):
        global hflip
        hflip = 0
        self.hflip_btn.setEnabled(True)
        picam2.stop()
        preview_config = picam2.create_preview_configuration()
        preview_config["transform"] = libcamera.Transform(hflip=hflip, vflip=vflip)
        picam2.configure(preview_config)
        picam2.set_controls({"FrameRate": 3})
        picam2.start()

    def on_vflip_clicked(self):
        global vflip
        vflip = 1
        self.vflip_btn.setEnabled(True)
        picam2.stop()
        preview_config = picam2.create_preview_configuration()
        preview_config["transform"] = libcamera.Transform(hflip=hflip, vflip=vflip)
        picam2.configure(preview_config)
        picam2.set_controls({"FrameRate": 3})
        picam2.start()

    def on_vflip_unclicked(self):
        global vflip
        vflip = 0
        self.vflip_btn.setEnabled(True)
        picam2.stop()
        preview_config = picam2.create_preview_configuration()
        preview_config["transform"] = libcamera.Transform(hflip=hflip, vflip=vflip)
        picam2.configure(preview_config)
        picam2.set_controls({"FrameRate": 3})
        picam2.start()

    @property
    def img_dict(self):
        return {
            "Saturation": self.saturation.value(),
            "Contrast": self.contrast.value(),
            "Sharpness": self.sharpness.value(),
            "Brightness": self.brightness.value(),
        }

    def reset(self):
        self.saturation.setValue(picam2.camera_controls["Saturation"][2], emit=True)
        self.contrast.setValue(picam2.camera_controls["Contrast"][2], emit=True)
        self.sharpness.setValue(picam2.camera_controls["Sharpness"][2], emit=True)
        self.brightness.setValue(picam2.camera_controls["Brightness"][2], emit=True)

    def img_update(self):
        self.saturation.setMinimum(picam2.camera_controls["Saturation"][0])
        self.saturation.setMaximum(6.0)
        self.contrast.setMinimum(picam2.camera_controls["Contrast"][0])
        self.contrast.setMaximum(6.0)
        self.sharpness.setMinimum(picam2.camera_controls["Sharpness"][0])
        self.sharpness.setMaximum(picam2.camera_controls["Sharpness"][1])
        self.brightness.setMinimum(picam2.camera_controls["Brightness"][0])
        self.brightness.setMaximum(picam2.camera_controls["Brightness"][1])
        picam2.set_controls(self.img_dict)

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
        _, full_img, _ = picam2.camera_controls['ScalerCrop']
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
        picam2.controls.ScalerCrop = scaler_crop
        self.update()

# Initialize the Main window with the defined widgets.
try:
    picam2 = Picamera2()
except Exception:
    pop_error()
    sys.exit()
picam2.post_callback = request_callback
picam2.configure(picam2.create_preview_configuration(main={"size": (800, 600)}))
app = QApplication([])
_, scaler_crop, _ = picam2.camera_controls['ScalerCrop']
image_Controls= Image_Controls()
qpicamera2 = QPicamera2(picam2, width=800, height=600)
tabs = QVBoxLayout()
# zoomDisplay = ZoomDisplay()
# zoomDisplay.setContentsMargins(0,0,0,0)
navigate_Buttons = Navigate_Buttons()
repeat_circum = Repeat_Circum()
label = QLabel()
checkbox = QCheckBox("Set Overlay", checked=False)
window = QWidget()
#window.setWindowTitle("Qt Picamera2 App")
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
layout_h.addLayout(tabs,15)
layout_h.addWidget(qpicamera2, 80)
layout_h.setContentsMargins(0,0,0,0)
window.resize(1600, 1000)
window.setLayout(layout_h)
picam2.start()

def turn_off_wifi_bluetooth():
    subprocess.run("sudo ifconfig wlan0 down", shell=True, capture_output=True, text=True)
    subprocess.run("sudo hciconfig hci0 down", shell=True, capture_output=True, text=True)

if __name__ == '__main__':
    window.setWindowFlags(Qt.FramelessWindowHint)
    window.showMaximized()
    # serial_thread = SerialThread()
    # serial_thread_home = SerialThread_Home()
    # serial_thread.start()
    savingThread = SavingThread()
    # savingThread.start()
    load_state()
    #turn_off_wifi_bluetooth()
    shutdown_by_pin =Shutdown_by_pin()
    shutdown_by_pin.start()
    app.exec()
    picam2.stop()