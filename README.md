> **NOTE:** This repository is an archival lab or partial prototype. It is not actively maintained and should not be used as a reference for production-grade deployments or performance benchmarks.


# autonomous-content-pipeline

[![Release](https://img.shields.io/github/v/release/SumitDalavi/autonomous-content-pipeline?color=blue&logo=github)](https://github.com/SumitDalavi/autonomous-content-pipeline/releases)
[![Release Workflow](https://github.com/SumitDalavi/autonomous-content-pipeline/actions/workflows/release.yml/badge.svg)](https://github.com/SumitDalavi/autonomous-content-pipeline/actions/workflows/release.yml)
[![SBOM](https://img.shields.io/badge/SBOM-SPDX%20JSON-blueviolet?logo=spdx)](https://github.com/SumitDalavi/autonomous-content-pipeline/releases)

[![Release](https://img.shields.io/github/v/release/SumitDalavi/autonomous-content-pipeline?color=blue&logo=github)](https://github.com/SumitDalavi/autonomous-content-pipeline/releases)
[![SBOM](https://img.shields.io/badge/SBOM-SPDX%20JSON-blueviolet?logo=spdx)](https://github.com/SumitDalavi/autonomous-content-pipeline/releases)

An automated pipeline that scrapes topics, generates content via LLMs, and publishes articles without human intervention.

## Features
- Fully automated workflow.
- Secure, scalable architecture.
- Built-in telemetry and observability.

## Technologies
- Python, LangChain, BeautifulSoup

## Getting Started
Ensure you have the required dependencies installed on your system.

```bash
# Setup & Test
pip install -r requirements.txt
pytest
```

## Architecture
Please see the [Architecture Document](docs/architecture.md) for sequence diagrams and system design details.

## Release & Security Verification

The project includes an automated DevSecOps release pipeline (`.github/workflows/release.yml`) triggered on semantic version tags (`v*.*.*`).

Each release automatically:
1. Executes test suite gates.
2. Builds the container image.
3. Performs vulnerability scanning via Trivy.
4. Generates an SPDX SBOM (`sbom.spdx.json`) using Anchore Syft.
5. Publishes a GitHub Release with attached SBOM.

### Verifying the Release
```bash
# Verify release via GitHub CLI
gh release view v0.1.0 --repo SumitDalavi/autonomous-content-pipeline

# Download and inspect SBOM
gh release download v0.1.0 --repo SumitDalavi/autonomous-content-pipeline --pattern "sbom.spdx.json"
cat sbom.spdx.json | jq .
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Runbook](docs/runbook.md)
- [Decisions](docs/decisions.md)
- [Changelog](docs/changelog.md)