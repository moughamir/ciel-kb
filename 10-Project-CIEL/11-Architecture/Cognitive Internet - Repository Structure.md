# Repository Structure

This document outlines the [[monorepo]] structure for the [[Cognitive Internet]] project.

```bash
cognitive-internet/
├── .github/         # GitHub Actions workflows and issue templates
├── crates/          # [[Rust]] workspace for all node software components
├── infrastructure/  # [[Docker]], [[Kubernetes]], and [[Terraform]] for deployment
├── os-build/        # Custom [[Linux]] OS build system with [[Libreboot]] support
├── contracts/       # Smart contracts for [[blockchain]] integration
├── docs/            # Project documentation
├── tests/           # Integration and end-to-end tests
├── scripts/         # Utility and automation scripts
├── Cargo.toml       # [[Rust]] workspace manifest
├── .gitignore
├── .dockerignore
├── README.md
└── LICENSE
```

## Top-Level Directories

*   `.github/`: Contains [[CI/CD]] workflows for automated testing, container builds, and releases.
*   `crates/`: A [[Rust]] workspace that houses all the core software components (crates) of a node, including networking, [[AI]] runtime, and [[blockchain]] integration. Each crate is independently testable.
*   `infrastructure/`: Holds all deployment and operations-related configurations. This includes [[Docker]] for development, [[Kubernetes]] for production, and [[Terraform]] for infrastructure as code.
*   `os-build/`: Contains the necessary scripts and configurations to build a custom, minimal [[Linux]] distribution for the nodes, including kernel configurations and [[Libreboot]] support.
*   `contracts/`: Stores the [[Solidity]] smart contracts for on-chain components like reputation, governance, and verification.
*   `docs/`: Project documentation, including architectural diagrams, API specifications, and deployment guides.
*   `tests/`: Contains integration, end-to-end, and benchmark tests for the entire system.
*   `scripts/`: A collection of utility scripts for development, building, and deployment automation.