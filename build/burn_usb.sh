burn_usb() {
    echo ""
    echo "[Step 3] Burning ISO to USB"
    echo ""
    cd ../kaowei-iso
    ISO_PATH_ABS=$(find . -name '*.iso' | sort | tail -n 1)
    if [ -z "$ISO_PATH_ABS" ]; then
        echo "ERROR: No existing ISO found to burn. Aborting."
        exit 1
    fi
    echo "[!] Using last built ISO: $ISO_PATH_ABS"
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

    echo "=== Summary ==="
    echo "USB Device : $USB_DEV"
    echo "ISO File   : $ISO_PATH_ABS"
    echo ""
    read -rp "[!] Are you sure you want to write $ISO_PATH_ABS to $USB_DEV? This will erase all data on it. [y/N]: " CONFIRM

    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        echo "[!] Aborted by user."
        exit 1
    fi

    echo "[!] Writing ISO to USB using 'dd'..."
    sudo dd if="$ISO_PATH_ABS" of="$USB_DEV" bs=1M status=progress oflag=direct && sync

    echo "[+] ISO written to USB successfully."

}
