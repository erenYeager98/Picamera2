import subprocess
import os

def run_command(command):
    """Run a shell command."""
    subprocess.run(command, shell=True, check=True)

def append_to_file(file_path, content):
    """Append content to a file."""
    with open(file_path, 'a') as file:
        file.write(content)

def replace_file(file_path, content):
    """Replace file content."""
    with open(file_path, 'w') as file:
        file.write(content)

def remove_lines_from_file(file_path, keywords):
    """Remove lines containing any keyword from file."""
    if not os.path.exists(file_path):
        return
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if not any(keyword in line for keyword in keywords):
                file.write(line)

def restore_file(backup_path, original_path):
    """Restore a backup file to original path."""
    if os.path.exists(backup_path):
        run_command(f"sudo mv {backup_path} {original_path}")

# ✅ Function to enable hotspot
def enable_hotspot():
    try:
        run_command('sudo apt install hostapd dnsmasq -y')
        run_command('sudo systemctl stop hostapd')
        run_command('sudo systemctl stop dnsmasq')

        dhcpcd_conf = """
interface wlan0
static ip_address=192.168.0.1/24
nohook wpa_supplicant
"""
        append_to_file('/etc/dhcpcd.conf', dhcpcd_conf)

        run_command('sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig')

        dnsmasq_conf = """
interface=wlan0
dhcp-range=192.168.0.2,192.168.0.20,255.255.255.0,24h
"""
        replace_file('/etc/dnsmasq.conf', dnsmasq_conf)

        hostapd_conf = """
interface=wlan0
driver=nl80211
ssid=node
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=pass1234
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
"""
        replace_file('/etc/hostapd/hostapd.conf', hostapd_conf)

        daemon_conf = """
DAEMON_CONF="/etc/hostapd/hostapd.conf"
"""
        append_to_file('/etc/default/hostapd', daemon_conf)

        run_command('sudo systemctl unmask hostapd')
        run_command('sudo systemctl enable hostapd')
        run_command('sudo systemctl start hostapd')
        run_command('sudo systemctl enable dnsmasq')
        run_command('sudo systemctl start dnsmasq')

        print("✅ Hotspot enabled successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error enabling hotspot: {e}")

# ✅ Function to disable hotspot (revert to normal Wi-Fi)
def disable_hotspot():
    try:
        remove_lines_from_file('/etc/dhcpcd.conf', ['interface wlan0', 'static ip_address=', 'nohook wpa_supplicant'])
        restore_file('/etc/dnsmasq.conf.orig', '/etc/dnsmasq.conf')
        run_command('sudo rm -f /etc/hostapd/hostapd.conf')
        remove_lines_from_file('/etc/default/hostapd', ['DAEMON_CONF'])

        run_command('sudo systemctl stop hostapd')
        run_command('sudo systemctl disable hostapd')
        run_command('sudo systemctl stop dnsmasq')
        run_command('sudo systemctl disable dnsmasq')
        run_command('sudo systemctl restart dhcpcd')

        print("✅ Hotspot disabled. Wi-Fi station mode restored.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error disabling hotspot: {e}")

# ✅ Master controller
def master_main():
    print("""\"\"\"\n==== Hotspot Controller ====\n1. Enable Hotspot\n2. Disable Hotspot\n3. Exit\n\"\"\"""")
    choice = input("Select option: ").strip()
    if choice == '1':
        enable_hotspot()
    elif choice == '2':
        disable_hotspot()
    else:
        print("Exited.")

if __name__ == "__main__":
    master_main()
