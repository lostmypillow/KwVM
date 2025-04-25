#!/bin/bash
set -e

# Prevent script from running on host
if [ "$$" -eq 1 ]; then
    echo "[!] Warning: Running outside of chroot! Exiting to prevent host modification."
    exit 1
fi

# Create user and set password
useradd -m -s /bin/bash -d /home/kaowei kaowei || true
echo -e "kaowei\nkaowei" | passwd kaowei
usermod -aG sudo kaowei

# Autologin configuration for LightDM
mkdir -p /etc/lightdm
cat <<EOT >/etc/lightdm/lightdm.conf
[Seat:*]
autologin-user=kaowei
autologin-user-timeout=0
autologin-session=lightdm-xsession
greeter-hide-users=true
greeter-show-manual-login=false
EOT

# User entry for AccountsService
mkdir -p /var/lib/AccountsService/users
cat <<EOT >/var/lib/AccountsService/users/kaowei
[User]
Session=lightdm-xsession
XSession=lightdm-xsession
Icon=
SystemAccount=false
EOT

# Font fallback config for Chinese and emoji
mkdir -p /etc/fonts/conf.d
cat <<EOF_FONT >/etc/fonts/conf.d/99-noto.conf
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <alias>
    <family>sans-serif</family>
    <prefer>
      <family>Noto Sans CJK TC</family>
      <family>Noto Sans</family>
    </prefer>
  </alias>
</fontconfig>
EOF_FONT

# Disable screen blanking and DPMS
mkdir -p /etc/X11/xorg.conf.d
cat <<EOT >/etc/X11/xorg.conf.d/10-dpms.conf
Section "ServerFlags"
    Option "BlankTime" "0"
    Option "StandbyTime" "0"
    Option "SuspendTime" "0"
    Option "OffTime" "0"
EndSection

Section "Monitor"
    Identifier "Monitor0"
    Option "DPMS" "false"
EndSection

Section "ServerLayout"
    Identifier "ServerLayout0"
    Option "BlankTime" "0"
    Option "StandbyTime" "0"
    Option "SuspendTime" "0"
    Option "OffTime" "0"
EndSection
EOT

# Startup script for XFCE
echo "exec startxfce4" >/home/kaowei/.xsession
chmod +x /home/kaowei/.xsession
chown kaowei:kaowei /home/kaowei/.xsession

# Set timezone
ln -sf /usr/share/zoneinfo/Asia/Taipei /etc/localtime
echo "Asia/Taipei" >/etc/timezone

# Generate random hostname
HOSTNAME="kaowei-$(head /dev/urandom | tr -dc a-z0-9 | head -c6)"
echo "$HOSTNAME" >/etc/hostname
echo "127.0.1.1 $HOSTNAME" >>/etc/hosts

# Symlink services for proper startup
ln -sf /lib/systemd/system/lightdm.service /etc/systemd/system/display-manager.service
ln -sf /lib/systemd/system/NetworkManager.service /etc/systemd/system/dbus-org.freedesktop.NetworkManager.service

# Add hostname to bash prompt
cat <<EOF_BC >>/home/kaowei/.bashrc

# Custom prompt to show generated hostname
export PS1='\u@$HOSTNAME:\w\$ '
EOF_BC
chown kaowei:kaowei /home/kaowei/.bashrc

# Create hidden config directory
mkdir -p /home/kaowei/.kwvm
# Ensure autostart directory exists
mkdir -p /home/kaowei/.config/autostart

# Create a small autostart .desktop file
cat <<EOT > /home/kaowei/.config/autostart/fix_desktop_trust.desktop
[Desktop Entry]
Type=Application
Exec=/home/kaowei/.config/autostart/fix_desktop_trust.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Fix Desktop Trust
Comment=Automatically trust desktop launchers
EOT

# Create the actual script that will "trust" the Desktop .desktop files
cat <<'EOS' > /home/kaowei/.config/autostart/fix_desktop_trust.sh
#!/bin/bash
# Trust all .desktop files on the user's Desktop
for f in ~/Desktop/*.desktop; do
    [ -f "$f" ] || continue
    chmod +x "$f"
    if command -v gio >/dev/null 2>&1; then
        gio set -t string "$f" metadata::xfce-exe-checksum "$(sha256sum "$f" | awk '{print $1}')"
    fi
done
# Remove this script after running once
rm -- "$0"
EOS

# Make the trust script executable
chmod +x /home/kaowei/.config/autostart/fix_desktop_trust.sh

# Make sure ownership is correct
chown -R kaowei:kaowei /home/kaowei/.config/autostart

# Set permissions for launch files

chmod u+s /usr/bin/remote-viewer
chown -R kaowei:kaowei /home/kaowei
chmod +x /home/kaowei/.kwvm/高偉虛擬機.bin
chmod +x /home/kaowei/.config/autostart/launch_app.desktop
chmod +x /home/kaowei/Desktop/高偉虛擬機.desktop
chmod 755 /home/kaowei/Desktop
chown kaowei:kaowei /home/kaowei/.kwvm
