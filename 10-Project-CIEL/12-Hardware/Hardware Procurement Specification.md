# Hardware Procurement Guide

This guide outlines hardware recommendations for the [[Cognitive Internet]] project, organized into three tiers. The focus is on balancing performance, cost, and open-source firmware (`[[Libreboot]]`) compatibility.

---

## Tier 1: Entry-Level Prototype (3-Node Cluster)

**Use Case:** Initial development and testing.

| Option | A: [[Raspberry Pi]] 5 ([[ARM]]) | B: Used ThinkPad X230 ([[x86_64]]) |
| :--- | :--- | :--- |
| **Processor** | Broadcom BCM2712 (4-core Cortex-A76) | Intel Core i5/i7 (Ivy Bridge) |
| **Memory** | 8GB LPDDR4X | 16GB DDR3 (upgraded) |
| **Storage** | 256GB NVMe SSD | 512GB SATA SSD |
| **[[AI]] Accelerator** | [[Raspberry Pi]] [[AI]] HAT+ (26 TOPS) | None (CPU only) |
| **Firmware** | Proprietary | **[[Libreboot]]** |
| **Cost/Node** | ~$340 | ~$340 |
| **3-Node Cost** | ~,020 | ~,020 |
| **Pros** | [[AI]] acceleration, low power, small form factor | **Full [[Libreboot]] support**, [[x86_64]], more RAM |
| **Cons** | No [[Libreboot]], less RAM | Older CPU, no dedicated [[AI]] accelerator |

---

## Tier 2: Performance Prototype (5-Node Cluster)

**Use Case:** Production evaluation and community mesh testing.

| Component | Specification | Cost (Used) |
| :--- | :--- | :--- |
| **Motherboard** | ASUS KGPE-D16 ([[Libreboot]] compatible) | ~$200 |
| **Processors** | 2x AMD Opteron 6272 (32 cores total) | ~$50 |
| **Memory** | 64GB ECC DDR3 | ~00 |
| **Storage** | 128GB NVMe (Boot) + 2TB NVMe (Cache) | ~50 |
| **Networking** | 10GbE PCIe NIC | ~$80 |
| **Optional [[GPU]]**| NVIDIA Tesla P40 (24GB VRAM) | ~$350 |
| **Total/Node** | **~$680 (No [[GPU]]) / ~,030 (With [[GPU]])** | |
| **5-Node Cost**| **$3,400 (No [[GPU]]) / $5,150 (With [[GPU]])** | |

**Advantages:** Full `[[Libreboot]]` support, massive compute capacity, ECC memory, and 10GbE networking.

---

## Tier 3: Production Cluster (10-50 Nodes)

**Use Case:** Large-scale community mesh network and production workloads.

This tier uses a hybrid approach, mixing different node types for optimal performance and cost-effectiveness.

| Node Type | Quantity | Purpose | Cost/Node | Total Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Coordinator** | 3 | Orchestration, [[Blockchain]] | ~$700 | $2,100 |
| **[[GPU]] Inference** | 10 | High-throughput inference | ~,100 | 1,000 |
| **Edge Inference**| 35 | Distributed inference | ~$340 | 1,900 |
| **Storage** | 2 | [[IPFS]] model distribution | ~$800 | ,600 |
| **Networking** | - | 10GbE Switch, Cabling | - | ,000 |
| **Grand Total** | **50** | | | **~$27,600** |

---

## Critical Hardware Selection Criteria

*   **1. `[[Libreboot]]` Compatibility:** Essential for a verifiable and secure boot process.
*   **2. [[AI]] Acceleration:** [[NPU]]s (e.g., Hailo-8) for edge inference, [[GPU]]s (e.g., NVIDIA Tesla P40) for large models.
*   **3. Memory:** Minimum 8GB for small models, 32GB+ for larger models.
*   **4. Networking:** 1GbE for development, 10GbE for production.
*   **5. Storage:** NVMe SSDs for boot and caching, HDDs for archival.

---

## Procurement Roadmap

*   **Phase 1 (Months 1-2):** Build a 3-node development cluster (Tier 1).
*   **Phase 2 (Months 3-4):** Expand to a 5-node performance cluster (Tier 2).
*   **Phase 3 (Months 5-8):** Deploy a 20-50 node community mesh (Tier 3).

---

## Final Recommendations

*   **Immediate Start:** Use [[Raspberry Pi]] 5 with [[AI]] HAT+ for a quick start.
*   **Long-Term Vision:** Concurrently, set up `[[Libreboot]]`-compatible hardware to prepare for a fully open and verifiable system.
*   **Production:** Deploy a hybrid cluster with a mix of `[[Libreboot]]` coordinator nodes and specialized inference nodes.