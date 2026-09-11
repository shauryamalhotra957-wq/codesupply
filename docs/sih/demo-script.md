# SIH1449 Live Demo & Presentation Script

**Problem Statement**: SIH1449 — Software Bill of Materials (SBOM) Generation Tool  
**Application**: CodeSupply  
**Format**: 3-Minute Live Demonstration + 2-Minute Jury Q&A  

---

## ⏱️ Minute-by-Minute Live Demo Flow

### Minute 0:00 - 0:45 | The Problem & Architecture (Hook)
> **Speaker**:
> \"Good morning respected judges. In modern software, 80 to 90 percent of application code consists of open-source third-party dependencies. Recent attacks like Log4j, XZ-Utils, and SolarWinds proved that what you don't see in your software supply chain can destroy your enterprise.
>
> Most tools fail because they require running untrusted code via build scripts like \
pm install\ or \pip\, opening attack vectors, or they output incomplete flat lists.
>
> We built **CodeSupply**: an enterprise-grade, zero-untrusted-code-execution SBOM platform with real-time vulnerability intelligence and dual standard compliance.\"

### Minute 0:45 - 1:45 | Live Archive Scan & Graph Resolution (The WOW Moment)
> **Action**:
> Click **Scan Demo Project (Instant)** on the landing page or drop a multi-language ZIP archive.
>
> **Speaker**:
> \"Watch as CodeSupply immediately processes a real multi-language archive in seconds:
> 1. Our hardened sandbox inspects ZIP magic bytes, suppresses Zip Slip attacks, and executes pure static AST parsing across Python, Node.js, Maven, Go, and Rust.
> 2. It parses 6 distinct manifests simultaneously, extracting both direct and transitive dependencies.
> 3. Rather than returning flat lists, our DAG engine constructs a Directed Acyclic Graph, resolving deep dependency chains down to vulnerable leaf packages.\"

### Minute 1:45 - 2:30 | Intelligence, Scoring & Dual SBOM Standards
> **Action**:
> Navigate to the **Executive Dashboard**, click on the **Dependency DAG**, and switch to the **Dual SBOM** view.
>
> **Speaker**:
> \"Notice our intelligence pipeline:
> - Every package is normalized into a canonical Package URL (PURL).
> - We execute concurrent sub-second batch queries against **OSV.dev** and correlate findings with the **CISA Known Exploited Vulnerabilities (KEV)** catalog.
> - We compute mathematical **CVSS v3.1 base scores**, delivering an objective letter-grade risk score (Grade F due to active critical CVEs).
> - For regulatory compliance under US Executive Order 14028, we support **Dual Standard Generation**: 1-click export to **OWASP CycloneDX 1.7 JSON** AND **SPDX 2.3 JSON (ISO/IEC 5962:2021)**.\"

### Minute 2:30 - 3:00 | Standalone CLI & Supply Chain Diffing (Closing)
> **Action**:
> Show terminal CLI execution or navigate to **/scans/compare**.
>
> **Speaker**:
> \"Developers aren't confined to a browser. Our standalone CLI allows running \codesupply scan\ right in CI/CD pipelines. Furthermore, our **Diff Engine** compares sequential releases to catch dependency drift and emerging CVEs before deployment.
>
> CodeSupply delivers the complete standard for software transparency: automated, accurate, secure, and compliant. Thank you, and we welcome your questions.\"

---

## 🎯 Jury Defense & Anticipated Questions

### Q1: \"How do you prevent malicious code execution from uploaded archives?\"
> **Answer**:
> \"We maintain a strict zero-code-execution policy. We never run \
pm\, \pip\, \mvn\, or evaluate Python setup files. We parse lockfiles and declarative manifests purely through static syntax tree analysis and deterministic parsers, with filesystem sandboxing, Zip Slip suppression, and decompression bomb thresholds.\"

### Q2: \"How do you handle packages that don't specify an exact version?\"
> **Answer**:
> \"When lockfiles are present (e.g. \package-lock.json\ or \Cargo.lock\), we extract the exact pinned resolved version. When only declared ranges exist, our Version Confidence Engine stamps the component as \declared_range\ or \unknown\, surfaces it in the compliance disclosure, and queries OSV for broad version ranges.\"

### Q3: \"Is this compliant with international standards?\"
> **Answer**:
> \"Yes. We strictly adhere to both OWASP CycloneDX 1.7 schema specifications and the Linux Foundation SPDX 2.3 international standard (ISO/IEC 5962:2021), meeting all 7 NTIA Minimum Elements for SBOMs.\"
