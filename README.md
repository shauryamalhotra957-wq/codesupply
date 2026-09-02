# CodeSupply — Automated SBOM Generation & Supply-Chain Risk Engine

[![SIH1449](https://img.shields.io/badge/SIH-1449-indigo.svg)](https://smartindiahackathon.gov.in/)
[![CycloneDX](https://img.shields.io/badge/CycloneDX-v1.5_JSON-blue.svg)](https://cyclonedx.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org/)
[![Tests](https://img.shields.io/badge/Tests-15%2F15_Passing-brightgreen.svg)]()

> **SIH1449 Problem Statement**: A developer should be able to upload a ZIP containing a software project. The system must automatically identify libraries, dependencies, and modules used by the application, identify versions where possible, generate a standard SBOM, detect anomalies, and provide actionable context with high automation, granularity, and UX.

---

## 🌟 Executive Overview

**CodeSupply** is a full-stack, production-grade Software Bill of Materials (SBOM) generator and software supply-chain intelligence tool. It enables developers, DevOps teams, and security auditors to upload project archives (`.zip`), safely inspect multi-ecosystem manifests (Python & Node.js), extract and normalize direct and transitive dependencies into canonical Package URLs (PURL), construct interactive dependency DAG graphs, generate validated **CycloneDX v1.5 JSON** SBOMs, identify deterministic supply-chain anomalies, and export comprehensive audit reports (PDF & CSV).

---

## 🏗️ Architecture & Data Flow

```
                      +---------------------------------------+
                      |         Developer / Web Client        |
                      +-------------------+-------------------+
                                          |
                                          | HTTP / REST (Multipart ZIP)
                                          v
                      +---------------------------------------+
                      |           FastAPI Gateway             |
                      |   /api/projects/upload | /sbom | ...  |
                      +-------------------+-------------------+
                                          |
     +------------------------------------+------------------------------------+
     |                                    |                                    |
     v                                    v                                    v
+----+--------------------+      +--------+---------------+      +-------------+----------+
| Safe Extractor & Sandbox|      | Multi-Ecosystem Parser |      | Normalizer & PURL      |
| - ZipSlip Traversal Def | ---> | - Python (PEP 508/621) | ---> | - Canonical PURL Gen   |
| - Bomb Size & Count Lim |      | - Node (v1/v2/v3 Lock) |      | - Direct / Transitive  |
| - ZERO Code Execution   |      +------------------------+      +-------------+----------+
+-------------------------+                                                    |
                                                                               v
     +-------------------------------------------------------------------------+
     |
     +-------------------> +--------------------+      +---------------------------------+
                           |   DAG Builder      | ---> | CycloneDX v1.5 JSON Generator   |
                           |   & React Flow     |      | - Metadata, PURLs, Hashes, DAG  |
                           +---------+----------+      +----------------+----------------+
                                     |                                  |
                                     v                                  v
                           +---------+----------+      +----------------+----------------+
                           | Deterministic Risk | ---> | SQLite Database Persistence     |
                           | & Anomaly Engine   |      | (Projects, Components, Findings)|
                           +--------------------+      +---------------------------------+
```

---

## 🚀 Key Features

1. **Strict Sandboxed Archive Ingestion**:
   - Guaranteed **zero execution** of uploaded source code, scripts, or binaries.
   - Built-in **ZipSlip** directory traversal exploit prevention (`os.path.commonpath` / relative containment checks).
   - Decompression zip bomb safeguards (50MB compressed / 100MB decompressed limits).
   - Deterministic workspace teardown and cleanup.

2. **Multi-Ecosystem Manifest & Lockfile Parsing**:
   - **Python Ecosystem**:
     - `requirements.txt` (supports pinned `==`, range specifiers, inline comments, extras `pkg[extra]`, markers, URL dependencies).
     - `pyproject.toml` (PEP 621 `[project.dependencies]`, `[project.optional-dependencies]`, Poetry `[tool.poetry.dependencies]`).
   - **Node.js Ecosystem**:
     - `package.json` (`dependencies`, `devDependencies`, `peerDependencies`, `optionalDependencies`).
     - `package-lock.json` (Lockfile v1, v2, and v3 deep parsing with full transitive resolution, sub-dependencies, and SHA-512 integrity hashes).

3. **Standard-Compliant CycloneDX v1.5 JSON Generation**:
   - Emits schema-compliant CycloneDX v1.5 BOMs with unique UUID serial numbers, timestamped metadata, application component descriptors, package URLs (`pkg:pypi/...`, `pkg:npm/...`), integrity hashes, license identifiers, and dependency graph relationships (`ref` -> `dependsOn`).

4. **Deterministic Risk & Supply-Chain Anomaly Engine**:
   - **Unpinned Version Detection**: Flags direct dependencies lacking exact versions (`HIGH` risk).
   - **Conflicting Requirements**: Flags inconsistent version specifiers across multiple manifest files (`HIGH` risk).
   - **Duplicate Declarations**: Identifies duplicate dependency declarations across repository files (`MEDIUM` risk).
   - **Wildcard Specifiers**: Flags dangerous `*` or loose version ranges (`MEDIUM` risk).
   - **Direct Git/URL Dependencies**: Warns on mutable Git URLs (`MEDIUM` risk).
   - **Deprecated Components**: Flags known legacy/EOL libraries (e.g., `pycrypto`, `request`) with migration advice.

5. **Extensible `RiskExplanationService`**:
   - Decoupled explanation provider architecture.
   - Ships with a deterministic rule-based explanation and remediation engine.
   - Modular interface ready for optional LLM / AI vulnerability enrichment without altering core parsing.

6. **Interactive Visual Dashboard & React Flow DAG**:
   - **Dashboard**: High-level KPIs, version pinning health percentage, Recharts ecosystem donut chart, direct vs transitive bar charts.
   - **Dependency Graph**: Interactive canvas (`@xyflow/react`) displaying application root -> direct dependencies -> nested transitive trees with risk flags and minimap.
   - **Component Details Drawer**: Deep slide-out drawer with PURL 1-click copy, exact versions, source provenance, hashes, child dependencies, and active findings.
   - **Findings Hub**: Filterable by severity (High, Medium, Low) and category with step-by-step remediation advice.
   - **Export Hub**: 1-click downloads for CycloneDX 1.5 JSON, CSV inventory, and formatted PDF Audit Reports (ReportLab).

---

## 📂 Project Structure

```
codesupply/
├── backend/                  # FastAPI Application & Services
│   ├── database.py           # SQLite schema & CRUD repository
│   ├── main.py               # FastAPI entrypoint, CORS, lifespan
│   ├── models.py             # Pydantic data schemas
│   ├── routers/
│   │   └── projects.py       # Upload, graph, findings, SBOM, & export endpoints
│   ├── services/
│   │   ├── scanner_service.py           # Pipeline orchestrator
│   │   ├── risk_engine.py               # Deterministic anomaly detection
│   │   ├── risk_explanation_service.py  # Remediation guidance service
│   │   └── report_generator.py          # ReportLab PDF & CSV generator
│   └── requirements.txt      # Backend Python dependencies
├── scanner/                  # Core Analysis & Parsing Engine
│   ├── detection/            # Multi-ecosystem manifest detector
│   │   └── detector.py
│   ├── parsers/              # Extensible parser modules
│   │   ├── base.py
│   │   ├── python_parser.py
│   │   └── node_parser.py
│   ├── normalization/        # Normalizer & PURL generator
│   │   └── normalizer.py
│   ├── relationships/        # Dependency tree & DAG builder
│   │   └── graph_builder.py
│   ├── sbom/                 # CycloneDX v1.5 JSON generator
│   │   └── cyclonedx_generator.py
│   └── security/             # ZipSlip & sandbox security
│       └── safe_extractor.py
├── frontend/                 # React + Vite + Tailwind UI
│   ├── src/
│   │   ├── components/       # UI Views, Drawers, Charts, & Nodes
│   │   │   ├── Navbar.jsx
│   │   │   ├── LandingView.jsx
│   │   │   ├── DashboardView.jsx
│   │   │   ├── DependencyGraphView.jsx
│   │   │   ├── CustomDependencyNode.jsx
│   │   │   ├── ComponentsTableView.jsx
│   │   │   ├── FindingsView.jsx
│   │   │   ├── ExportView.jsx
│   │   │   ├── ComponentDrawer.jsx
│   │   │   └── ScanProgressModal.jsx
│   │   ├── api.js            # Frontend REST API client
│   │   ├── App.jsx           # Root layout and state management
│   │   └── index.css         # Clean custom styling
│   └── package.json
├── samples/                  # Curated Sample Repositories for Demo
│   ├── python-project/       # FastAPI + SQLAlchemy sample
│   ├── node-project/         # Express + Axios + Lockfile v3 sample
│   ├── mixed-project/        # Fullstack Monorepo (Python + React)
│   ├── broken-project/       # Anomaly demonstration (unpinned, duplicates, conflicts)
│   └── *.zip                 # Pre-packaged archives for live testing
├── tests/                    # Automated Test Suite
│   ├── test_parsers.py       # Python & Node parsers tests
│   ├── test_normalizer.py    # PURL & Normalization tests
│   ├── test_graph_builder.py # DAG & edge relation tests
│   ├── test_cyclonedx.py     # CycloneDX v1.5 compliance tests
│   ├── test_risk_engine.py   # Anomaly engine & explanations tests
│   ├── test_security.py      # ZipSlip & safe extraction tests
│   └── test_api.py           # End-to-end FastAPI testclient
└── README.md
```

---

## ⚡ Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Backend Setup & Startup
```powershell
# Navigate to project root
cd C:\Users\shaur\.gemini\antigravity\scratch\codesupply

# Activate the virtual environment
.\backend\venv\Scripts\Activate.ps1

# (Optional: If creating fresh venv)
# python -m venv backend/venv
# .\backend\venv\Scripts\pip install -r backend/requirements.txt

# Start the FastAPI server on port 8000
.\backend\venv\Scripts\uvicorn.exe backend.main:app --host 127.0.0.1 --port 8000 --reload
```
Backend API will be live at `http://127.0.0.1:8000` (API Docs at `http://127.0.0.1:8000/docs`).

### 2. Frontend Setup & Startup
```powershell
# In a new terminal, navigate to frontend directory
cd C:\Users\shaur\.gemini\antigravity\scratch\codesupply\frontend

# Install dependencies (if not already installed)
npm install

# Start Vite dev server on port 5173
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🧪 Running Automated Tests

### Backend Test Suite (Pytest)
```powershell
cd C:\Users\shaur\.gemini\antigravity\scratch\codesupply
.\backend\venv\Scripts\pytest.exe -v
```
**Tests cover:**
- Python `requirements.txt` & `pyproject.toml` parsing (pinned, specs, extras, markers).
- Node.js `package.json` & `package-lock.json` (v1/v2/v3 direct and transitive trees).
- Canonical PURL generation and duplicate merging.
- CycloneDX v1.5 JSON schema properties.
- ZipSlip directory traversal exploit rejection.
- All REST API endpoints (Upload, Graph, Findings, SBOM, PDF, CSV).

### Frontend Test Suite (Vitest)
```powershell
cd C:\Users\shaur\.gemini\antigravity\scratch\codesupply\frontend
npm test
```

---

## 🔍 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/projects/upload` | Upload `.zip` archive to extract, parse, scan, and store SBOM |
| `POST` | `/api/projects/demo/{sample_type}` | 1-click instant scan of sample project (`python-project`, `node-project`, `mixed-project`, `broken-project`) |
| `GET` | `/api/projects` | List all past scanned projects |
| `GET` | `/api/projects/{id}` | Get metadata and summary metrics for a project |
| `GET` | `/api/projects/{id}/components` | Get all normalized components with PURLs, versions, and provenance |
| `GET` | `/api/projects/{id}/graph` | Get React Flow DAG nodes and edges |
| `GET` | `/api/projects/{id}/findings` | Get deterministic security and hygiene anomalies with recommendations |
| `GET` | `/api/projects/{id}/sbom` | Get raw CycloneDX v1.5 JSON document |
| `GET` | `/api/projects/{id}/export/cyclonedx` | Download CycloneDX JSON file attachment |
| `GET` | `/api/projects/{id}/export/csv` | Download CSV component inventory |
| `GET` | `/api/projects/{id}/report` | Download generated PDF security audit report |

---

## 🛡️ Security Model

- **No Code Execution**: CodeSupply does **not** execute uploaded source code, setup scripts, or binaries (`python setup.py`, `npm install`, etc.). All dependencies are extracted using safe static grammar parsers.
- **ZipSlip Protection**: Every file path in uploaded archives is sanitized. Any entry attempting path traversal (`../`, absolute paths, leading slashes) is rejected immediately with `SafeExtractionError`.
- **Zip Bomb Mitigation**: Archives are capped at 50MB compressed, 100MB uncompressed, and 5,000 files.
- **Deterministic Temporary Workspace**: Files are extracted to isolated `tempfile.mkdtemp` directories and cleaned up deterministically upon scan completion.

---

## 🔮 Future Scope & Extensibility

- **Vulnerability Database Feed**: Integrate OSV.dev / NVD REST API into `RiskEngine` to correlate CVEs directly against normalized PURLs.
- **Additional Ecosystem Parsers**: Plug in Go (`go.mod`), Rust (`Cargo.toml`/`Cargo.lock`), and Java (`pom.xml`) by implementing `BaseParser`.
- **AI/LLM Remediation Agent**: Wire an LLM into `RiskExplanationService` using the included `BaseExplanationProvider` interface to generate automated pull requests fixing unpinned and conflicting dependencies.
