# Setup on Raspberry pi A

## 1. Set a permanent password on Ras A upon running it once.
```
rustdesk --password 123456
```

## 2. Open this file

``` 
sudo nano /boot/config.txt
```
### Append this line at the bottom
```
hdmi_force_hotplug=1
```

# Setup on Raspberry pi B

## 1. Paste these content in ~/.bash_profile
```
sudo X :0 &
export DISPLAY=:0
openbox-session &
rustdesk --connect (User ID) (permanent password) &
sleep 10
python auto_fullscreen.py
```



## 2. Copy files

File to copy:

[auto_fullscreen.py](https://github.com/erenYeager98/Picamera2/blob/main/appV3_with_ID/auto_fullscreen.py)

[button.png](https://github.com/erenYeager98/Picamera2/blob/main/appV3_with_ID/button.png)

copy these files and paste in /home/pi/

## 3. Install dependencies

```
sudo apt update
sudo apt install -y libjpeg-dev zlib1g-dev libfreetype6-dev libopenjp2-7-dev libtiff5-dev tk-dev python3-tk
sudo apt install -y python3-opencv libopencv-dev
sudo apt install pyautogui
```

## 4. Reboot Rasbperry B
