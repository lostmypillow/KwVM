#!/bin/bash

# Exit on error
set -e

echo "KwVDI 0.0.1"
echo "Author: Johnny Lin"
echo "Email: jmlin0101@gmail.com"

echo "SETUP [Updating system...]"
sudo apt-get update -y >/dev/null
echo "ok"

echo "SETUP [Installing necessary packages...]"
packages=("python3-venv" "python3-pip" "python3-tk" "wget" "curl" "gnupg" "virt-viewer")
# Loop through each package and check if it's installed
for package in "${packages[@]}"; do
    if ! dpkg-query -l $package >/dev/null 2>&1; then
        sudo apt-get install -y $package >/dev/null
    fi
done
echo "ok"

echo "SETUP [Installing Python requirements...]"
pip install -r requirements.txt >/dev/null
echo "ok"

echo "SETUP [Running setup.py..]"
python3 -m setup
echo "ok"

