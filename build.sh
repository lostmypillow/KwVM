#!/bin/bash
set -eo pipefail
trap 'echo "[!] ERROR at line $LINENO: $BASH_COMMAND exited with status $?"' ERR


VERSION="0.1.0"
echo "KAOWEI DEBIAN BUILD SCRIPT for v$VERSION STARTING..."
### Variables
ISO_NAME="KAOWEI_DEBIAN_$VERSION"
BIN_NAME="高偉虛擬機.bin"
FULL_NAME="KAOWEI DEBIAN $VERSION"
VENV_PATH="gui/Python/venv"
BIN_OUTPUT_DIR="gui"
SKIP_BIN=false
SKIP_ISO=false
SKIP_BURN=false
echo ""
echo "[Step 0] Pre-build setup"
while [[ "$1" != "" ]]; do
  case $1 in
    --skip-bin) SKIP_BIN=true ;;
    --skip-iso) SKIP_ISO=true ;;
    --skip-burn) SKIP_BURN=true ;;
  esac
  shift
done

# Set up APT proxy to speed up live-build
APT_PROXY="http://localhost:3142"
if ! curl -s --connect-timeout 2 "$APT_PROXY" > /dev/null; then
  sudo apt install -y -qq apt-cacher-ng
fi

sudo apt update -qq -y  > /dev/null
sudo apt install -qq -y python3-venv python3-dev live-build imagemagick ccache syslinux-common syslinux-utils grub-pc-bin util-linux > /dev/null

if [ "$SKIP_BIN" = false ]; then
  echo ""
  echo "[Step 1] Build binary with pyside6-deploy"
  if [ ! -d ".venv" ]; then
    python3 -m venv .venv
  fi
  source .venv/bin/activate
  pip install --no-cache-dir -r gui/Python/requirements.txt > /dev/null

  cd gui/Python
  rm -f pysidedeploy.spec
  pyside6-deploy --init
  PATCH_ARGS="--jobs=$(nproc) --include-module=proxmoxer.backends --include-module=proxmoxer.backends.https"
  APP_TITLE="title = 高偉虛擬機"
  sed -i "/^\[nuitka\]/,/^\[/ s|^\(extra_args *= *\)|\1$PATCH_ARGS |" pysidedeploy.spec
  sed -i "/^\[app\]/,/^\[/ s|^title *= *.*|$APP_TITLE|" pysidedeploy.spec
  pyside6-deploy

  cd ../..

  BIN_PATH=$(find "$BIN_OUTPUT_DIR" -name "*.bin" | head -n 1)
  if [[ ! -f "$BIN_PATH" ]]; then
      echo "ERROR: .bin not found!"
      exit 1
  fi
  cp -f "$BIN_PATH" ./"$BIN_NAME"
else
  echo "[!] Skipping [Step 1] Build binary with pyside6-deploy"
fi

if [ "$SKIP_ISO" = false ]; then
  echo ""
  echo "[Step 2] Build custom Debian ISO with lb"
  ISO_DIR="kaowei-iso"
  rm -rf "$ISO_DIR"
  sudo lb clean
  sudo rm -rf kaowei-iso
  mkdir "$ISO_DIR"
  cd "$ISO_DIR"
  lb config \
    --iso-volume "$FULL_NAME" \
    --apt-http-proxy "$APT_PROXY" \
    --distribution bookworm \
    --cache true \
    --debian-installer none \
    --archive-areas "main contrib non-free non-free-firmware" \
    --debootstrap-options "--variant=minbase" \
    --bootappend-live "boot=live quiet splash persistence persistence-label=persistence"

  rm -f config/includes.binary/isolinux/live.cfg
  mkdir -p config/package-lists
  cat <<EOF > config/package-lists/kaowei.list.chroot
xfce4
lightdm
lightdm-gtk-greeter
xorg
virt-viewer
sudo
bash
network-manager
libglib2.0-bin
libxcb-cursor0
firmware-linux
firmware-linux-free
firmware-linux-nonfree
firmware-misc-nonfree
firmware-realtek
qt6-base-dev
qt6-gtk-platformtheme
libqt6gui6
libqt6core6
libqt6widgets6
libqt6network6
libxcb-xinerama0
libxkbcommon-x11-0
libegl1
libgl1
fonts-noto-core
fonts-noto-cjk
systemd
EOF
  mkdir -p config/includes.chroot/home/kaowei/Desktop
  mkdir -p config/includes.chroot/home/kaowei/.config/autostart
  cp -f ../"$BIN_NAME" config/includes.chroot/home/kaowei/Desktop/
  cat <<EOF > config/includes.chroot/home/kaowei/.config/autostart/launch_app.desktop
