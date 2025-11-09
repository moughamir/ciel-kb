# [[Cognitive OS]] Setup Guide

This guide provides instructions for building and running [[Cognitive OS]], a minimal [[Linux]] distribution for the [[Cognitive Internet]] project.

## Features

*   **Custom [[Linux]] [[Kernel]]:** Version 6.6.10 with framebuffer support.
*   **Minimal Userspace:** Built with [[BusyBox]] for a small footprint.
*   **[[Rust]] Integration:** Includes a [[Rust]]-based display program.
*   **Bootable ISO:** A small (~50-100MB) bootable ISO image.
*   **Automated Build:** Single command build process.

## Quick Start (5 Minutes)

This method uses your existing [[kernel]] for a fast build.

1.  **Install Dependencies (Debian/Ubuntu):**
    ```bash
    sudo apt-get update
    sudo apt-get install -y build-essential wget tar cpio gzip qemu-system-x86 rust-all
    ```

2.  **Build and Test:**
    ```bash
    # Download and run the quick test builder script
    wget https://raw.githubusercontent.com/.../quick_test_version.sh
    chmod +x quick_test_version.sh
    ./quick_test_version.sh
    ./quick_test_version.sh test
    ```

## Full Build (30-60 Minutes)

This method builds a custom [[kernel]] from source.

1.  **Install Dependencies (Debian/Ubuntu):**
    ```bash
    sudo apt-get update
    sudo apt-get install -y build-essential gcc make wget tar gzip cpio git bc flex bison libelf-dev libssl-dev grub-pc-bin xorriso mtools qemu-system-x86 rust-all
    ```

2.  **Build:**
    ```bash
    # Download and run the full builder script
    wget https://raw.githubusercontent.com/.../cognitive_os_builder.sh
    chmod +x cognitive_os_builder.sh
    ./cognitive_os_builder.sh
    ```
    The output is a bootable ISO: `cognitive-os-build/cognitive-os.iso`.

## Testing

*   **[[QEMU]]:**
    ```bash
    # For full build
    qemu-system-x86_64 -cdrom cognitive-os-build/cognitive-os.iso -m 512M
    ```
*   **VirtualBox:** Create a new [[Linux]] VM and attach the ISO.
*   **Real Hardware:** Use `dd` or Rufus to write the ISO to a USB drive.

## Customization

*   **Change Display Message:** Edit `src/main.rs` in the `salam-display` [[Rust]] program and rebuild.
*   **Add Programs:** Build static binaries, copy them to `rootfs/bin/`, and modify the `/rootfs/init` script.
*   **Integrate [[Ollama]]:** Download the static [[Ollama]] binary, add it to `rootfs/bin/`, and modify the `init` script to start the service and pull a model.

## System Overview

*   **ISO Size:** ~50-100MB
*   **RAM Usage:** ~100-150MB
*   **Boot Time:** < 5 seconds
*   **Init Process:** `[[GRUB]]` -> `vmlinuz` -> `[[initramfs]]` -> `/init` script -> `salam-display` program.

## Next Steps

*   **[[AI]]:** Integrate [[Ollama]], add a [[Rust]] interface.
*   **Networking:** Add network drivers to the [[kernel]], integrate `[[libp2p]]`.
*   **[[Blockchain]]:** Add an [[Ethereum]] client for smart contract interaction.
*   **Optimization:** Tune the [[kernel]] for real-time performance (`PREEMPT_RT`), huge pages, and CPU isolation.