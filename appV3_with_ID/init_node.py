import os

# Configuration variables (can be overridden before calling)
SSID = "node"
PASSWORD = "pass1234"
INTERFACE = "wlan0"
IP_RANGE = "192.168.50.10,192.168.50.50,255.255.255.0,24h"
GATEWAY_IP = "192.168.50.1/24"
CHANNEL = "7"

def write_config_files():
    hostapd_conf = f"""
interface={INTERFACE}
driver=nl80211
ssid={SSID}
ignore_broadcast_ssid=1
hw_mode=g
channel={CHANNEL}
wmm_enabled=0
macaddr_acl=0
auth_algs=1
wpa=2
wpa_passphrase={PASSWORD}
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
"""

    dnsmasq_conf = f"""
interface={INTERFACE}
dhcp-range={IP_RANGE}
"""

    with open("/etc/hostapd/hostapd.conf", "w") as f:
        f.write(hostapd_conf.strip())

    with open("/etc/dnsmasq.conf", "w") as f:
        f.write(dnsmasq_conf.strip())

    with open("/etc/default/hostapd", "w") as f:
        f.write(f'DAEMON_CONF="/etc/hostapd/hostapd.conf"\n')

def configure_network():
    os.system(f"nmcli device set {INTERFACE} managed no")
    os.system(f"sudo ip link set {INTERFACE} down")
    os.system(f"sudo ip addr flush dev {INTERFACE}")
    os.system(f"sudo ip addr add {GATEWAY_IP} dev {INTERFACE}")
    os.system(f"sudo ip link set {INTERFACE} up")

def start_hotspot():
    write_config_files()
    configure_network()
    os.system("sudo systemctl restart dnsmasq")
    os.system("sudo systemctl restart hostapd")
    print(f"✅ Hotspot '{SSID}' started on {INTERFACE} (hidden SSID).")

def stop_hotspot():
    os.system("sudo systemctl stop hostapd")
    os.system("sudo systemctl stop dnsmasq")
    os.system(f"nmcli device set {INTERFACE} managed yes")
    print(f"🛑 Hotspot on {INTERFACE} stopped and restored to default.")

