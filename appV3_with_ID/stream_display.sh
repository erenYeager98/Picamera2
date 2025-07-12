#!/bin/bash

# IP address of Raspberry Pi B
TARGET_IP="192.168.0.1"

# Automatically detect the screen resolution
RESOLUTION=$(xdpyinfo | grep dimensions | awk '{print $2}')

# Start streaming the display using ffmpeg
ffmpeg -f x11grab -r 25 -s "$RESOLUTION" -i :0.0 \
       -vcodec libx264 -preset ultrafast -tune zerolatency \
       -f mpegts udp://$TARGET_IP:1234
