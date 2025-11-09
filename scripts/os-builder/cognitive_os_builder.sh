#!/bin/bash
# Cognitive OS Builder - Custom Linux Distribution
# Builds a minimal Linux system that displays "Salam" on boot

set -e

# Configuration
COGNITIVE_OS_VERSION="1.0.0"
BUILD_DIR="$(pwd)/cognitive-os-build"
KERNEL_VERSION="6.6.10"
BUSYBOX_VERSION="1.36.1"
RUST_VERSION="1.75.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%T')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check for required tools
check_dependencies() {
    log "Checking dependencies..."
    
    local deps=("gcc" "make" "wget" "tar" "gzip" "cpio" "git" "bc" "flex" "bison" "libelf-dev" "libssl-dev" "grub-mkrescue" "xorriso")
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null && ! dpkg -l | grep -q "$dep"; then
            error "Missing dependency: $dep. Install with: sudo apt-get install $dep"
        fi
    done
    
    log "All dependencies satisfied"
}

# Setup build environment
setup_build_env() {
    log "Setting up build environment in: $BUILD_DIR"
    
    mkdir -p "$BUILD_DIR"/{src,rootfs,iso/boot/grub}
    cd "$BUILD_DIR"
    
    # Create directory structure for rootfs
    mkdir -p rootfs/{bin,sbin,etc,proc,sys,dev,tmp,usr/{bin,sbin},lib,lib64,root,home}
    chmod 1777 rootfs/tmp
}

# Download and build kernel
build_kernel() {
    log "Building Linux kernel $KERNEL_VERSION..."
    
    cd "$BUILD_DIR/src"
    
    if [ ! -f "linux-$KERNEL_VERSION.tar.xz" ]; then
        info "Downloading kernel source..."
        wget -c "https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-$KERNEL_VERSION.tar.xz"
    fi
    
    if [ ! -d "linux-$KERNEL_VERSION" ]; then
        info "Extracting kernel..."
        tar -xf "linux-$KERNEL_VERSION.tar.xz"
    fi
    
    cd "linux-$KERNEL_VERSION"
    
    info "Configuring kernel..."
    
    # Start with minimal config
    make defconfig
    
    # Enable framebuffer for graphics display
    scripts/config --enable FB
    scripts/config --enable FRAMEBUFFER_CONSOLE
    scripts/config --enable FB_SIMPLE
    scripts/config --enable FB_VESA
    scripts/config --enable FB_EFI
    scripts/config --enable LOGO
    scripts/config --enable LOGO_LINUX_CLUT224
    
    # Enable console fonts
    scripts/config --enable FONTS
    scripts/config --enable FONT_8x16
    scripts/config --enable FONT_TER16x32
    
    # Enable essential features
    scripts/config --enable DEVTMPFS
    scripts/config --enable DEVTMPFS_MOUNT
    scripts/config --enable TMPFS
    scripts/config --enable PROC_FS
    scripts/config --enable SYSFS
    
    # Enable EXT4 filesystem
    scripts/config --enable EXT4_FS
    
    # Disable unnecessary features to reduce size
    scripts/config --disable DEBUG_KERNEL
    scripts/config --disable DEBUG_INFO
    scripts/config --disable SOUND
    scripts/config --disable WIRELESS
    scripts/config --disable WLAN
    
    # Finalize config
    make olddefconfig
    
    info "Compiling kernel (this will take 10-30 minutes)..."
    make -j$(nproc) bzImage
    
    # Copy kernel to ISO directory
    cp arch/x86/boot/bzImage "$BUILD_DIR/iso/boot/vmlinuz"
    
    log "Kernel compiled successfully"
}

