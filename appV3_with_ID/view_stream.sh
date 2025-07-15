#!/bin/bash

# View the incoming stream in fullscreen, borderless
while true; do
    ffplay -fflags nobuffer -flags low_delay -framedrop \
           -fs -noborder -nostats -loglevel warning \
           -analyzeduration 0 -probesize 32 \
           -an udp://0.0.0.0:1234
    sleep 1
done
