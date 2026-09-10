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

**Endpoint:** `POST /api/v1/scan/archive`

Uploads a zip or tar archive for static supply chain analysis.

- **Content-Type**: `multipart/form-data`
- **Parameters**: 
  - `file`: The archive file.

**Response (202 Accepted)**
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Archive uploaded successfully. Connect to WebSocket for real-time status."
}
```

### 2. Get Scan Status / Results

**Endpoint:** `GET /api/v1/scan/{scan_id}`

Retrieves the risk assessment and vulnerability report for a completed scan.

- **Path Parameters**: 
  - `scan_id` (string): The UUID of the scan.

**Response (200 OK)**
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "risk_score": 85,
  "risk_level": "HIGH",
  "ecosystems_found": ["npm", "python"],
  "vulnerabilities": [
    {
      "id": "GHSA-xxxx-yyyy-zzzz",
      "package": "lodash",
      "version": "4.17.15",
      "severity": "HIGH",
      "cvss": 7.5
    }
  ]
}
```

### 3. Download SBOM

**Endpoint:** `GET /api/v1/scan/{scan_id}/sbom`

Retrieves the CycloneDX 1.7 JSON SBOM generated from the scan.

**Response (200 OK)**
- **Content-Type**: `application/json`
*(Returns a standard CycloneDX JSON document)*

### 4. SBOM Diffing

**Endpoint:** `POST /api/v1/sbom/diff`

Compares two CycloneDX SBOMs to identify changes in dependencies and vulnerabilities.

- **Content-Type**: `application/json`

**Request Body**
```json
{
  "base_sbom": { ... },
  "target_sbom": { ... }
}
```

**Response (200 OK)**
```json
{
  "added_dependencies": ["express@4.18.2"],
  "removed_dependencies": ["express@4.17.1"],
  "new_vulnerabilities": [],
  "resolved_vulnerabilities": ["GHSA-xxxx"]
}
```

### 5. Real-time Scan Progress (WebSocket)

**Endpoint:** `WS /api/v1/ws/scan/{scan_id}`

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
