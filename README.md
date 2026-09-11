<div align="center">

# 🛡️ CodeSupply

**Enterprise-Grade Software Supply-Chain Intelligence & Dual-Standard SBOM Platform**

[![CI Status](https://github.com/shauryamalhotra957-wq/codesupply/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/shauryamalhotra957-wq/codesupply/actions/workflows/ci.yml)
[![Release](https://img.shields.io/badge/release-v1.2.0-blue.svg)](https://github.com/shauryamalhotra957-wq/codesupply)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776ab?logo=python&logoColor=white)](https://python.org)
[![Next.js 14](https://img.shields.io/badge/Next.js-14.2%20App%20Router-black?logo=next.js)](https://nextjs.org)
[![CycloneDX 1.7](https://img.shields.io/badge/CycloneDX-1.7%20JSON-cb3837?logo=owasp)](https://cyclonedx.org)
[![SPDX 2.3](https://img.shields.io/badge/SPDX-2.3%20ISO%20Standard-43853d)](https://spdx.dev)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Security: Hardened](https://img.shields.io/badge/Security-Hardened%20(No%20Code%20Execution)-emerald.svg)](#-security-model)

*Deep manifest inspection, multi-ecosystem dependency graph resolution, OSV.dev vulnerability intelligence, dual-standard SBOM generation (CycloneDX 1.7 & SPDX 2.3), and executive compliance reporting.*

</div>

---

## 🏆 Smart India Hackathon (SIH) Showcase

CodeSupply was built as a zero-compromise, production-grade response to national and enterprise software supply chain security challenges:
- **Zero Remote Code Execution (RCE)**: Pure static parsing of manifests and lockfiles without running `npm install`, `pip`, or build tools.
- **Dual Regulatory Compliance**: Generates cryptographically validated SBOMs compliant with **US Executive Order 14028** and **NTIA Minimum Elements for SBOM**.
- **Real-Time Visibility**: Live WebSocket event streaming + instant SBOM drift comparison.
- **Developer-Centric**: Fully featured Web Dashboard **AND** standalone terminal CLI tool.

---

## ✨ Features

- **📦 5 Major Ecosystems Supported**: Native lockfile and manifest parsers for **npm** (Node.js), **PyPI** (Python), **Maven** (Java), **Go Modules** (Golang), and **Cargo** (Rust).
- **📋 Dual-Standard SBOM Generation**: Instant export to both **CycloneDX 1.7 JSON** and **SPDX 2.3 JSON** (ISO/IEC 5962:2021) with Package URLs (PURLs) and dependency relationships.
- **🚨 Real-Time Vulnerability Intelligence**: High-throughput batch querying against **OSV.dev** with CVSS v3.1 vector calculation and offline caching.
- **📄 Executive Compliance & Audit Reports**: 1-click generation of printable, standalone HTML/PDF Security Audit Reports with letter grades (A–F), CVSS matrices, and remediation guides.
- **💻 Standalone CLI (`codesupply-cli`)**: Inspect any local repository or directory right from your terminal without opening a browser.
- **⚡ Live Scan Streaming & SBOM Diffing**: Native WebSocket updates during scan execution, plus visual delta comparisons between different builds.
- **🔒 Hardened Defense-in-Depth**: In-memory rate limiting, ZIP magic byte (`PK\x03\x04`) validation, Zip Slip prevention, decompression bomb limits, and strict CSP headers.

---

## 🏗️ System Architecture

`mermaid
graph TD
    Client[Web Dashboard / Standalone CLI] --> |Upload / Query| API[FastAPI API Layer]
    Client <--> |WebSocket /ws| WS[Real-Time Event Stream]

    subgraph Core Engine
        API --> Extractor[Safe Archive Extractor (Magic Bytes, Zip Slip & Bomb Protection)]
        Extractor --> Discovery[Multi-Ecosystem Manifest Discovery]
        Discovery --> Parsers[Deterministic Parsers (npm, pip, maven, go, cargo)]
        Parsers --> Normalizer[Component & PURL Normalizer]
        Normalizer --> GraphBuilder[Dependency Graph Builder]
        Normalizer --> OSV[OSV.dev Batch Vulnerability Engine]
        OSV --> Risk[Multi-Factor Risk Assessment Engine]
        GraphBuilder --> SBOM_CDX[CycloneDX 1.7 Generator]
        GraphBuilder --> SBOM_SPDX[SPDX 2.3 Generator]
        Risk --> Report[Executive Audit Report Generator]
    end

    API --> DB[(SQLite / PostgreSQL via Async SQLAlchemy)]
`

---

## 🌐 Ecosystem Support Matrix

| Ecosystem | Manifests Parsed | Lockfiles Supported | PURL Generation | Vuln Intelligence | Risk Scoring | SBOM Ready |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Node.js (npm)** | `package.json` | `package-lock.json` (v1, v2, v3) | ✅ | ✅ | ✅ | ✅ |
| **Python (PyPI)** | `requirements.txt`, `pyproject.toml` | Pinned versions, version ranges | ✅ | ✅ | ✅ | ✅ |
| **Java (Maven)** | `pom.xml` | Standard POMs with property resolution | ✅ | ✅ | ✅ | ✅ |
| **Go (Golang)** | `go.mod` | Single/block requires, replace directives | ✅ | ✅ | ✅ | ✅ |
| **Rust (Cargo)** | `Cargo.toml` | Inline tables, dev/build dependencies | ✅ | ✅ | ✅ | ✅ |

---

## 💻 Standalone CLI Usage

CodeSupply includes a powerful command-line tool for developers and CI/CD pipelines:

`ash
# Scan a directory and display rich terminal table results
python -m app.cli scan ./sample-projects/demo-project

# Scan and export CycloneDX 1.7 SBOM
python -m app.cli scan ./my-project --export-sbom sbom.cdx.json --format cyclonedx

# Scan and export SPDX 2.3 JSON SBOM
python -m app.cli scan ./my-project --export-sbom sbom.spdx.json --format spdx

# Show platform version
python -m app.cli version
`

---

## 🚀 1-Click Launch & Deployment

### Option 1: 1-Click Launch Scripts (Fastest)

**On Windows:**
`cmd
start.bat
`

**On Linux / macOS:**
`ash
chmod +x start.sh && ./start.sh
`
- **Web Dashboard**: `http://localhost:3000`
- **Interactive API Docs**: `http://localhost:8000/docs`

### Option 2: Docker Compose

`ash
docker compose up --build
`

### Option 3: Cloud Deployment (Render Blueprint)
CodeSupply includes a pre-configured `render.yaml` blueprint. Connect this repository to **Render** or **Railway** for automated dual-service web deployment.

---

## 📚 API Reference (Highlights)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/scans` | Upload and analyze a project ZIP archive |
| `POST` | `/api/scans/sample` | Trigger immediate demo scan of multi-ecosystem project |
| `GET` | `/api/scans/{id}` | Retrieve complete scan status, summary, and risk score |
| `GET` | `/api/scans/{id}/components` | Paginated list of normalized components with evidence |
| `GET` | `/api/scans/{id}/vulnerabilities`| All detected CVEs/GHSAs with CVSS scores and fixes |
| `GET` | `/api/scans/{id}/sbom` | Get CycloneDX 1.7 JSON metadata & validation status |
| `GET` | `/api/scans/{id}/download/sbom` | Download CycloneDX 1.7 SBOM file |
| `GET` | `/api/scans/{id}/sbom/spdx` | Get SPDX 2.3 JSON SBOM |
| `GET` | `/api/scans/{id}/download/spdx` | Download SPDX 2.3 SBOM file |
| `GET` | `/api/scans/{id}/report/html` | Generate self-contained Executive Audit Report HTML |
| `GET` | `/api/scans/{base}/diff/{compare}`| Compare two scans for SBOM drift and vulnerability deltas |
| `WS` | `/api/scans/{id}/ws` | Real-time WebSocket scan progress stream |

*For complete API schemas, error codes, and headers, see [docs/API.md](docs/API.md).*

---

## 🧪 Testing & Verification

CodeSupply features 100% automated test coverage across all layers:

`ash
# Backend test suite (56/56 passing)
cd backend
pytest -v

# Backend linting & style enforcement (0 errors)
cd backend
ruff check . && ruff format --check .

# Frontend build & typecheck (0 errors)
cd frontend
npm run build && npm test
`

---

## 🔒 Security Model

- **Safe Extraction**: Strict magic bytes validation (`PK\x03\x04`), Zip Slip path traversal suppression, and 500MB bomb limits.
- **Zero Code Execution**: CodeSupply strictly parses configuration text; package scripts (`postinstall`, `setup.py`) are never run.
- **Built-in Hardening**: In-memory IP rate limiting (5 uploads/min, 60 requests/min), security headers (`X-Frame-Options: DENY`, `CSP`, `HSTS`).
- See [docs/security.md](docs/security.md) for full threat modeling details.

---

## 📄 License & Team

This project is licensed under the **MIT License**.
Developed with pride for the **Smart India Hackathon (SIH)**.
