# Cognitive Internet - Hardware Procurement Guide

## Executive Summary

This document outlines three hardware deployment tiers for the Cognitive Internet proof-of-concept, balancing performance, cost, and open-source firmware compatibility. The recommendations prioritize verifiable boot processes (Libreboot) and efficient AI inference capabilities.

---

## Tier 1: Entry-Level Prototype (3-Node Cluster)

**Target Use Case:** Initial development, testing core concepts, home deployment

### Option A: Raspberry Pi 5 with AI Accelerator (Recommended for ARM)

**Base Configuration:**

- **Board:** Raspberry Pi 5 (8GB RAM variant)
    
    - Processor: Broadcom BCM2712 (Quad-core Cortex-A76 @ 2.4GHz)
    - GPU: VideoCore VII @ 800MHz
    - Memory: 8GB LPDDR4X-4267
    - Storage: 256GB NVMe SSD via M.2 HAT
    - Network: Gigabit Ethernet (onboard)
    - PCIe: Gen 3.0 x1 lane for expansion
    - Cost per unit: ~$80
- **AI Accelerator:** Raspberry Pi AI HAT+ (26 TOPS variant)
    
    - NPU: Hailo-8 neural network accelerator
    - Performance: 26 TOPS for inference
    - Interface: PCIe Gen 3
    - Power efficiency: ~5W under load
    - Cost per unit: $110

**Total per node:** $190 (board) + $110 (AI HAT) + $40 (NVMe, power, cooling) = ~$340/node **3-Node cluster cost:** ~$1,020

**Advantages:**

- Native AI acceleration through Hailo NPU significantly improves inference performance beyond CPU-only
- Low power consumption (entire cluster under 50W)
- PCIe expansion allows for future hardware additions
- Excellent community support and documentation
- Can run quantized 7B parameter models efficiently with NPU
- Small form factor suitable for distributed deployment

**Limitations:**

- No Libreboot support (proprietary bootloader)
- Limited to 8GB RAM constrains larger model hosting
- ARM architecture may limit some x86-specific optimizations
- Requires building Rust toolchain for aarch64 target

**Firmware Strategy:** Since Libreboot doesn't support Raspberry Pi hardware, we'll focus on:

- Using U-Boot with verified boot and custom kernel
- Minimizing proprietary blob dependencies
- Documenting the boot chain for security auditing
- Building toward Phase 4 migration to Libreboot-compatible hardware

---

### Option B: Used ThinkPad X230 (Libreboot Compatible, x86_64)

**Base Configuration:**

- **Model:** Lenovo ThinkPad X230
    
    - Processor: Intel Core i5-3320M or i7-3520M (Ivy Bridge)
    - Memory: 16GB DDR3 (upgraded)
    - Storage: 512GB SATA SSD
    - Network: Gigabit Ethernet (USB 3.0 adapter) + onboard WiFi
    - Cost per unit: ~$150-200 (used/refurbished market)
- **Firmware:** Libreboot
    
    - BIOS replacement: Complete open-source firmware
    - Boot time: ~2 seconds to kernel
    - No Intel ME (Management Engine) - removed/neutered
    - Full control of boot process
    - Cost: $0 (flash existing hardware)

**Total per node:** $200 (laptop) + $80 (RAM upgrade) + $60 (SSD) = ~$340/node **3-Node cluster cost:** ~$1,020

**Advantages:**

- **Full Libreboot support** - this is the gold standard for "trust begins at boot"
- x86_64 architecture has broader software support
- 16GB RAM allows hosting larger models (up to 13B parameters quantized)
- Built-in battery provides UPS functionality
- Established Libreboot community and documentation
- Can run full PREEMPT_RT kernel with all optimizations

**Limitations:**

- Older CPU architecture (2012 era) means lower performance than modern hardware
- No dedicated AI accelerator (CPU-only inference is 5-10x slower)
- Higher power consumption (~25W per unit vs 10W for Pi 5)
- Bulkier form factor, less suitable for distributed deployment
- Used hardware may have reliability concerns

**Performance Estimate:**

- Inference speed: ~5-10 tokens/second for 7B parameter models (CPU only)
- Suitable for development and testing, but not production workloads

---

## Tier 2: Performance Prototype (5-Node Cluster)

**Target Use Case:** Serious development, production evaluation, community mesh testing

### Recommended: Custom x86_64 Build with Libreboot

**Base Configuration:**

- **Motherboard:** ASUS KGPE-D16 (Libreboot-supported server board)
    
    - Dual Socket G34 (AMD Opteron 6000 series)
    - Memory: Up to 256GB ECC DDR3
    - Expansion: 7x PCIe slots for GPUs/accelerators
    - Network: Dual gigabit Ethernet (onboard)
    - Cost: ~$200 (used server market)
