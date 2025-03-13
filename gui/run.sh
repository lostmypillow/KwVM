#!/bin/bash

# Exit on error
set -e
APP_DIR="$(pwd)"

echo "SETUP [Update system]"
sudo apt update > /dev/null
echo "ok"

echo "SETUP [Install libxcb-cursor0]"
sudo apt-get install libxcb-cursor0 > /dev/null
echo "ok"


echo "SETUP [Configure .env file]"
ENV_FILE=".env"
echo "SETUP [Review the env variables, press Enter to continue or Ctrl+C to abort]:"
cat $ENV_FILE
echo ""
read

echo "SETUP [Ensure virtual environment is enabled]"
if [ ! -d "$APP_DIR/.venv" ]; then
    python3 -m venv "$APP_DIR/.venv" >/dev/null
fi
source "$APP_DIR/.venv/bin/activate"
echo "ok"

echo "SETUP [Install Python requirements]"
pip install -r "$APP_DIR/requirements.txt" >/dev/null
echo "ok"


echo "BUILD [Build executable with pyside6-deploy]"
pyside6-deploy --name kwmathconsult --mode standalone Python/main.py

# Get the .bin filename dynamically
BIN_FILE=$(find ./kwmathconsult.dist -maxdepth 1 -type f -name "*.bin" -exec basename {} \;)

if [ -n "$BIN_FILE" ]; then
    sudo chmod +x "$APP_DIR/kwmathconsult.dist/$BIN_FILE"
else
    echo "Error: No .bin file found!"
    exit 1
fi
echo "ok"

echo "DEPLOY [Create .desktop file]"
DESKTOP_DIR="/home/kaowei/Desktop"
DESKTOP_FILE="$DESKTOP_DIR/數輔刷卡.desktop"

# Remove all .desktop files from the Desktop folder
sudo rm -f "$DESKTOP_DIR"/*.desktop

# Create or overwrite the .desktop file
echo "Creating desktop file..." >/dev/null
cat <<EOF >"$DESKTOP_FILE"
[Desktop Entry]
Version=0.2.4
Name=數輔刷卡
Comment=Launch KwMathConsult GUI
Exec=/bin/bash -c "cd $APP_DIR/kwmathconsult.dist && ./$BIN_FILE"
Icon=$APP_DIR/logo.jpg
Terminal=false
Type=Application
Categories=Utility;Application;
StartupNotify=true
EOF

# Set the appropriate permissions
sudo chmod 0755 "$DESKTOP_FILE"

echo "ok"



echo "POST-INSTALL TASK [Copying .desktop file to .config/autostart]"
AUTOSTART_DIR="/home/kaowei/.config/autostart"
if [ ! -d "$AUTOSTART_DIR" ]; then
    mkdir -p "$AUTOSTART_DIR"
    chmod 0755 "$AUTOSTART_DIR"
fi
sudo rm -f "$AUTOSTART_DIR"/*.desktop
cp "$DESKTOP_FILE" "$AUTOSTART_DIR/數輔刷卡.desktop"
sudo chmod 0755 "$AUTOSTART_DIR/數輔刷卡.desktop"
echo "ok"

echo "POST-INSTALL TASK [Enable app.log permissions]"
sudo chown -R kaowei $(dirname app.log)
sudo chmod u+w $(dirname app.log)
echo "ok"

echo "POST-INSTALL TASK [Disable screen blanking via autostart]"

AUTOSTART_FILE="/home/kaowei/.config/lxsession/LXDE-pi/autostart"
if [ ! -f "$AUTOSTART_FILE" ]; then
    mkdir -p "/home/kaowei/.config/lxsession/LXDE-pi"
    touch "$AUTOSTART_FILE"
fi

# Disable screen saver, DPMS, and blanking
if ! grep -q "@xset s off" "$AUTOSTART_FILE"; then
    echo "@xset s off" >> "$AUTOSTART_FILE"
fi
if ! grep -q "@xset -dpms" "$AUTOSTART_FILE"; then
    echo "@xset -dpms" >> "$AUTOSTART_FILE"
fi
if ! grep -q "@xset s noblank" "$AUTOSTART_FILE"; then
    echo "@xset s noblank" >> "$AUTOSTART_FILE"
fi

# Disable xscreensaver if it's installed
if ! grep -q "@xscreensaver -no-splash" "$AUTOSTART_FILE"; then
    echo "@xscreensaver -no-splash" >> "$AUTOSTART_FILE"
fi

echo "ok"

# Reboot to apply all changes
echo "ALL SETUP FINISHED! Please reboot the system with sudo reboot"