[Desktop Entry]
Type=Application
Name=Launch App
Exec=bash -c "sleep 2 && /home/kaowei/Desktop/高偉虛擬機.bin"
X-GNOME-Autostart-enabled=true
EOF
  mkdir -p config/hooks/normal
  cat <<'EOF' > config/hooks/normal/00-customize.chroot
#!/bin/bash
set -e
if [ "$$" -eq 1 ]; then
  echo "[!] Warning: Running outside of chroot! Exiting to prevent host modification."
  exit 1
fi
# Create user and set password
useradd -m -s /bin/bash -d /home/kaowei kaowei || true
echo -e "kaowei\nkaowei" | passwd kaowei
usermod -aG sudo kaowei

# Configure LightDM autologin
mkdir -p /etc/lightdm
cat <<EOT > /etc/lightdm/lightdm.conf
[Seat:*]
autologin-user=kaowei
autologin-user-timeout=0
autologin-session=lightdm-xsession
greeter-hide-users=true
greeter-show-manual-login=false
EOT

# Add AccountsService entry
mkdir -p /var/lib/AccountsService/users
cat <<EOT > /var/lib/AccountsService/users/kaowei
[User]
Session=lightdm-xsession
XSession=lightdm-xsession
Icon=
SystemAccount=false
EOT

# Font fallback config (Noto for Chinese, emoji, etc.)
mkdir -p /etc/fonts/conf.d
cat <<EOF_FONT > /etc/fonts/conf.d/99-noto.conf
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

# Disable screen blanking and power saving
mkdir -p /etc/X11/xorg.conf.d
cat <<EOT > /etc/X11/xorg.conf.d/10-dpms.conf
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

# XFCE desktop icon and wallpaper preferences
mkdir -p /home/kaowei/.config/xfce4/xfconf/xfce-perchannel-xml
cat <<EOF_X > /home/kaowei/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml
<?xml version="1.0" encoding="UTF-8"?>

<channel name="xfce4-desktop" version="1.0">
  <property name="desktop-icons" type="empty">
    <property name="file-icons" type="bool" value="true"/>
    <property name="removable-devices" type="bool" value="false"/>
    <property name="volumes" type="bool" value="false"/>
    <property name="home-icon" type="bool" value="false"/>
    <property name="trash-icon" type="bool" value="false"/>
    <property name="filesystem-icon" type="bool" value="false"/>
  </property>
</channel>
EOF_X
chown -R kaowei:kaowei /home/kaowei/.config/xfce4

# Set up .xsession for XFCE
echo "exec startxfce4" > /home/kaowei/.xsession
chmod +x /home/kaowei/.xsession
chown kaowei:kaowei /home/kaowei/.xsession

# Set timezone to Asia/Taipei
ln -sf /usr/share/zoneinfo/Asia/Taipei /etc/localtime
echo "Asia/Taipei" > /etc/timezone

# Generate random hostname at build time
HOSTNAME="kaowei-$(head /dev/urandom | tr -dc a-z0-9 | head -c6)"
echo "$HOSTNAME" > /etc/hostname
echo "127.0.1.1 $HOSTNAME" >> /etc/hosts
ln -sf /lib/systemd/system/lightdm.service /etc/systemd/system/display-manager.service
ln -sf /lib/systemd/system/NetworkManager.service /etc/systemd/system/dbus-org.freedesktop.NetworkManager.service


# Modify .bashrc to show persistent hostname
cat <<EOF_BC >> /home/kaowei/.bashrc

# Custom prompt to show generated hostname
export PS1='\u@$HOSTNAME:\w\$ '
EOF_BC
chown kaowei:kaowei /home/kaowei/.bashrc