# Build BusyBox for minimal userspace
build_busybox() {
    log "Building BusyBox $BUSYBOX_VERSION..."
    
    cd "$BUILD_DIR/src"
    
    if [ ! -f "busybox-$BUSYBOX_VERSION.tar.bz2" ]; then
        info "Downloading BusyBox..."
        wget -c "https://busybox.net/downloads/busybox-$BUSYBOX_VERSION.tar.bz2"
    fi
    
    if [ ! -d "busybox-$BUSYBOX_VERSION" ]; then
        info "Extracting BusyBox..."
        tar -xf "busybox-$BUSYBOX_VERSION.tar.bz2"
    fi
    
    cd "busybox-$BUSYBOX_VERSION"
    
    info "Configuring BusyBox..."
    make defconfig
    
    # Enable static build (no dynamic libraries needed)
    sed -i 's/# CONFIG_STATIC is not set/CONFIG_STATIC=y/' .config
    
    info "Compiling BusyBox..."
    make -j$(nproc)
    
    info "Installing BusyBox to rootfs..."
    make CONFIG_PREFIX="$BUILD_DIR/rootfs" install
    
    log "BusyBox installed successfully"
}

# Install Rust toolchain
setup_rust() {
    log "Setting up Rust toolchain..."
    
    if ! command -v rustc &> /dev/null; then
        info "Installing Rust $RUST_VERSION..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain $RUST_VERSION
        source "$HOME/.cargo/env"
    fi
    
    # Add musl target for static compilation
    rustup target add x86_64-unknown-linux-musl
    
    log "Rust toolchain ready: $(rustc --version)"
}

# Build the Salam display program in Rust
build_salam_program() {
    log "Building Salam display program..."
    
    cd "$BUILD_DIR"
    
    # Create Rust project if it doesn't exist
    if [ ! -d "salam-display" ]; then
        cargo new --bin salam-display
    fi
    
    cd salam-display
    
    # Write the Rust program
    cat > src/main.rs << 'RUST_EOF'
use std::fs::{File, OpenOptions};
use std::io::{self, Write, Read};
use std::thread;
use std::time::Duration;

const TERM_CLEAR: &str = "\x1B[2J\x1B[H";
const TERM_HIDE_CURSOR: &str = "\x1B[?25l";

fn get_terminal_size() -> (u16, u16) {
    // Try to get terminal size, default to 80x24 if unavailable
    #[cfg(target_os = "linux")]
    {
        use std::os::unix::io::AsRawFd;
        
        #[repr(C)]
        struct WinSize {
            ws_row: u16,
            ws_col: u16,
            ws_xpixel: u16,
            ws_ypixel: u16,
        }
        
        let stdout = io::stdout();
        let mut size = WinSize {
            ws_row: 24,
            ws_col: 80,
            ws_xpixel: 0,
            ws_ypixel: 0,
        };
        
        unsafe {
            libc::ioctl(stdout.as_raw_fd(), libc::TIOCGWINSZ, &mut size);
        }
        
        if size.ws_row > 0 && size.ws_col > 0 {
            return (size.ws_row, size.ws_col);
        }
    }
    
    (24, 80)
}

fn display_centered(text: &str) {
    let (rows, cols) = get_terminal_size();
    
    // Clear screen and hide cursor
    print!("{}{}", TERM_CLEAR, TERM_HIDE_CURSOR);
    
    // Calculate center position
    let text_width = text.len() as u16;
    let row = rows / 2;
    let col = if cols > text_width {
        (cols - text_width) / 2
    } else {
        0
    };
    
    // Move cursor to center and print text
    print!("\x1B[{};{}H", row, col);
    
    // Print with colors and style
    print!("\x1B[1;32m{}\x1B[0m", text);
    
    io::stdout().flush().unwrap();
}

fn display_boot_sequence() {
    // Clear screen
    print!("{}{}", TERM_CLEAR, TERM_HIDE_CURSOR);
    io::stdout().flush().unwrap();
    
    thread::sleep(Duration::from_millis(500));
    
    let messages = vec![
        ("Cognitive OS v1.0.0", 1),
        ("Initializing kernel...", 2),
        ("Loading AI runtime...", 3),
        ("Starting decentralized mesh...", 4),
        ("", 6),
    ];
    
    for (msg, row) in messages {
        print!("\x1B[{};2H\x1B[2K\x1B[0;36m{}\x1B[0m", row, msg);
        io::stdout().flush().unwrap();
        thread::sleep(Duration::from_millis(300));
    }
    
    thread::sleep(Duration::from_millis(500));
}

fn main() {
    // Display boot sequence
    display_boot_sequence();
    
    // Clear and display centered "Salam"
    print!("{}", TERM_CLEAR);
    
    // ASCII art for "Salam" (optional, looks nice)
    let salam_art = r#"
    ███████╗ █████╗ ██╗      █████╗ ███╗   ███╗
    ██╔════╝██╔══██╗██║     ██╔══██╗████╗ ████║
    ███████╗███████║██║     ███████║██╔████╔██║
    ╚════██║██╔══██║██║     ██╔══██║██║╚██╔╝██║
    ███████║██║  ██║███████╗██║  ██║██║ ╚═╝ ██║
    ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
    "#;
    
    display_centered(salam_art);
    
    // Display system info below
    let (rows, _) = get_terminal_size();
    print!("\x1B[{};0H", rows - 2);
    print!("\x1B[0;33m      Cognitive Internet OS - Decentralized AI Mesh\x1B[0m");
    
    io::stdout().flush().unwrap();
    
    // Keep program running
    thread::sleep(Duration::from_secs(3600));
}
RUST_EOF
    
    # Add libc dependency to Cargo.toml
    cat > Cargo.toml << 'TOML_EOF'
[package]
name = "salam-display"
version = "1.0.0"
edition = "2021"

[dependencies]
libc = "0.2"

[profile.release]
opt-level = "z"     # Optimize for size
lto = true          # Enable link-time optimization
codegen-units = 1   # Single codegen unit for better optimization
panic = "abort"     # Abort on panic (smaller binary)
strip = true        # Strip debug symbols
TOML_EOF
    
    info "Compiling Rust program (static binary)..."
    cargo build --release --target x86_64-unknown-linux-musl
    
    # Copy to rootfs
    cp target/x86_64-unknown-linux-musl/release/salam-display "$BUILD_DIR/rootfs/bin/"
    chmod +x "$BUILD_DIR/rootfs/bin/salam-display"
    
    log "Salam program compiled and installed"
}