- **Processors:** 2x AMD Opteron 6272 (16-core, 2.1GHz)
    
    - Total: 32 cores, 64 threads per node
    - L3 cache: 16MB per CPU
    - TDP: 115W per CPU
    - Cost: ~$40-60 per pair (used)
- **Memory:** 64GB ECC DDR3 (8x 8GB DIMMs)
    
    - Cost: ~$80-120
- **Storage:**
    
    - Boot: 128GB NVMe (PCIe adapter)
    - Models: 2TB NVMe for model caching
    - Cost: ~$150
- **Network Upgrade:** 10GbE PCIe NIC
    
    - Critical for inter-node model synchronization
    - Cost: ~$80 (used Intel X520)
- **Optional GPU Accelerator:** NVIDIA Tesla P40 (24GB VRAM)
    
    - Datacenter inference card (no display outputs)
    - FP32 performance: 12 TFLOPS
    - Can host 70B parameter models quantized to 4-bit
    - Cost: ~$300-400 (used market)

**Total per node (without GPU):** ~$650-700 **Total per node (with GPU):** ~$950-1,100 **5-Node cluster cost:** $3,250 (no GPUs) or $5,250 (with GPUs)

**Advantages:**

- **Full Libreboot support** on production-grade server hardware
- Massive compute capacity (32 cores per node)
- ECC memory for production reliability
- PCIe expansion allows mixing CPU inference nodes with GPU-accelerated nodes
- 10GbE networking enables true cluster-level performance
- Can host larger models that current Raspberry Pi solutions cannot

**Limitations:**

- High power consumption (250-400W per node under load)
- Requires proper cooling and rack mounting
- Older AMD architecture (2012) means lower IPC than modern CPUs
- Setup complexity is significantly higher

---

## Tier 3: Production Cluster (10-50 Nodes)

**Target Use Case:** Community mesh network, production workloads, research platform

### Hybrid Approach: Mix of Node Types

**Coordinator Nodes (3x):** High-performance x86_64 with Libreboot

- Purpose: Orchestration, blockchain interaction, model aggregation
- Config: Tier 2 specification without GPUs
- Cost per node: ~$700

**Inference Nodes - GPU (5-10x):** x86_64 with NVIDIA GPUs

- Purpose: High-throughput inference for large models
- Config: Tier 2 specification with Tesla P40 or T4 GPUs
- Cost per node: ~$1,100

**Inference Nodes - Edge (20-40x):** Raspberry Pi 5 + AI HAT

- Purpose: Distributed inference, federated learning participants
- Config: Tier 1 Option A
- Cost per node: ~$340

**Storage Nodes (2x):** High-capacity IPFS nodes

- Purpose: Model distribution, blockchain archival
- Config: Used server with 8-12x 4TB HDDs in RAID
- Cost per node: ~$800

**Network Infrastructure:**

- 10GbE switch with 48 ports: ~$500 (used)
- CAT6a cabling and power distribution: ~$500

**Total 50-Node Cluster:**

- 3 Coordinators: $2,100
- 10 GPU nodes: $11,000
- 35 Edge nodes: $11,900
- 2 Storage nodes: $1,600
- Network: $1,000
- **Grand Total: ~$27,600**

**Performance Expectations:**

- Aggregate compute: ~260 TOPS (NPU) + ~120 TFLOPS (GPU) + ~3,200 CPU cores
- Can serve 1,000+ inference requests per minute
- Federated learning across 35 edge nodes
- Complete model distribution in under 2 minutes via IPFS

---

## Critical Hardware Selection Criteria

### 1. Libreboot Compatibility (Priority: Critical for x86 nodes)

The whitepaper emphasizes that "trust begins at boot." This isn't just philosophical - it's practical. A proprietary BIOS can:

- Contain backdoors or vulnerabilities we cannot audit
- Prevent boot of custom kernels with specific optimizations
- Include Intel Management Engine or AMD PSP that operate below the OS

**Verified Libreboot-Compatible Hardware:**

- ThinkPad X230, T430, T440p
- ASUS KGPE-D16, KCMA-D8 (AMD server boards)
- Intel D510MO, D945GCLF (older Atom boards)

For a complete list, consult: https://libreboot.org/docs/hardware/

### 2. AI Acceleration Options

**NPU (Neural Processing Unit):**

- Hailo-8: 26 TOPS, excellent for edge inference
- Google Coral TPU: 4 TOPS, lower cost but limited model support
- Best for: Quantized models up to 13B parameters

**GPU (Graphics Processing Unit):**

- NVIDIA Tesla P40: 24GB VRAM, 12 TFLOPS FP32, excellent for serving
- NVIDIA Tesla T4: 16GB VRAM, Turing architecture, better efficiency
- Best for: Large models (30B-70B parameters), high-throughput serving

**CPU-Only:**

- Modern AMD Ryzen/EPYC: AVX2/AVX-512 support critical
- Intel Xeon: Good for older Libreboot-compatible hardware
- Best for: Small models (7B and under), development, coordination tasks

