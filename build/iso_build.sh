build_iso() {
    cd ..

    echo "[Step 2] Build custom Debian ISO with lb"
    # Clean up any existing build artifacts
    ISO_DIR="kaowei-iso"
    rm -rf "$ISO_DIR"
    sudo lb clean
    sudo rm -rf kaowei-iso

    pwd

    # Find the compiled .bin file
    BIN_PATH=$(find "gui" -name "*.bin" | head -n 1)
    if [[ ! -f "$BIN_PATH" ]]; then
        echo "ERROR: .bin not found!"
        exit 1
    fi

    # Copy the .bin file to the root of the build directory
    cp -f "$BIN_PATH" ./"$BIN_NAME"

    

    # Create build directory and enter it
    mkdir "$ISO_DIR"
    cd "$ISO_DIR"

    # Configure live-build options
    lb config \
        --iso-volume "$FULL_NAME" \
        --apt-http-proxy "$APT_PROXY" \
        --distribution bookworm \
        --cache true \
        --debian-installer none \
        --archive-areas "main contrib non-free non-free-firmware" \
        --debootstrap-options "--variant=minbase" \
        --bootappend-live "boot=live quiet splash persistence persistence-label=persistence"

    # Remove default boot config
    rm -f config/includes.binary/isolinux/live.cfg

    # ------------------------------
    # Package installation list
    # ------------------------------
    mkdir -p config/package-lists
    cp -f ../build/kaowei.list.chroot config/package-lists/
    # ------------------------------
    # Application autostart setup
    # ------------------------------
    mkdir -p config/includes.chroot/home/kaowei/Desktop
    mkdir -p config/includes.chroot/home/kaowei/.config/autostart
    # cp -f ../"$BIN_NAME" config/includes.chroot/home/kaowei/Desktop/

    # Place binary in shared config dir
    mkdir -p config/includes.chroot/home/kaowei/.kwvm
    cp -f ../"$BIN_NAME" config/includes.chroot/home/kaowei/.kwvm/
    cp -f ../logo.png config/includes.chroot/home/kaowei/.kwvm/
    cp -f ../win10.png config/includes.chroot/home/kaowei/.kwvm/
    cp -f ../win7.png config/includes.chroot/home/kaowei/.kwvm/
    mkdir -p config/includes.chroot/home/kaowei/Desktop
    cat <<EOF >config/includes.chroot/home/kaowei/Desktop/高偉虛擬機.desktop
[Desktop Entry]
Type=Application
Name=高偉虛擬機
Exec=/home/kaowei/.kwvm/$BIN_NAME
Icon=/home/kaowei/.kwvm/logo.png
Terminal=false
X-GNOME-Autostart-enabled=false
EOF

    cat <<EOF >config/includes.chroot/home/kaowei/.config/autostart/launch_app.desktop
[Desktop Entry]
Type=Application
Name=Launch App
Exec=/home/kaowei/.kwvm/高偉虛擬機.bin
X-GNOME-Autostart-enabled=true
EOF

    # ------------------------------
    # System customization hook
    # ------------------------------
    mkdir -p config/hooks/normal
    cp -f ../build/customize_chroot.sh config/hooks/normal/00-customize.chroot
    chmod +x config/hooks/normal/00-customize.chroot

    # ------------------------------
    # ISOLINUX bootloader config
    # ------------------------------
    mkdir -p config/includes.binary/isolinux
    cat <<EOF >config/includes.binary/isolinux/isolinux.cfg
DEFAULT live
PROMPT 0
TIMEOUT 0
LABEL live
  menu label ^$FULL_NAME
  kernel /live/vmlinuz
  append initrd=/live/initrd.img boot=live quiet splash ---
EOF

    # ------------------------------
    # GRUB bootloader config (UEFI)
    # ------------------------------
    mkdir -p config/includes.binary/boot/grub
    cat <<EOF_G >config/includes.binary/boot/grub/grub.cfg
set timeout=0
set default=0
set hidden_timeout=0
set menu_auto_hide=1
insmod all_video
load_video
set gfxpayload=keep
insmod png
if [ "${grub_platform}" = "efi" ]; then
  set menu_hide=true
fi
menuentry "$FULL_NAME" {
    linux /live/vmlinuz boot=live quiet splash ---
    initrd /live/initrd.img
}
EOF_G

    # ------------------------------
    # Final ISO build and naming
    # ------------------------------
    export LB_COMPRESSION_THREADS=$(nproc)
    export LB_COMPRESSION_XZ_OPTIONS="-9e -T$(nproc)"
    sudo lb build
    ISO_FINAL_NAME="${ISO_NAME}-$(date +%Y%m%d-%H%M).iso"
    mv live-image-amd64.hybrid.iso "$ISO_FINAL_NAME"
    ISO_PATH_ABS=$(realpath "$ISO_FINAL_NAME")

    echo "[Done] Created $FULL_NAME ISO at: $ISO_FINAL_NAME"
    echo ""
}