# Create init system
create_init_system() {
    log "Creating init system..."
    
    # Create init script
    cat > "$BUILD_DIR/rootfs/init" << 'INIT_EOF'
#!/bin/sh

# Cognitive OS Init Script
export PATH=/bin:/sbin:/usr/bin:/usr/sbin

# Mount essential filesystems
mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev

# Set hostname
hostname cognitive-os

# Configure console
stty -F /dev/console rows 24 cols 80

# Set framebuffer mode (if available)
if [ -e /sys/class/graphics/fb0 ]; then
    echo 0 > /sys/class/graphics/fb0/blank
fi

# Clear screen
clear

# Run our Salam display program
exec /bin/salam-display

# If that exits, drop to shell
exec /bin/sh
INIT_EOF
    
    chmod +x "$BUILD_DIR/rootfs/init"
    
    log "Init system created"
}

# Create system configuration files
create_system_configs() {
    log "Creating system configuration..."
    
    # Create /etc/passwd
    cat > "$BUILD_DIR/rootfs/etc/passwd" << 'EOF'
root:x:0:0:root:/root:/bin/sh
EOF
    
    # Create /etc/group
    cat > "$BUILD_DIR/rootfs/etc/group" << 'EOF'
root:x:0:
EOF
    
    # Create /etc/hostname
    echo "cognitive-os" > "$BUILD_DIR/rootfs/etc/hostname"
    
    # Create /etc/issue (login banner)
    cat > "$BUILD_DIR/rootfs/etc/issue" << 'EOF'
Cognitive OS v1.0.0
Decentralized AI Operating System

EOF
    
    log "System configuration created"
}

