#!/bin/bash
set -eo pipefail
trap 'echo "[!] ERROR at line $LINENO: $BASH_COMMAND exited with status $?"' ERR


VERSION="0.2.1"
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
  sudo apt-get install -y -qq apt-cacher-ng
fi

sudo apt-get update -qq -y  > /dev/null
sudo apt-get install -qq -y python3-venv python3-dev live-build imagemagick ccache syslinux-common syslinux-utils grub-pc-bin util-linux > /dev/null

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
else
  echo "[!] Skipping [Step 1] Build binary with pyside6-deploy"
fi

