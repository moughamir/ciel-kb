# Building Custom Arch Linux for QEMU

This guide provides instructions for building a minimal, custom [[Linux]] distribution for the [[Cognitive Internet]] project on [[Arch Linux]].

## Overview

This guide is a variant of the main build guide, tailored for [[Arch Linux]]. It uses the same build scripts but with different dependencies and a slightly different [[QEMU]] command.

## Build Scripts

The build scripts are located in the `scripts/os-builder` directory:

*   `cognitive_os_builder.sh`: The full build script that compiles a custom [[kernel]].
*   `quick_test_version.sh`: A faster build script that uses your existing [[kernel]] for quick testing.

## Arch Linux Dependencies

Install the required dependencies for [[Arch Linux]]:

```bash
sudo pacman -Syu
sudo pacman -S --needed base-devel wget tar cpio gzip qemu libvirt rustup clang lld git bc flex bison libelf openssl grub xorriso mtools
```

## Quick Start (5-10 Minutes)

1.  **Run the quick build script:**
    ```bash
    cd scripts/os-builder
    ./quick_test_version.sh
    ```

2.  **Test with [[QEMU]]:**
    Note the [[kernel]] path is `/boot/vmlinuz-linux` on [[Arch Linux]].
    ```bash
    qemu-system-x86_64 \
        -kernel /boot/vmlinuz-linux \
        -initrd cognitive-quick-test/[[initramfs]].img \
        -append "console=ttyS0 quiet loglevel=3" \
        -nographic \
        -m 256M \
        -serial mon:stdio
    ```

## Full Build (30-60 Minutes)

1.  **Run the full build script:**
    ```bash
    cd scripts/os-builder
    ./cognitive_os_builder.sh
    ```

2.  **Test the ISO with [[QEMU]]:**
    ```bash
    qemu-system-x86_64 -cdrom cognitive-os-build/cognitive-os.iso -m 512M
    ```

## Troubleshooting

*   **[[QEMU]] Display Issues:** If you experience display issues, try appending `"console=tty1 quiet loglevel=3"` to the [[QEMU]] command.
*   **Permission Issues:** If you encounter permission issues with `mknod`, you may need to run the script with `sudo` or adjust your system's device node permissions.
*   **Cargo Build Failures:**
    ```bash
    # Ensure musl target is installed
    rustup target add x86_64-unknown-linux-musl

    # Check Rust version (needs 1.70+)
    rustc --version
    ```
*   **[[musl]] support:** The build scripts use `[[musl]]` to create static binaries. Ensure your [[Arch Linux]] environment has the necessary tools to compile for the `x86_64-unknown-linux-musl` target.