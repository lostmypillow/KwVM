#!/bin/bash
set -eo pipefail
trap 'echo "[!] ERROR at line $LINENO: $BASH_COMMAND exited with status $?"' ERR

VERSION="0.2.2"
FULL_NAME="KAOWEI DEBIAN $VERSION"
BIN_NAME="高偉虛擬機.bin"
ISO_NAME="KAOWEI_DEBIAN_$VERSION"
BIN_OUTPUT_DIR="gui"
SKIP_BIN=false
SKIP_ISO=false
SKIP_BURN=false
echo "$FULL_NAME"

while [[ "$1" != "" ]]; do
  case $1 in
  --skip-bin) SKIP_BIN=true ;;
  --skip-iso) SKIP_ISO=true ;;
  --skip-burn) SKIP_BURN=true ;;
  esac
  shift
done

source "$(dirname "$0")/bin_build.sh"
source "$(dirname "$0")/iso_build.sh"
source "$(dirname "$0")/burn_usb.sh"

# Set up APT proxy to speed up live-build
APT_PROXY="http://localhost:3142"
if ! curl -s --connect-timeout 2 "$APT_PROXY" > /dev/null; then
  echo "[!] Setting up apt cache"
  sudo apt-get install -y -qq apt-cacher-ng
  echo "Done!"
else
  echo "Using existing apt cache at $APT_PROXY"
fi
echo ""

echo "Updating APT, courtesy of Rosé..."
sudo apt-get update -qq -y  > /dev/null
echo "Done!"
echo ""

echo "Installing packages via APT, courtesy of Rosé..."
sudo apt-get install -qq -y python3-venv python3-dev live-build imagemagick ccache  syslinux-common syslinux-utils grub-pc-bin util-linux libglib2.0-bin > /dev/null
echo "Done!"
echo ""


if [ "$SKIP_BIN" = false ]; then
  build_binary
else
  echo "[!] Skipping binary build."
fi
if [ "$SKIP_ISO" = false ]; then
  build_iso
else
  echo "[!] Skipping ISO build"
fi
if [ "$SKIP_BURN" = false ]; then
burn_usb
else
  echo "[!] Skipping burning to USB"
fi
