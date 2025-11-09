# Cognitive OS - Custom Linux Distribution

A minimal [[Linux]] distribution built from scratch for the [[Cognitive Internet]] project. Boots directly to display "[[Salam]]" in an [[ASCII]] art format.

## 🎯 What You Get

- **Custom Linux kernel** (6.6.10) with [[framebuffer]] support
- **Minimal [[userspace]]** with [[BusyBox]] (static compilation)
- **Rust-based display program** that shows "Salam" centered on screen
- **Bootable ISO** (~50-100MB) that runs on real hardware or VMs
- **Complete build automation** - one command to build everything

## 🚀 Quick Start (Fast Method - 5 Minutes)

This method uses your existing kernel for rapid testing:

```bash
# 1. Install dependencies
sudo apt-get update
sudo apt-get install -y build-essential wget tar cpio gzip qemu-system-x86

# 2. Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"

# 3. Download the quick test builder
wget https://raw.githubusercontent.com/.../quick_test_version.sh
chmod +x quick_test_version.sh

# 4. Build and test
./quick_test_version.sh
./quick_test_version.sh test
```

Expected output:
```
🚀 Cognitive OS v1.0.0
🔧 Initializing kernel...
🤖 Loading AI runtime...
🌐 Starting mesh network...

    ███████╗ █████╗ ██╗      █████╗ ███╗   ███╗
    ██╔════╝██╔══██╗██║     ██╔══██╗████╗ ████║
    ███████╗███████║██║     ███████║██╔████╔██║
    ╚════██║██╔══██║██║     ██╔══██║██║╚██╔╝██║
    ███████║██║  ██║███████╗██║  ██║██║ ╚═╝ ██║
    ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝

      Cognitive Internet OS - Decentralized AI Mesh
```

## 🏗️ Full Build (Custom Kernel - 30-60 Minutes)

This builds everything from source including a custom-optimized kernel:

```bash
# 1. Install all dependencies
sudo apt-get update
sudo apt-get install -y \
    build-essential gcc make wget tar gzip cpio git bc \
    flex bison libelf-dev libssl-dev \
    grub-pc-bin xorriso mtools \
    qemu-system-x86

# 2. Download the full builder
wget https://raw.githubusercontent.com/.../cognitive_os_builder.sh
chmod +x cognitive_os_builder.sh

# 3. Run the build (grab coffee, this takes 20-30 minutes)
./cognitive_os_builder.sh
```

The build process:
1. ✅ Downloads Linux kernel 6.6.10 source
2. ✅ Configures kernel for minimal size + framebuffer
3. ✅ Compiles kernel (20-30 minutes)
4. ✅ Builds BusyBox static binary
5. ✅ Compiles Rust display program
6. ✅ Creates initramfs
7. ✅ Generates bootable ISO

Output: `cognitive-os-build/cognitive-os.iso` (~50-80MB)

## 🧪 Testing Your Build

### Method 1: QEMU (Fastest)

```bash
# Quick test build
qemu-system-x86_64 \
    -kernel /boot/vmlinuz-$(uname -r) \
    -initrd cognitive-quick-test/initramfs.img \
    -append "console=ttyS0 quiet" \
    -nographic -m 256M

# Full ISO test
qemu-system-x86_64 \
    -cdrom cognitive-os-build/cognitive-os.iso \
    -m 512M
```

### Method 2: VirtualBox

1. Create new VM (Linux 2.6/3.x/4.x 64-bit)
2. Allocate 512MB RAM (minimum)
3. Attach `cognitive-os.iso` as CD/DVD
4. Boot VM

### Method 3: Real Hardware (USB Boot)

```bash
# Linux
sudo dd if=cognitive-os.iso of=/dev/sdX bs=4M status=progress
# Replace /dev/sdX with your USB device (check with lsblk)

# Windows
# Use Rufus or balenaEtcher to write the ISO
```

### Method 4: Docker (Development)

```bash
docker run -it --rm \
    -v $(pwd):/workspace \
    -w /workspace \
    rust:latest bash

# Inside container
./cognitive_os_builder.sh
```

## 📦 Project Structure

```
cognitive-os-build/
├── src/
│   ├── linux-6.6.10/           # Kernel source
│   ├── busybox-1.36.1/          # BusyBox source
│   └── salam-display/           # Rust program
├── rootfs/
│   ├── bin/                     # BusyBox + salam-display
│   ├── init                     # Init script
│   └── etc/                     # Configuration
├── iso/
│   ├── boot/
│   │   ├── vmlinuz             # Compiled kernel
│   │   ├── initramfs.img       # Compressed rootfs
│   │   └── grub/
│   │       └── grub.cfg        # Bootloader config
│   └── ...
└── cognitive-os.iso             # Final bootable image
```

## 🔧 Customization

### Change Display Message

Edit `src/main.rs` in the Rust program:

