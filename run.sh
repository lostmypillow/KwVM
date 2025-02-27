#!/bin/bash

# Exit on error
set -e

echo "KwVDI 0.0.1"
echo "Author: Johnny Lin"
echo "Email: jmlin0101@gmail.com"

echo "SETUP [Updating system...]"
sudo apt-get update -y >/dev/null
echo "ok"

echo "SETUP [Ensuring necessary packages are installed...]"
sudo apt-get install -y python3-venv python3-pip python3-tk wget curl gnupg virt-viewer 
echo "ok"

echo "SETUP [Installing Python requirements...]"
pip install -r requirements.txt >/dev/null
# Gunicorn is installed only in deployment. This is becuz gunicorn doesn't work in Windows, where most of the dev work happens

echo "ok"

echo "SETUP [Running setup.py..]"
python3 -m setup
echo "ok"

