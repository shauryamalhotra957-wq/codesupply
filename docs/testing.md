# Testing & Verification Guide

CodeSupply enforces strict, automated test verification across both backend services and frontend components. Every release and pull request must achieve 100% test pass rates with zero regressions.

---

## 🧪 Test Architecture Overview

| Layer | Framework | Scope | Total Tests |
|---|---|---|---|
| **Backend Unit & Integration** | `pytest`, `pytest-asyncio`, `httpx` | REST routes, WebSocket broadcasts, parsers, normalizers, OSV client, CVSS scoring, risk engine, SBOM generators (CycloneDX 1.7 & SPDX 2.3), archive security. | **69 tests** |
| **Frontend Unit** | `jest`, `ts-jest`, `@testing-library/react` | Badge primitives, utility mergers, type guards, design tokens. | **15 tests** |
| **Type Verification** | `tsc --noEmit` | Strict mode TypeScript compilation across all routes, components, and hooks. | **0 errors** |
| **Production Build** | `next build` | Production optimization, static page generation, standalone bundling. | **7/7 routes pass** |

---

## 🚀 Running Tests

### 1. Backend Pytest Suite

Run all 69 backend tests using the virtual environment Python interpreter:

```powershell
# Windows (PowerShell)
cd C:\Users\shaur\OneDrive\Attachments\Desktop\CodeSupply
& backend\venv\Scripts\python.exe -m pytest backend\tests\ -v

# macOS / Linux
cd backend
source venv/bin/activate
pytest tests/ -v
```

#### Key Backend Test Modules:
- `backend/tests/test_api.py`: Validates healthcheck, scan lifecycle, sample scan, VEX generation, prescriptive remediations, CSV export, and AI explanation endpoint.
- `backend/tests/test_archive_security.py`: Verifies zero-code-execution sandbox, path traversal suppression (`../` and `..\`), decompressed bomb ratio limits (100:1), and file count quotas.
- `backend/tests/test_npm_parser.py`: Tests `package.json` and lockfile (v1, v2, v3) AST extraction, version resolution, and declaration merging.
- `backend/tests/test_python_parser.py`: Tests `requirements.txt` (PEP 508 specifiers, hashes, extras) and `pyproject.toml` parsing.
- `backend/tests/test_rust_parser.py`: Tests `Cargo.toml` and `Cargo.lock` parsing and lockfile resolution.
- `backend/tests/test_go_parser.py`: Tests `go.mod` module extraction, indirect dependency tagging, and replace directives.
- `backend/tests/test_maven_parser.py`: Tests `pom.xml` XML namespace handling and `${property}` variable interpolation.
- `backend/tests/test_sbom.py`: Validates generated CycloneDX 1.7 JSON documents against structural schema requirements.
- `backend/tests/test_spdx_generator.py`: Validates SPDX 2.3 JSON (ISO/IEC 5962:2021) document structure and relationship assertions.
- `backend/tests/test_vex_generator.py`: Validates CycloneDX 1.7 VEX and OpenVEX v0.2.0 documents.
- `backend/tests/test_cvss_scoring.py`: Mathematical verification of CVSS v3.1 base score calculation following NIST SP 800-126.
- `backend/tests/test_e2e_pipeline.py`: End-to-end pipeline execution from sample creation through all 10 analysis stages to dashboard readiness.

---

### 2. Frontend Unit Tests

Run the Jest test suite:

```powershell
cd C:\Users\shaur\OneDrive\Attachments\Desktop\CodeSupply\frontend
npm test
```

### 3. Frontend Typecheck & Production Build

Verify strict TypeScript types and generate the production bundle:

```powershell
cd C:\Users\shaur\OneDrive\Attachments\Desktop\CodeSupply\frontend

# Typecheck
npm run typecheck

# Production Build
npm run build
```

---

## 🛡️ Security Verification (Zero-Code-Execution)

The security test suite (`test_archive_security.py`) explicitly validates that CodeSupply:
1. **Never executes uploaded code**: Archives are parsed strictly via read-only AST data extraction.
2. **Blocks Zip Slip vulnerabilities**: Malicious archive entries attempting path traversal outside the extraction root raise `ArchiveSecurityError` and are immediately quarantined.
3. **Rejects Decompression Bombs**: Archives exceeding 100MB compressed, 500MB uncompressed, or a 100:1 expansion ratio are aborted prior to processing.
