## Set a permanent password on Ras A upon running it once.
```
rustdesk --password 123456
```

## Open this file

``` 
sudo nano /boot/config.txt
```
### Append this line at the bottom
```
hdmi_force_hotplug=1
```

## Connect using Ras B

```
rustdesk --connect (User ID) ( permanent password ) --log-level debug
```

## If you are using openbox

```
mkdir -p ~/.config/openbox
nano ~/.config/openbox/autostart
```

