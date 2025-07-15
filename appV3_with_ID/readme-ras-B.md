## Setup the view_script.sh
```
mkdir -p ~/stream_kiosk
nano ~/stream_kiosk/view_stream.sh
```

## Paste this content
```
#!/bin/bash

# View the incoming stream in fullscreen, borderless
while true; do
    ffplay -fflags nobuffer -flags low_delay -framedrop \
           -fs -noborder -nostats -loglevel warning \
           -analyzeduration 0 -probesize 32 \
           -an udp://0.0.0.0:1234
    sleep 1
done

```

## Make it executable
```
chmod +x ~/stream_kiosk/view_stream.sh

```

## If you are using openbox

```
mkdir -p ~/.config/openbox
nano ~/.config/openbox/autostart

```
