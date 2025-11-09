#!/bin/bash
# Cognitive OS Quick Test Builder
# Uses system kernel for faster builds (perfect for testing)

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

BUILD_DIR="$(pwd)/cognitive-quick-test"
BUSYBOX_VERSION="1.36.1"

log() { echo -e "${GREEN}[$(date +'%T')]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }

# Check dependencies
check_deps() {
    log "Checking dependencies..."
    for cmd in cargo wget tar cpio gzip; do
        command -v $cmd &>/dev/null || { echo "Missing: $cmd"; exit 1; }
    done
    rustup target add x86_64-unknown-linux-musl 2>/dev/null || true
}

# Create workspace
setup() {
    log "Creating workspace: $BUILD_DIR"
    mkdir -p "$BUILD_DIR"/{rootfs/{bin,sbin,etc,proc,sys,dev,tmp,usr/bin,lib},src}
    cd "$BUILD_DIR"
}

# Build BusyBox
build_busybox() {
    log "Building BusyBox..."
    cd "$BUILD_DIR/src"
    
    if [ ! -f "busybox-$BUSYBOX_VERSION.tar.bz2" ]; then
        wget -q "https://busybox.net/downloads/busybox-$BUSYBOX_VERSION.tar.bz2"
    fi
    
    if [ ! -d "busybox-$BUSYBOX_VERSION" ]; then
        tar -xf "busybox-$BUSYBOX_VERSION.tar.bz2"
    fi
    
    cd "busybox-$BUSYBOX_VERSION"
    make defconfig &>/dev/null
    sed -i 's/# CONFIG_STATIC is not set/CONFIG_STATIC=y/' .config
    make -j$(nproc) &>/dev/null
    make CONFIG_PREFIX="$BUILD_DIR/rootfs" install &>/dev/null
    
    log "BusyBox installed"
}

# Build Salam program
build_salam() {
    log "Building Salam display program..."
    cd "$BUILD_DIR"
    
    # Create Rust project
    cargo new --bin salam-display &>/dev/null || true
    cd salam-display
    
    # Write program
    cat > src/main.rs << 'EOF'
use std::io::{self, Write};
use std::thread;
use std::time::Duration;

fn main() {
    // Clear screen and hide cursor
    print!("\x1B[2J\x1B[H\x1B[?25l");
    io::stdout().flush().unwrap();
    
    // Boot sequence
    let boot_msgs = [
        ("🚀 Cognitive OS v1.0.0", 1),
        ("🔧 Initializing kernel...", 2),
        ("🤖 Loading AI runtime...", 3),
        ("🌐 Starting mesh network...", 4),
    ];
    
    for (msg, row) in boot_msgs.iter() {
        print!("\x1B[{};2H\x1B[0;36m{}"\x1B[0m", row, msg);
        io::stdout().flush().unwrap();
        thread::sleep(Duration::from_millis(400));
    }
    
    thread::sleep(Duration::from_millis(800));
    print!("\x1B[2J\x1B[H");
    
    // Display SALAM in center
    let art = r#"#

    ███████╗ █████╗ ██╗      █████╗ ███╗   ███╗
    ██╔════╝██╔══██╗██║     ██╔══██╗████╗ ████║
    ███████╗███████║██║     ███████║██╔████╔██║
    ╚════██║██╔══██║██║     ██╔══██║██║╚██╔╝██║
    ███████║██║  ██║███████╗██║  ██║██║ ╚═╝ ██║
    ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
    #";
    
    // Center it (assuming 80x24 terminal)
    let lines: Vec<&str> = art.lines().collect();
    let start_row = (24 - lines.len()) / 2;
    
    for (i, line) in lines.iter().enumerate() {
        print!("\x1B[{};1H\x1B[1;32m{}"\x1B[0m", start_row + i, line);
    }
    
    // Bottom info
    print!("\x1B[22;10H\x1B[0;33mCognitive Internet OS - Decentralized AI Mesh"\x1B[0m");
    print!("\x1B[23;20H\x1B[0;90mPress Ctrl+C to exit"\x1B[0m");
    
    io::stdout().flush().unwrap();
    
    // Keep running
    loop {
        thread::sleep(Duration::from_secs(1));
    }
}
EOF
    
    # Configure for minimal size
    cat > Cargo.toml << 'EOF'
[package]
name = "salam-display"
version = "1.0.0"
edition = "2021"

[profile.release]
opt-level = "z"
lto = true
strip = true
panic = "abort"
EOF
    
    info "Compiling..."
    cargo build --release --target x86_64-unknown-linux-musl &>/dev/null
    
    cp target/x86_64-unknown-linux-musl/release/salam-display "$BUILD_DIR/rootfs/bin/"
    chmod +x "$BUILD_DIR/rootfs/bin/salam-display"
    
    log "Salam program ready ($(du -h $BUILD_DIR/rootfs/bin/salam-display | cut -f1))"
}

# Create init
create_init() {
    log "Creating init script..."
    
    cat > "$BUILD_DIR/rootfs/init" << 'EOF'
#!/bin/sh
export PATH=/bin:/sbin:/usr/bin:/usr/sbin

mount -t proc none /proc 2>/dev/null
mount -t sysfs none /sys 2>/dev/null
mount -t devtmpfs none /dev 2>/dev/null

hostname cognitive-os
clear

exec /bin/salam-display
EOF
    
    chmod +x "$BUILD_DIR/rootfs/init"
}

# Create initramfs
build_initramfs() {
    log "Creating initramfs..."
    
    cd "$BUILD_DIR/rootfs"
    
    # Create minimal device nodes
    [ -e dev/null ] || mknod -m 666 dev/null c 1 3
    [ -e dev/console ] || mknod -m 600 dev/console c 5 1
    
    find . -print0 | cpio --null --create --format=newc 2>/dev/null | gzip -9 > "$BUILD_DIR/initramfs.img"
    
    log "Initramfs ready ($(du -h $BUILD_DIR/initramfs.img | cut -f1))"
}

# Test with QEMU
test_qemu() {
    log "Testing with QEMU..."
    
    if ! command -v qemu-system-x86_64 &>/dev/null; then
        echo -e "${YELLOW}QEMU not found. Install with: sudo apt-get install qemu-system-x86${NC}"
        return
    fi
    
    info "Launching QEMU (press Ctrl+C to exit)..."
    info "Using host kernel: $(uname -r)"
    
    qemu-system-x86_64 \
        -kernel /boot/vmlinuz-$(uname -r) \
        -initrd "$BUILD_DIR/initramfs.img" \
        -append "console=ttyS0 quiet loglevel=3" \
        -nographic \
        -m 256M
}

# Main
main() {
    echo -e "${BLUE}"
    cat << "BANNER"
╔═══════════════════════════════════════════════════╗
║   Cognitive OS - Quick Test Builder               ║
║   (Uses existing kernel for fast iteration)       ║
╚═══════════════════════════════════════════════════╝
BANNER
    echo -e "${NC}"
    
    check_deps
    setup
    build_busybox
    build_salam
    create_init
    build_initramfs
    
    echo ""
    echo -e "${GREEN}Build complete!${NC}"
    echo ""
    echo -e "${YELLOW}Test commands:${NC}"
    echo "  1. Test with QEMU (recommended):"
    echo "     $0 test"
    echo ""
    echo "  2. Manual QEMU test:"
    echo "     qemu-system-x86_64 -kernel /boot/vmlinuz-\\\$(uname -r) -initrd $BUILD_DIR/initramfs.img -append 'console=ttyS0' -nographic -m 256M"
    echo ""
    echo "  3. Test in VirtualBox/VMware:"
    echo "     Use your existing kernel + initramfs.img"
    echo ""
}

# Handle test command
if [ "$1" = "test" ]; then
    if [ ! -f "$BUILD_DIR/initramfs.img" ]; then
        echo "Build first: $0"
        exit 1
    fi
    test_qemu
else
    main "$@"
fi