# Build initramfs
build_initramfs() {
    log "Building initramfs..."
    
    cd "$BUILD_DIR/rootfs"
    
    # Create device nodes
    sudo mknod -m 666 dev/null c 1 3
    sudo mknod -m 666 dev/zero c 1 5
    sudo mknod -m 666 dev/tty c 5 0
    sudo mknod -m 600 dev/console c 5 1
    sudo mknod -m 666 dev/random c 1 8
    sudo mknod -m 666 dev/urandom c 1 9
    
    info "Creating initramfs archive..."
    find . -print0 | cpio --null --create --format=newc | gzip -9 > "$BUILD_DIR/iso/boot/initramfs.img"
    
    log "Initramfs created: $(du -h $BUILD_DIR/iso/boot/initramfs.img | cut -f1)"
}

# Create bootable ISO
create_iso() {
    log "Creating bootable ISO..."
    
    # Create GRUB configuration
    cat > "$BUILD_DIR/iso/boot/grub/grub.cfg" << 'GRUB_EOF'
set timeout=0
set default=0

menuentry "Cognitive OS" {
    linux /boot/vmlinuz quiet loglevel=3 vga=791
    initrd /boot/initramfs.img
}
GRUB_EOF
    
    cd "$BUILD_DIR"
    
    info "Building ISO image..."
    grub-mkrescue -o cognitive-os.iso iso/ 2>&1 | grep -v "warning:"
    
    local iso_size=$(du -h cognitive-os.iso | cut -f1)
    
    log "ISO created successfully: cognitive-os.iso ($iso_size)"
}

# Display final instructions
show_instructions() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  Cognitive OS Build Complete!                             ║${NC}"
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo ""
    echo -e "${BLUE}ISO Location:${NC} $BUILD_DIR/cognitive-os.iso"
    echo -e "${BLUE}ISO Size:${NC} $(du -h $BUILD_DIR/cognitive-os.iso | cut -f1)"
    echo ""
    echo -e "${YELLOW}Testing Options:${NC}"
    echo ""
    echo -e "${GREEN}1. Test in QEMU (Quick Test):${NC}"
    echo "   qemu-system-x86_64 -cdrom $BUILD_DIR/cognitive-os.iso -m 512M"
    echo ""
    echo -e "${GREEN}2. Test in VirtualBox:${NC}"
    echo "   - Create new VM (Linux 2.6/3.x/4.x 64-bit)"
    echo "   - Attach cognitive-os.iso as CD/DVD"
    echo "   - Boot VM"
    echo ""
    echo -e "${GREEN}3. Create bootable USB (Linux):${NC}"
    echo "   sudo dd if=$BUILD_DIR/cognitive-os.iso of=/dev/sdX bs=4M status=progress"
    echo "   (Replace /dev/sdX with your USB device)"
    echo ""
    echo -e "${GREEN}4. Create bootable USB (Windows):${NC}"
    echo "   Use Rufus or balenaEtcher to write the ISO"
    echo ""
    echo -e "${YELLOW}What You'll See:${NC}"
    echo "   - Boot sequence with Cognitive OS branding"
    echo "   - Large ASCII art 'SALAM' in center of screen"
    echo "   - System info at bottom"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "   - Add Ollama/LLM runtime to the init system"
    echo "   - Integrate libp2p networking"
    echo "   - Add blockchain client"
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
}

# Main build process
main() {
    echo -e "${BLUE}"
    cat << "BANNER"
╔═══════════════════════════════════════════════════════════╗
║   Cognitive OS Builder                                     ║
║   Custom Linux Distribution for Decentralized AI          ║
╚═══════════════════════════════════════════════════════════╝
BANNER
    echo -e "${NC}"
    
    check_dependencies
    setup_build_env
    build_kernel
    build_busybox
    setup_rust
    build_salam_program
    create_init_system
    create_system_configs
    build_initramfs
    create_iso
    show_instructions
    
    echo ""
    log "Build completed successfully!"
}

# Run main if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
