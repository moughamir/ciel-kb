# Cognitive Internet - Repository Structure

```bash
cognitive-internet/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                    # Continuous integration for all crates
│   │   ├── docker-build.yml          # Multi-arch container builds
│   │   └── release.yml               # Automated releases and artifacts
│   └── ISSUE_TEMPLATE/
│       └── bug_report.md
│
├── crates/                           # Rust workspace root
│   ├── node-core/                    # Main node daemon
│   │   ├── src/
│   │   │   ├── main.rs              # Entry point with async runtime
│   │   │   ├── lifecycle.rs         # Node startup, shutdown, health
│   │   │   ├── config.rs            # Configuration management
│   │   │   └── telemetry.rs         # Metrics and tracing integration
│   │   └── Cargo.toml
│   │
│   ├── networking/                   # P2P and mesh networking
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── libp2p_transport.rs  # libp2p-rs configuration
│   │   │   ├── discovery.rs         # Peer discovery (mDNS, Kademlia)
│   │   │   ├── protocols/           # Custom protocol definitions
│   │   │   │   ├── inference.rs     # Inference request/response
│   │   │   │   ├── federated.rs     # Model update distribution
│   │   │   │   └── governance.rs    # DAO voting protocol
│   │   │   └── security.rs          # Noise protocol, encryption
│   │   └── Cargo.toml
│   │
│   ├── blockchain/                   # Smart contract integration
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── ethereum.rs          # Ethereum/L2 client
│   │   │   ├── contracts/           # Contract interfaces
│   │   │   │   ├── reputation.rs    # Reputation tracking
│   │   │   │   ├── governance.rs    # DAO governance
│   │   │   │   └── verification.rs  # Output verification
│   │   │   └── proofs.rs            # Zero-knowledge proof generation
│   │   └── Cargo.toml
│   │
│   ├── ai-runtime/                   # AI engine abstraction
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── traits.rs            # Runtime trait definitions
│   │   │   ├── engines/
│   │   │   │   ├── ollama.rs        # Ollama integration
│   │   │   │   ├── vllm.rs          # vLLM integration
│   │   │   │   └── tensorrt.rs      # TensorRT-LLM
│   │   │   ├── models.rs            # Model management and loading
│   │   │   └── scheduler.rs         # Request scheduling and batching
│   │   └── Cargo.toml
│   │
│   ├── orchestration/                # Cluster management
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── discovery.rs         # Node discovery and health
│   │   │   ├── load_balancer.rs     # Request routing
│   │   │   ├── consensus.rs         # Distributed consensus
│   │   │   └── benchmarking.rs      # ELO rating system
│   │   └── Cargo.toml
│   │
│   ├── api-gateway/                  # Unified API interface
│   │   ├── src/
│   │   │   ├── main.rs
│   │   │   ├── rest.rs              # REST API endpoints
│   │   │   ├── graphql.rs           # GraphQL schema
│   │   │   ├── grpc.rs              # gRPC services
│   │   │   └── websocket.rs         # WebSocket streaming
│   │   └── Cargo.toml
│   │
│   ├── storage/                      # Distributed storage layer
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── ipfs.rs              # IPFS integration
│   │   │   ├── torrent.rs           # BitTorrent protocol
│   │   │   ├── cache.rs             # Local caching layer
│   │   │   └── verification.rs      # Content integrity checks
│   │   └── Cargo.toml
│   │
│   └── common/                       # Shared utilities
│       ├── src/
│       │   ├── lib.rs
│       │   ├── crypto.rs            # Cryptographic primitives
│       │   ├── types.rs             # Common data structures
│       │   └── errors.rs            # Error handling
│       └── Cargo.toml
│
├── infrastructure/                   # Deployment and operations
│   ├── docker/
│   │   ├── Dockerfile.node          # Multi-stage build for nodes
│   │   ├── Dockerfile.gateway       # API gateway container
│   │   └── docker-compose.yml       # Development cluster
│   │
│   ├── kubernetes/                   # K8s manifests
│   │   ├── base/                    # Base configurations
│   │   ├── overlays/                # Environment-specific overlays
│   │   │   ├── development/
│   │   │   ├── staging/
│   │   │   └── production/
│   │   └── kustomization.yaml
│   │
│   ├── terraform/                    # Infrastructure as code
│   │   ├── aws/                     # AWS deployment
│   │   ├── gcp/                     # Google Cloud deployment
│   │   └── bare-metal/              # Physical cluster config
│   │
│   └── monitoring/                   # Observability stack
│       ├── prometheus/
│       │   ├── prometheus.yml
│       │   └── alerts.yml
│       ├── grafana/
│       │   └── dashboards/
│       └── opentelemetry/
│           └── collector.yml
│
├── os-build/                         # Custom OS build system
│   ├── kernel/
│   │   ├── configs/
│   │   │   ├── x86_64.config       # x86_64 kernel config
│   │   │   └── aarch64.config      # ARM64 kernel config
│   │   ├── patches/                # RT and optimization patches
│   │   └── build.sh                # Kernel compilation script
│   │
│   ├── libreboot/
│   │   ├── configs/                # Board-specific configs
│   │   └── build.sh
│   │
│   ├── base-system/
│   │   ├── packages.txt            # Minimal package list
│   │   ├── rootfs/                 # Root filesystem structure
│   │   └── init-scripts/           # Custom init system
│   │
│   └── provisioning/
│       ├── ansible/                # Automated provisioning
│       └── scripts/                # Shell-based setup
│
├── contracts/                        # Smart contracts
│   ├── solidity/                    # Ethereum contracts
│   │   ├── Reputation.sol
│   │   ├── Governance.sol
│   │   └── Verification.sol
│   └── tests/
│
├── docs/                            # Documentation
│   ├── architecture/
│   │   ├── system-design.md
│   │   ├── networking.md
│   │   └── security.md
│   ├── api/
│   │   ├── rest-api.md
│   │   └── grpc-spec.md
│   ├── deployment/
│   │   ├── bare-metal-guide.md
│   │   └── cloud-deployment.md
│   └── research/
│       └── whitepaper.pdf          # Original whitepaper
│
├── tests/                           # Integration tests
│   ├── integration/
│   ├── e2e/
│   └── benchmarks/
│
├── scripts/                         # Utility scripts
│   ├── setup-dev.sh                # Development environment setup
│   ├── build-all.sh                # Build all components
│   └── deploy.sh                   # Deployment automation
│
├── Cargo.toml                       # Workspace root manifest
├── Cargo.lock
├── .gitignore
├── .dockerignore
├── README.md
└── LICENSE
```

## Key Design Decisions

### Crate Organization
The crate structure mirrors the seven-layer architecture from the whitepaper, creating clear boundaries between networking, AI runtime, blockchain, and orchestration concerns. Each crate is designed to be independently testable and potentially usable outside the main system.

### Infrastructure Separation
The infrastructure directory contains everything needed for deployment across different environments - from Docker containers for development to Kubernetes manifests for production and Terraform for bare-metal provisioning. This separation ensures deployment concerns don't pollute the core application code.

### OS Build System
The os-build directory is critical for Phase 4 (Physical Prototype). It contains everything needed to build optimized Linux images with custom kernels, Libreboot configurations, and minimal base systems. This is where the vision of "trust begins at boot" becomes reality.

### Documentation Structure
Documentation is organized by audience - architecture docs for system designers, API docs for developers, and deployment guides for operators. The research directory preserves the theoretical foundation.