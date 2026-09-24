# CycloneDX v1.5/v1.6 VEX Assessment Engine

CodeSupply integrates full **Vulnerability Exploitability eXchange (VEX)** analysis into its software bill of materials (SBOM) generation pipeline.

## Overview
Traditional vulnerability scanners produce excessive noise by flagging vulnerabilities in dependencies that are never executed or reachable in runtime application logic. CodeSupply's VEX engine programmatically evaluates AST call-graph reachability to produce standards-compliant VEX statements:

- `not_affected`: Exploitability mitigated due to:
  - `code_not_present` (package installed but never imported)
  - `code_not_reachable` (functions never executed in call paths)
  - `protected_at_runtime` (sanitization and perimeter defenses active)
- `affected`: Vulnerability confirmed reachable in call path; provides actionable remediation steps.
- `fixed`: Component patched in deployed manifest.
- `under_investigation`: Triage actively underway.
