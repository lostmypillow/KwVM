#!/bin/bash

# Exit on error
set -e

echo "KwVM Pre-launch Setup"
echo "Author: Johnny Lin"
echo "Email: jmlin0101@gmail.com"

echo "SETUP [Updating system...]"
sudo apt-get update -y >/dev/null
echo "ok"

echo "SETUP [Installing necessary packages...]"
packages=("python3.12-venv" ,"virt-viewer", "ccache", "libxcb-cursor0")
for package in "${packages[@]}"; do
    if ! dpkg-query -l $package >/dev/null 2>&1; then
        sudo apt-get install -y $package >/dev/null
    fi
done
echo "ok"

