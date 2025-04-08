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
echo ""
echo "[Step 0] Pre-build setup"
while [[ "$1" != "" ]]; do
  case $1 in
    --skip-bin) SKIP_BIN=true ;;
  esac
  shift
done
sudo chmod +x 00-customize.chroot

# Set up APT proxy to speed up live-build
APT_PROXY="http://localhost:3142"
if ! curl -s --connect-timeout 2 "$APT_PROXY" > /dev/null; then
  sudo apt install -y -qq apt-cacher-ng
fi

sudo apt update -qq -y  > /dev/null
sudo apt install -qq -y rsync mmdebstrap python3-venv python3-dev live-build imagemagick ccache syslinux-common syslinux-utils grub-pc-bin util-linux > /dev/null

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

USB_MOUNT="/mnt/usbroot"
sudo mkdir -p "$USB_MOUNT"


echo ""
echo "[Step 3] Installing base system to USB"

echo "[!] Partitioning $USB_DEV..."
sudo parted "$USB_DEV" --script mklabel gpt
sudo parted "$USB_DEV" --script mkpart ESP fat32 1MiB 200MiB
sudo parted "$USB_DEV" --script set 1 esp on
sudo parted "$USB_DEV" --script mkpart primary ext4 200MiB 100%

echo "[!] Formatting partitions..."
sudo mkfs.vfat -F32 -n KAOWEI_EFI "${USB_DEV}1"
sudo mkfs.ext4 -F -L KAOWEI_DEBIAN "${USB_DEV}2"

echo "[!] Mounting root partition..."
sudo mount "${USB_DEV}2" $USB_MOUNT

TMP_RAM_ROOT="/tmp/kaowei-rootfs"

echo "[!] Creating tmpfs for fast rootfs build (4GB in RAM)..."
sudo mkdir -p "$TMP_RAM_ROOT"
sudo mount -t tmpfs -o size=4G tmpfs "$TMP_RAM_ROOT"

echo "[!] Installing base Debian with mmdebstrap into RAM..."
sudo mmdebstrap \
  --variant=minbase \
  --architectures=amd64 \
  --include=ca-certificates,locales \
  bookworm \
  "$TMP_RAM_ROOT" \
  http://deb.debian.org/debian

echo "[!] Copying rootfs from RAM to USB..."
sudo rsync -aHAX "$TMP_RAM_ROOT"/ "$USB_MOUNT"/

echo "[!] Cleaning up RAM disk..."
sudo umount "$TMP_RAM_ROOT"
sudo rmdir "$TMP_RAM_ROOT"



echo "[!] Binding system dirs..."
for dir in dev proc sys run; do
    sudo mount --bind /$dir $USB_MOUNT/$dir
done

echo "[!] Copying customization script..."
sudo cp 00-customize.chroot $USB_MOUNT/root/customize.sh
sudo chmod +x $USB_MOUNT/root/customize.sh

echo "[!] Entering chroot and customizing..."
sudo chroot $USB_MOUNT /bin/bash -c "/root/customize.sh"

echo "[!] Installing GRUB to USB (UEFI)..."
sudo mount "${USB_DEV}1" $USB_MOUNT/boot/efi
sudo chroot $USB_MOUNT grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id="$FULL_NAME" --removable
sudo chroot $USB_MOUNT update-grub

echo "[!] Cleaning up..."
sudo rm $USB_MOUNT/root/customize.sh
for dir in dev proc sys run; do
    sudo umount $USB_MOUNT/$dir
done
sudo umount $USB_MOUNT/boot/efi || true
sudo umount $USB_MOUNT
sudo rmdir "$USB_MOUNT"

sudo eject "$USB_DEV"

echo "[✅] Done! Full Debian system installed 


