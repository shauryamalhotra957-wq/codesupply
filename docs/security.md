# Security Documentation

This document outlines the security architecture and practices of the CodeSupply platform. Because CodeSupply ingests and processes untrusted user-uploaded archives, security is designed in layers to isolate threats and protect the host system.

## 🛡️ Threat Model Overview

CodeSupply operates under the assumption that **any uploaded archive is potentially malicious**. The primary threats we mitigate are:
1. **Host Compromise**: Malicious payloads attempting to execute code on the backend.
2. **Resource Exhaustion (Denial of Service)**: Archives designed to crash the system via excessive memory or CPU usage.
3. **Data Exfiltration / SSRF**: Payloads attempting to coerce the backend into making unauthorized network requests.
4. **File System Manipulation**: Attempts to overwrite critical system files.

## 📦 Archive Security

The core of CodeSupply involves extracting archives. We employ aggressive hardening during this phase:

- **Zip Slip Prevention**: All extracted paths are strictly validated to ensure they resolve within the intended target directory. Any path attempting directory traversal (e.g., `../../etc/passwd`) is immediately rejected.
- **Symlink Blocking**: Symbolic links within archives are ignored or explicitly blocked. We do not resolve symlinks to prevent attackers from pointing to sensitive files outside the extraction sandbox.
- **Decompression Bomb Protection**: We enforce strict thresholds:
  - Maximum compression ratio limits (e.g., rejecting files that expand by more than 100x).
  - Maximum file count limits.
  - Maximum total extracted size limits.
- **Magic Bytes Validation**: File extensions are easily spoofed. CodeSupply inspects the magic bytes (file headers) of uploads to ensure they genuinely match the expected archive formats (ZIP, TAR.GZ) before attempting processing.

## 🌐 Network Security

- **SSRF Protection**: All outbound requests (such as querying OSV.dev) use strictly parameterized clients that cannot be manipulated to query internal IP addresses or metadata services.
- **Rate Limiting**: Aggressive rate limiting is applied to all API endpoints, especially the archive upload endpoint, to prevent abuse and API exhaustion.
- **Security Headers**: The API and frontend serve standard security headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options).

## 🗄️ Data Handling

- **No Code Execution**: CodeSupply relies entirely on **static analysis**. We parse package manifests (`package.json`, `requirements.txt`, etc.) using strict schemas. We **never** execute dependency code, install packages, or run setup scripts.
- **Ephemeral Storage**: Uploaded archives and extracted files are stored in temporary, isolated directories and are securely wiped immediately after analysis completes.
- **No PII Collection**: CodeSupply does not collect, store, or process Personally Identifiable Information from the analyzed source code.

## 📑 SBOM Integrity

- **Schema Compliance**: Generated SBOMs are strictly validated against the CycloneDX 1.7 JSON schema before being returned to the user.
- **Data Provenance**: Vulnerability data is sourced exclusively from trusted, verifiable upstream databases (OSV.dev).

## 🔗 Supply Chain Transparency

CodeSupply aims to be a zero-trust tool. The platform itself has minimal external dependencies, and all dependencies are pinned and regularly audited using CodeSupply itself. We do not use binary blobs or opaque third-party libraries for core scanning functionality.

## 🚨 Incident Response Contact

If you discover a security vulnerability in CodeSupply, please do **NOT** report it in a public GitHub issue.

Please report security issues directly to the security team via email at `security@codesupply.example.com`. We will respond within 48 hours.