# Fix permissions for autostart and desktop
chmod u+s /usr/bin/remote-viewer
chown -R kaowei:kaowei /home/kaowei
chmod +x /home/kaowei/Desktop/高偉虛擬機.bin
chmod +x /home/kaowei/.config/autostart/launch_app.desktop
chmod 755 /home/kaowei/Desktop
EOF

  chmod +x config/hooks/normal/00-customize.chroot
  mkdir -p config/includes.binary/isolinux
  cat <<EOF > config/includes.binary/isolinux/isolinux.cfg
UI vesamenu.c32
DEFAULT live
PROMPT 0
TIMEOUT 1
MENU TITLE Loading $FULL_NAME...
LABEL live
  menu label ^FULL_NAME
  kernel /live/vmlinuz
  append initrd=/live/initrd.img boot=live quiet splash ---
EOF

# UEFI splash image + config
  mkdir -p config/includes.binary/boot/grub
  cat <<EOF > config/includes.binary/boot/grub/grub.cfg
set timeout=1
set default=0
insmod all_video
load_video
set gfxpayload=keep
insmod png
menuentry "$FULL_NAME" {
    linux /live/vmlinuz boot=live quiet splash ---
    initrd /live/initrd.img
}
EOF
  export LB_COMPRESSION_THREADS=$(nproc)
  export LB_COMPRESSION_XZ_OPTIONS="-9e -T$(nproc)"
  sudo lb build
  ISO_FINAL_NAME="${ISO_NAME}-$(date +%Y%m%d-%H%M).iso"
  mv live-image-amd64.hybrid.iso "$ISO_FINAL_NAME"
  ISO_PATH_ABS=$(realpath "$ISO_FINAL_NAME")

  echo "[Done] Created $FULL_NAME ISO at: $ISO_FINAL_NAME"
else
  echo "[!] Skipping [Step 2] Build custom Debian ISO with lb"
  ISO_PATH_ABS=$(find . -name '*.iso' | sort | tail -n 1)
  if [ -z "$ISO_PATH_ABS" ]; then
    echo "ERROR: No existing ISO found to burn. Aborting."
    exit 1
  fi
  echo "[!] Using last built ISO: $ISO_PATH_ABS"
fi


echo "[!] Available USB devices:"
lsblk -dpno NAME,SIZE,MODEL,TRAN | grep -i "usb" || echo "No USB devices found."

echo ""
read -rp "[!] Enter the USB device (just the letter, like 'sdb', or full path '/dev/sdb'): " USER_INPUT

  # Normalize input to full path
if [[ "$USER_INPUT" =~ ^/dev/ ]]; then
  USB_DEV="$USER_INPUT"
else
  USB_DEV="/dev/$USER_INPUT"
fi

  # Validate device
if [ ! -b "$USB_DEV" ]; then
    echo "[!] Error: $USB_DEV is not a valid block device: $USB_DEV"
    exit 1
fi

  # Find and unmount partitions
PARTITIONS=$(lsblk -lnpo NAME "$USB_DEV" | tail -n +2)
if [ -n "$PARTITIONS" ]; then
    echo "[!] Checking for mounted partitions on $USB_DEV..."
    for part in $PARTITIONS; do
        mountpoint=$(lsblk -no MOUNTPOINT "$part")
        if [ -n "$mountpoint" ]; then
            echo "[!] Mounted: $part → $mountpoint"
            read -rp "[!] Do you want to unmount $part? [y/N]: " reply
            if [[ "$reply" =~ ^[Yy]$ ]]; then
                sudo umount "$part"
            else
                echo "Aborting."
                exit 1
            fi
        fi
    done
fi

if [ "$SKIP_BURN" = false ]; then
  echo ""
  echo "[Step 3] Burning ISO to USB"
  echo ""
  echo "=== Summary ==="
  echo "USB Device : $USB_DEV"
  echo "ISO File   : $ISO_PATH_ABS"
  echo ""
  read -rp "[!] Are you sure you want to write $ISO_PATH_ABS to $USB_DEV? This will erase all data on it. [y/N]: " CONFIRM

  if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
      echo "[!] Aborted by user."
      exit 1
  fi

  echo "[!] Writing ISO to USB using 'dd'..."
  sudo dd if="$ISO_PATH_ABS" of="$USB_DEV" bs=1M status=progress oflag=direct && sync

  echo "[+] ISO written to USB successfully."
else
  echo "[!] Skipping [Step 3] Burning ISO to USB"
fi

