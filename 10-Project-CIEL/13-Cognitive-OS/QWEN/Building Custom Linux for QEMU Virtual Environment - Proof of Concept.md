# Building a Custom Linux Distribution for [[QEMU]]

This guide provides instructions for building a minimal custom Linux distribution for the [[Cognitive Internet]] project.

## Overview

This guide provides instructions for building a minimal, custom Linux distribution for the Cognitive Internet project. The build process includes:
*   Compiling a custom [[Linux kernel]].
*   Building a minimal [[userspace]] with [[BusyBox]] and [[musl]].
*   Including a [[Rust]] program to display a boot message.
*   Packaging everything into a [[bootable]] ISO.

## Build Scripts

The build scripts are located in the `scripts/os-builder` directory:

*   `cognitive_os_builder.sh`: The full build script that compiles a custom kernel.
*   `quick_test_version.sh`: A faster build script that uses your existing kernel for quick testing.

## Dependencies for Debian/Ubuntu

Install the required dependencies for Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y build-essential wget tar cpio gzip qemu-system-x86 curl rust-all
```

## Quick Start (5-10 Minutes)

1.  **Run the quick build script:**
    ```bash
    cd scripts/os-builder
    ./quick_test_version.sh
    ```

2.  **Test with QEMU:**
    ```bash
    ./quick_test_version.sh test
    ```

## Full Build (30-60 Minutes)

1.  **Run the full build script:**
    ```bash
    cd scripts/os-builder
    ./cognitive_os_builder.sh
    ```

2.  **Test the ISO with QEMU:**
    ```bash
    qemu-system-x86_64 -cdrom cognitive-os-build/cognitive-os.iso -m 512M
    ```

## Troubleshooting

*   **QEMU Display Issues:** If you see garbage or no display, try this alternative command:
    ```bash
    qemu-system-x86_64 \
        -kernel /boot/vmlinuz-$(uname -r) \
        -initrd cognitive-quick-test/initramfs.img \
        -append "console=tty1 quiet loglevel=3" \
        -m 256M
    ```
*   **Cargo Build Failures:**
    ```bash
    # Ensure musl target is installed
    rustup target add x86_64-unknown-linux-musl

    # Check Rust version (needs 1.70+)
    rustc --version
    ```
