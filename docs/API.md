# API Reference

This document provides a comprehensive overview of the CodeSupply REST and WebSocket APIs.

## 🔑 Authentication
For local and standard self-hosted deployments, CodeSupply **does not require authentication**. It is designed to run in a trusted CI/CD environment or locally on a developer's machine.

## 🚦 Rate Limiting
To prevent resource exhaustion, the API enforces rate limits:
- **General Endpoints**: 100 requests per minute per IP.
- **Upload Endpoints**: 10 requests per minute per IP.

---

## 🛠️ Endpoints

### 1. Upload & Scan Archive

**Endpoint:** `POST /api/scans` (or `POST /api/scans/sample` for instant demo project)

Uploads a ZIP archive for static supply chain analysis.

- **Content-Type**: `multipart/form-data`
- **Parameters**: 
  - `file`: The archive file (.zip).

**Response (201 Created)**
```json
{
  "id": "550e8400e29b41d4a716446655440000",
  "status": "queued",
  "filename": "project.zip",
  "file_size": 1048576,
  "created_at": "2026-09-11T12:00:00Z",
  "stages": []
}
```

### 2. Get Scan Status & Summary

- **Scan Details:** `GET /api/scans/{scan_id}`
- **Scan Summary (Metrics & Intelligence):** `GET /api/scans/{scan_id}/summary`
- **Components Inventory:** `GET /api/scans/{scan_id}/components` (supports `?q=...&risk_level=...&ecosystem=...&page=...&per_page=...`)
- **Dependency Graph (DAG):** `GET /api/scans/{scan_id}/graph`
- **Vulnerability Findings:** `GET /api/scans/{scan_id}/vulnerabilities`
- **Scan History:** `GET /api/scans` (supports pagination `?limit=50&offset=0`)

**Response (200 OK - GET /api/scans/{scan_id}/summary)**
```json
{
  "scan_id": "550e8400e29b41d4a716446655440000",
  "total_components": 42,
  "total_vulnerabilities": 3,
  "total_high_critical": 2,
  "total_unknown_versions": 0,
  "components_by_ecosystem": {"npm": 28, "pypi": 14},
  "components_by_risk": {"critical": 1, "high": 1, "low": 40},
  "components_by_type": {"direct": 12, "transitive": 30},
  "vulnerabilities_by_severity": {"CRITICAL": 1, "HIGH": 1, "MODERATE": 1},
  "sbom_valid": true,
  "intelligence_status": "live"
}
```

### 3. Download Dual-Standard SBOM & VEX

- **CycloneDX 1.7 JSON:** `GET /api/scans/{scan_id}/sbom` (Download: `GET /api/scans/{scan_id}/download/sbom`)
- **SPDX 2.3 JSON (ISO):** `GET /api/scans/{scan_id}/sbom/spdx` (Download: `GET /api/scans/{scan_id}/download/spdx`)
- **CycloneDX 1.7 VEX:** `GET /api/scans/{scan_id}/vex` (Download: `GET /api/scans/{scan_id}/download/vex`)
- **CSV Component Inventory:** `GET /api/scans/{scan_id}/export/csv`
- **Executive Audit Report (HTML):** `GET /api/scans/{scan_id}/report/html`

### 4. Prescriptive Remediation Engine

**Endpoint:** `GET /api/scans/{scan_id}/remediations`

Returns prioritized dependency upgrades with 1-click executable CLI commands:

**Response (200 OK)**
```json
{
  "scan_id": "9a38f712...",
  "total_remediations": 1,
  "remediations": [
    {
      "component_name": "lodash",
      "current_version": "4.17.15",
      "target_version": "4.17.21",
      "ecosystem": "npm",
      "upgrade_command": "npm install lodash@4.17.21",
      "severity": "high",
      "max_cvss_score": 7.4,
      "breaking_change_risk": "low",
      "risk_reduction_score": 7.4,
      "rationale": "Upgrading from 4.17.15 to 4.17.21 patches 1 vulnerabilities with low breaking risk."
    }
  ]
}
```

### 5. SBOM Diffing & Evolution Tracking

**Endpoint:** `GET /api/scans/{scan_id}/diff/{other_scan_id}`

Compares two scans to identify added/removed components, version bumps, and resolved vulnerabilities.

**Response (200 OK)**
```json
{
  "added_dependencies": ["express@4.18.2"],
  "removed_dependencies": ["express@4.17.1"],
  "new_vulnerabilities": [],
  "resolved_vulnerabilities": ["GHSA-xxxx"]
}
```

### 6. Real-time Scan Progress (WebSocket)

**Endpoint:** `WS /api/scans/{scan_id}/ws`

Connect to this WebSocket endpoint to receive real-time updates as the scan progresses through extraction, parsing, OSV querying, and scoring.

**Message Format (Server -> Client)**
```json
{
  "stage": "EXTRACTING",
  "progress": 25,
  "message": "Validating magic bytes and extracting archive..."
}
```

---

## ❌ Error Codes

| Status Code | Code | Description |
| :--- | :--- | :--- |
| **400** | `INVALID_ARCHIVE` | The uploaded file is not a valid zip/tar archive or violates size constraints. |
| **404** | `SCAN_NOT_FOUND` | The requested `scan_id` does not exist. |
| **413** | `PAYLOAD_TOO_LARGE` | The uploaded archive exceeds the maximum allowed size. |
| **422** | `UNPROCESSABLE_ENTITY`| The archive was valid, but contained no recognizable manifests. |
| **429** | `RATE_LIMIT_EXCEEDED` | Too many requests. Please slow down. |
| **500** | `INTERNAL_ERROR` | An unexpected error occurred during processing. |
