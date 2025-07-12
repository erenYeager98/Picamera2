# Raspberry Pi A - Screen Streamer (ffmpeg)

This Pi streams its entire display to another Raspberry Pi (Pi B) using `ffmpeg` over UDP.

##  Requirements

- Raspberry Pi OS with GUI (X11)
- `ffmpeg` installed
- Pi B's IP address

## Installation

1. **Install dependencies:**

```bash
sudo apt update
sudo apt install ffmpeg x11-utils xdotool
```
## Create the script to stream
```
mkdir -p ~/stream_kiosk
nano ~/stream_kiosk/stream_display.sh
```
## Make it executable
```
chmod +x ~/stream_kiosk/stream_display.sh

```
## Create a systemd link
```
sudo nano /etc/systemd/system/stream-display.service

```
## With this content
```
[Unit]
Description=Stream Raspberry Pi A Display to Raspberry Pi B
After=graphical.target

[Service]
ExecStart=/home/pi/stream_kiosk/stream_display.sh
Restart=always
User=pi
Environment=DISPLAY=:0

[Install]
WantedBy=default.target

```

## Start the service

```
sudo systemctl daemon-reload
sudo systemctl enable stream-display.service
sudo systemctl start stream-display.service

```

### Reboot