```rust
let art = r#"
    Your custom ASCII art here
"#;
```

Rebuild:
```bash
cd cognitive-os-build/salam-display
cargo build --release --target x86_64-unknown-linux-musl
cp target/x86_64-unknown-linux-musl/release/salam-display ../rootfs/bin/
# Rebuild initramfs and ISO
```

### Add More Programs

1. Build static binaries (must be statically linked)
2. Copy to `rootfs/bin/`
3. Modify `/rootfs/init` to run your program
4. Rebuild initramfs

### Integrate Ollama

```bash
# Download Ollama static binary
wget https://ollama.ai/download/ollama-linux-amd64 -O rootfs/bin/ollama
chmod +x rootfs/bin/ollama

# Modify init script
cat >> rootfs/init << 'EOF'
# Start Ollama
/bin/ollama serve &

# Wait for it to start
sleep 5

# Load model
/bin/ollama pull gemma:2b

# Run your AI application
exec /bin/your-ai-app
EOF

# Rebuild
./cognitive_os_builder.sh
```

## 📊 System Specifications

**ISO Size:** ~50-100MB
**RAM Usage:** ~100-150MB (idle)
**Boot Time:** <5 seconds (from GRUB to display)
**Kernel Size:** ~8-12MB (compressed)
**Initramfs Size:** ~10-20MB (compressed)

## 🐛 Troubleshooting

### Build fails with "command not found"

Install missing dependencies:
```bash
sudo apt-get install build-essential flex bison libelf-dev libssl-dev
```

### QEMU shows black screen

Add `-serial stdio` to see kernel messages:
```bash
qemu-system-x86_64 -cdrom cognitive-os.iso -serial stdio -m 512M
```

### "cargo: command not found"

Install Rust:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

### Kernel compilation takes forever

Use more CPU cores:
```bash
# Edit the build script, change:
make -j$(nproc)
# to:
make -j8  # or however many cores you want to use
```

### USB boot doesn't work

Ensure USB is properly formatted and bootable:
```bash
# Use proper device (check with lsblk first!)
sudo dd if=cognitive-os.iso of=/dev/sdX bs=4M status=progress && sync
```

## 🎓 Understanding the Build

### Why Static Compilation?

All binaries are statically linked (BusyBox, Rust program) because:
- **No library dependencies** - the entire program is self-contained
- **Smaller overall size** - no need for glibc, shared libraries
- **Faster boot** - no dynamic linking at runtime
- **More portable** - runs on any x86_64 Linux kernel

### Why Custom Kernel?

- **Minimal size** - disabled all unnecessary features (sound, wireless, etc.)
- **Framebuffer support** - for graphics display
- **Optimizations** - compiled with specific flags for performance
- **Control** - we know exactly what's in our kernel

### Init Process Flow

```
1. GRUB loads kernel (vmlinuz)
2. Kernel loads initramfs into RAM
3. Kernel executes /init
4. /init mounts proc, sys, dev
5. /init executes salam-display
6. salam-display shows ASCII art
7. System waits (infinite loop)
```

## 🚀 Next Steps

### Add AI Capabilities

1. **Integrate Ollama**
   - Download static Ollama binary
   - Add model loading to init script
   - Create Rust program to interface with Ollama

2. **Add Networking**
   - Enable network drivers in kernel
   - Include busybox networking tools
   - Add libp2p Rust library

3. **Add Blockchain Client**
   - Include Ethereum client
   - Smart contract interaction
   - Reputation tracking

### Performance Optimization

1. **Kernel Tuning**
   - Enable PREEMPT_RT for real-time
   - Configure huge pages for AI models
   - CPU isolation for inference

2. **Binary Size Reduction**
   - Use UPX compression on binaries
   - Strip more kernel modules
   - Optimize Rust compilation flags

## 📚 Resources

- **Linux Kernel:** https://kernel.org/
- **BusyBox:** https://busybox.net/
- **Rust:** https://www.rust-lang.org/
- **GRUB:** https://www.gnu.org/software/grub/
- **Buildroot:** https://buildroot.org/ (alternative build system)

## 🤝 Contributing

This is part of the Cognitive Internet project. To contribute:

1. Fork the repository
2. Make your changes
3. Test thoroughly (QEMU + real hardware)
4. Submit pull request

## 📄 License

MIT OR Apache-2.0 (dual license, like Rust)

## 🎉 Success Criteria

You've successfully built Cognitive OS when:

- ✅ ISO boots in QEMU without errors
- ✅ "Salam" appears in ASCII art, centered on screen
- ✅ System info displays at bottom
- ✅ Boot time is under 10 seconds
- ✅ Memory usage is under 200MB

Congratulations! You now have a custom Linux distribution built from scratch, optimized for AI workloads, ready to integrate with the Cognitive Internet ecosystem.