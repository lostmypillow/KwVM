#!/bin/bash
set -e

### Step 0: Variables
ISO_NAME="kaowei_debian_0.0.8"
BIN_NAME="高偉虛擬機.bin"
VENV_PATH="gui/Python/venv"
BIN_OUTPUT_DIR="gui"

echo "[Step 1] Install required packages"
sudo apt update -y
sudo apt install -y python3-venv live-build imagemagick ccache

echo "[Step 2] Set up Python venv and install dependencies"
cd gui/Python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo "[Step 3] Generate pysidedeploy.spec"
rm -f pysidedeploy.spec
pyside6-deploy --init

echo "[Step 4] Patch pysidedeploy.spec with extra Nuitka args"
PATCH_ARGS="--show-progress --show-scons --show-memory --include-module=proxmoxer.backends --include-module=proxmoxer.backends.https"

if ! grep -qF "$PATCH_ARGS" pysidedeploy.spec; then
  sed -i "/^\[nuitka\]/,/^\[/ s|^\(extra_args *= *\)|\1$PATCH_ARGS |" pysidedeploy.spec
  echo "→ Added extra Nuitka args to pysidedeploy.spec"
else
  echo "→ Nuitka args already present. Skipping patch."
fi

echo "[Step 5] Build .bin file with pyside6-deploy"
pyside6-deploy

cd ../../..

# Find the .bin
BIN_PATH=$(find "$BIN_OUTPUT_DIR" -name "*.bin" | head -n 1)
if [[ ! -f "$BIN_PATH" ]]; then
    echo "ERROR: .bin not found!"
    exit 1
fi
cp "$BIN_PATH" ./"$BIN_NAME"

echo "[Step 6] Start building ISO structure"
ISO_DIR="kaowei-iso"
rm -rf "$ISO_DIR"
mkdir "$ISO_DIR"
cd "$ISO_DIR"

echo "[Step 7] Configure live-build"
lb config \
  --distribution bookworm \
  --debian-installer live \
  --archive-areas "main contrib non-free" \
  --debootstrap-options "--variant=minbase"

echo "[Step 8] Add required packages"
mkdir -p config/package-lists
cat <<EOF > config/package-lists/kaowei.list.chroot
xorg
lightdm
lightdm-gtk-greeter
openbox
lxsession
libglib2.0-bin
libxcb-cursor0
remote-viewer
sudo
EOF

echo "[Step 9] Copy .bin and autostart"
mkdir -p config/includes.chroot/home/kaowei/Desktop
mkdir -p config/includes.chroot/home/kaowei/.config/autostart

cp ../"$BIN_NAME" config/includes.chroot/home/kaowei/Desktop/

cat <<EOF > config/includes.chroot/home/kaowei/.config/autostart/launch_app.desktop
[Desktop Entry]
Type=Application
Name=Launch App
Exec=/home/kaowei/Desktop/$BIN_NAME
X-GNOME-Autostart-enabled=true
EOF

echo "[Step 10] Add customization hook"
mkdir -p config/hooks/normal
cat <<'EOF' > config/hooks/normal/00-customize.chroot
#!/bin/bash
set -e

# Create user
useradd -m -s /bin/bash kaowei
echo 'kaowei:kaowei' | chpasswd
usermod -aG sudo kaowei

# Autologin via LightDM
mkdir -p /etc/lightdm/lightdm.conf.d
cat <<EOT > /etc/lightdm/lightdm.conf.d/90-autologin.conf
[Seat:*]
autologin-user=kaowei
autologin-user-timeout=0
user-session=openbox
EOT

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

echo -e "setterm -blank 0 -powerdown 0 -powersave off\n" >> /etc/rc.local
chmod +x /etc/rc.local

# Fix permissions
chmod u+s /usr/bin/remote-viewer
chown -R kaowei:kaowei /home/kaowei
chmod +x /home/kaowei/Desktop/$BIN_NAME
chmod +x /home/kaowei/.config/autostart/launch_app.desktop
chmod 755 /home/kaowei/Desktop
EOF

chmod +x config/hooks/normal/00-customize.chroot

echo "[Step 11] Set ISO name, splash, and boot config"
mkdir -p config
echo "$ISO_NAME" > config/build.config

mkdir -p config/binary
echo "KAOWEI_DEBIAN" > config/binary/volume

mkdir -p config/bootloaders/isolinux
cp ../splash.jpg config/bootloaders/isolinux/splash.jpg

cat <<EOF > config/bootloaders/isolinux/isolinux.cfg
UI vesamenu.c32
DEFAULT live
PROMPT 0
TIMEOUT 1
MENU BACKGROUND splash.jpg
MENU TITLE Loading KAOWEI DEBIAN...
LABEL live
  menu label ^Live Boot (Autostart App)
  kernel /live/vmlinuz
  append initrd=/live/initrd.img boot=live quiet splash ---
EOF


echo "[Step 12] Build the ISO..."
sudo lb build

echo "[✅ Done] ISO built at: $PWD/$ISO_NAME.iso"