### 3. Memory Considerations

Model hosting memory requirements (approximate, 4-bit quantization):

- 7B parameters: 4-5GB RAM
- 13B parameters: 8-10GB RAM
- 30B parameters: 18-20GB RAM
- 70B parameters: 40-45GB RAM

For inference serving, add 2-4GB for system overhead and request batching.

### 4. Network Requirements

**Minimum (Development):** Gigabit Ethernet (1 Gbps)

- Sufficient for 3-node cluster with small models

**Recommended (Production):** 10 Gigabit Ethernet (10 Gbps)

- Required for:
    - Model synchronization across 10+ nodes
    - Federated learning with frequent weight updates
    - IPFS-based model distribution
    - High-frequency inference request routing

### 5. Storage Strategy

**Boot/System:** 128GB NVMe SSD

- Fast random I/O for OS and databases

**Model Cache:** 1-2TB NVMe SSD per node

- Stores frequently-accessed models
- IPFS pinned content

**Archival:** Spinning disks (4-12TB) on dedicated storage nodes

- Long-term model versioning
- Blockchain archival data

---

## Procurement Roadmap

### Phase 1 (Months 1-2): Initial 3-Node Development Cluster

**Budget: $1,500-2,000**

**Option A (Recommended for quick start):**

- 3x Raspberry Pi 5 (8GB) with AI HAT+ (13 TOPS variant)
- 3x 256GB NVMe drives
- Gigabit network switch
- Begin development immediately, accept proprietary bootloader

**Option B (Recommended for Libreboot commitment):**

- 3x Used ThinkPad X230 with Libreboot flashed
- 16GB RAM and SSD upgrades
- Begin with CPU-only inference, focus on networking and blockchain

### Phase 2 (Months 3-4): Expand to 5-Node Performance Cluster

**Budget: $3,000-4,000**

- Add 2x high-performance nodes (Tier 2 spec)
- Upgrade network to 10GbE for performance nodes
- Add 1x dedicated IPFS storage node
- Begin GPU inference testing if budget allows

### Phase 3 (Months 5-8): Community Mesh (20-50 Nodes)

**Budget: $15,000-25,000**

- Deploy hybrid architecture (coordinators + GPU + edge)
- Geographically distributed nodes for true mesh testing
- Full blockchain integration with mainnet deployment
- Production monitoring and alerting infrastructure

---

## Vendor and Sourcing Recommendations

**New Hardware:**

- Raspberry Pi: Official distributors (Adafruit, CanaKit, Pishop)
- Network equipment: FS.com, 10Gtek (affordable 10GbE)

**Used Hardware:**

- eBay (search for "Libreboot compatible" or specific models)
- r/homelabsales (Reddit community, US-based)
- ServeTheHome forums (enterprise gear at home prices)
- Local datacenter decommission auctions

**Critical Verification:** Before purchasing used hardware, verify:

- Libreboot compatibility on libreboot.org
- No BIOS passwords or firmware locks
- All RAM slots and PCIe slots functional
- Network interfaces operational
- For laptops: battery health and screen condition

---

## Power and Cooling Considerations

**Power Consumption Estimates:**

_Raspberry Pi 5 cluster (3 nodes):_

- Idle: ~15W total
- Full inference load: ~45W total
- Annual electricity (at $0.15/kWh): ~$60

_ThinkPad X230 cluster (3 nodes):_

- Idle: ~30W total
- Full load: ~75W total
- Annual electricity: ~$100

_High-performance cluster (5 nodes with GPUs):_

- Idle: ~500W total
- Full load: ~2,000W total
- Annual electricity: ~$2,600
- Requires: Dedicated 20A circuit, proper cooling

**Cooling:**

- Raspberry Pi: Passive heatsinks + small fan adequate
- ThinkPads: Built-in cooling sufficient, keep vents clear
- Server hardware: Requires rack mount or loud fan tolerance

---

## Final Recommendations

**For immediate start (Phase 0-1):** Buy 3x Raspberry Pi 5 with AI HAT+ and begin development now. The proprietary bootloader is a compromise, but the AI acceleration and low power make this the fastest path to a working prototype.

**For long-term vision (Phase 4):** Parallel track: Acquire and flash 2-3x Libreboot-compatible ThinkPads or server boards. Develop and test the custom kernel, Libreboot configuration, and boot process on this hardware while the main development happens on Pi 5s. When ready for physical prototype, migration path is clear.

**For production (Phases 3-4):** Hybrid deployment combining Libreboot-verified coordinator nodes (x86_64) with edge inference nodes (ARM/x86 mix). This balances the need for verifiable boot security on critical infrastructure with the performance and cost benefits of purpose-built AI acceleration hardware.

The path to true hardware sovereignty is gradual but achievable with this phased approach.