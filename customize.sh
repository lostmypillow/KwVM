#!/bin/bash
set -e

### Install required packages
apt update
apt install -y python3.12-venv virt-viewer libxcb-cursor0 libglib2.0-bin

### Create user kaowei
useradd -m -s /bin/bash kaowei
echo 'kaowei:kaowei' | chpasswd
usermod -aG sudo kaowei

### Enable auto-login
mkdir -p /etc/lightdm/lightdm.conf.d
cat <<EOT > /etc/lightdm/lightdm.conf.d/90-autologin.conf
[Seat:*]
autologin-user=kaowei
autologin-user-timeout=0
user-session=xfce
EOT

### Set setuid on remote-viewer
chmod u+s /usr/bin/remote-viewer

### Place and trust .bin file
mkdir -p /home/kaowei/Desktop
cp 高偉虛擬機.bin /home/kaowei/Desktop/
chmod +x /home/kaowei/Desktop/高偉虛擬機.bin
chown -R kaowei:kaowei /home/kaowei/Desktop

mkdir -p /home/kaowei/.config/autostart
cat <<EOF > /home/kaowei/.config/autostart/launch_app.desktop
[Desktop Entry]
Type=Application
Name=Launch App
Exec=/home/kaowei/Desktop/高偉虛擬機.bin
X-GNOME-Autostart-enabled=true
EOF



### Final ownership pass
chown -R kaowei:kaowei /home/kaowei
chmod +x /home/kaowei/.config/autostart/launch_app.desktop
chmod 755 /home/kaowei/Desktop
