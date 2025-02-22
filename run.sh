#!/bin/bash

# Exit on error
set -e


echo "SETUP [Updating system...]"
sudo apt-get update -y >/dev/null
echo "ok"

echo "SETUP [Ensuring necessary packages are installed...]"
sudo apt-get install -y python3-venv python3-pip python3-tk wget curl gnupg  virt-viewer git >/dev/null
curl -sSL -O https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb >/dev/null
rm packages-microsoft-prod.deb >/dev/null
sudo apt-get update -y >/dev/null
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18 >/dev/null
sudo ACCEPT_EULA=Y apt-get install -y mssql-tools18 >/dev/null
echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
source ~/.bashrc
sudo apt-get install -y unixodbc-dev >/dev/null
echo "ok"


echo "SETUP [Cloning joshpatten/PVE-VDIClient...]"
git clone https://github.com/joshpatten/PVE-VDIClient.git
cd ./PVE-VDIClient/

echo "SETUP [Enabling virtual environment...]"
if [ ! -d "$APP_DIR/.venv" ]; then
    python3 -m venv "$APP_DIR/.venv" >/dev/null
fi
source "$APP_DIR/.venv/bin/activate"
echo "ok"

echo "SETUP [Installing Python requirements...]"
pip install -r "$APP_DIR/requirements.txt" >/dev/null
# Gunicorn is installed only in deployment. This is becuz gunicorn doesn't work in Windows, where most of the dev work happens

echo "ok"

echo "SETUP [Building executable..]"
pyinstaller --onefile --noconsole --noconfirm --hidden-import proxmoxer.backends --hidden-import proxmoxer.backends.https --hidden-import proxmoxer.backends.https.AuthenticationError --hidden-import proxmoxer.core --hidden-import proxmoxer.core.ResourceException --hidden-import subprocess.TimeoutExpired --hidden-import subprocess.CalledProcessError --hidden-import requests.exceptions --hidden-import requests.exceptions.ReadTimeout --hidden-import requests.exceptions.ConnectTimeout --hidden-import requests.exceptions.ConnectionError vdiclient.py
echo "ok"

echo "SETUP [Modifying ini..]"
python -m modify_ini.py
echo "ok"

echo "SETUP [Moving ini file...]"
mkdir -p ~/.config/VDIClient && mv vdiclient.ini ~/.config/VDIClient/
echo "ok"

echo "[DONE!] Launching executable..."
cd dist
sudo chmod +x vdiclient
./dist/vdiclient