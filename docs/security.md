# Security Documentation

## 1. Threat Model
CodeSupply defends against malicious archives, bad dependencies, and system-level threats by ensuring isolated processing.

## 2. Malicious Archives
- **File size limits**: Max 100MB upload.
- **File count limits**: Max 10,000 files in archive.
- **Uncompressed size limits**: Max 500MB extracted size.
- **Path traversal prevention**: Rejected `../` and absolute paths.
- **Dangerous filename rejection**: Blocks executables.

## 3. No Code Execution Guarantee
- Never runs npm install, pip install, mvn, etc.
- Never executes lifecycle scripts.
- Uploaded projects are DATA, never executable.

## 4. Temporary File Isolation
- Isolated directories per scan.
- Cleanup after retention period.

## 5. Data Retention
- Configurable retention via `SCAN_RETENTION_DAYS`.
- Manifest data stored, code discarded.

## 6. External Service Failures
- Graceful degradation for OSV API.
- Never marks unchecked components as safe.

## 7. SSRF Considerations
- Allowlisted external hosts only via `ALLOWED_REGISTRY_HOSTS`.
- No arbitrary URL fetching from manifests.

## 8. Logging Policy
- What is logged: Scan events.
- What is NEVER logged: Secrets, source, keys, credentials, full archives.

## 9. Input Validation
- All inputs validated via Pydantic.
- File type verification.
- Identifier validation.

## 10. Dependency Security
- Minimal dependency surface.
- All deps from official repositories.
