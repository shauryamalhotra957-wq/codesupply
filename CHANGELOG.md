# Changelog

All notable changes to the **CodeSupply** Software Supply-Chain Intelligence Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.0] - 2026-09-11 (Wispr Flow & Dual Standards Release)

### Added
- **Wispr Flow UI/UX Overhaul**: Complete redesign inspired by the editorial dark obsidian aesthetic (#08090c), ambient blurred lighting aura, and frosted glass cards (.wispr-glass, .wispr-glow).
- **Dual SBOM Standard Architecture**: Support for both **OWASP CycloneDX 1.7 JSON** and **Linux Foundation SPDX 2.3 JSON** (ISO/IEC 5962:2021) with PURLs and dependency trees.
- **License Compliance Policy Engine** (ackend/app/risk/license_policy.py): Automated classification of open source licenses into Permissive, Weak Copyleft, Strong Copyleft (viral), and Proprietary.
- **NIST / NTIA Minimum Elements Attestation** (docs/compliance/ntia-minimum-elements.md): Full verification matrix for US Executive Order 14028.
- **SIH1449 Jury Demonstration Guide** (docs/sih/demo-script.md): 3-minute pitch outline and defense Q&A.
- **Interactive Prototype Showcase Artifact** (codesupply_showcase.html): Self-contained, zero-dependency visual demonstrator.
- **Dark Mode Dependency DAG Explorer**: ReactFlow graph visualization rendered with obsidian glass cards and risk-based glowing borders.

### Changed
- Refactored landing page hero copy to authoritative enterprise cybersecurity messaging (*\"Map every dependency. Expose every risk.\"*).
- Added CVSS v3.1 mathematical severity score badges to vulnerability inspection tables.
- Expanded ecosystem filters across the dashboard to include all 5 supported ecosystems (npm, PyPI, Maven, Go, Cargo).
- Enforced dark mode by default on root layout.

### Security
- Defense-in-depth archive validation: ZIP magic bytes (PK\x03\x04), Zip Slip suppression, decompression bomb protection (max 10k files, max 50MB per uncompressed entry).
- Strict HTTP Security Headers: Content Security Policy, X-Frame-Options DENY, X-Content-Type-Options nosniff, Referrer-Policy.
- In-memory rate limiting for scan creation and API requests.

---

## [1.1.0] - 2026-09-10 (Real-Time Architecture & Graph Synthesis)

### Added
- **Go Parser** (ackend/app/scanners/go/parser.py): Full AST parsing of go.mod with indirect dependency tracking and replace directives.
- **Rust Cargo Parser** (ackend/app/scanners/rust/parser.py): Pinned and range dependency extraction from Cargo.toml.
- **CVSS v3.1 Math Calculator**: Mathematical computation of base scores from raw vector strings.
- **OSV Concurrent Hydrator**: Parallel fetching and caching of complete vulnerability advisories.
- **Real-Time WebSockets**: Live progress streaming for background scan execution (/api/scans/{id}/ws).
- **Supply Chain Diff & Drift Engine**: Comparing two scans to detect added/removed packages and vulnerability regressions (/api/scans/{base}/diff/{compare}).

---

## [1.0.0] - 2026-09-08 (Initial Production MVP)

### Added
- Multi-ecosystem static scanner for Python (equirements.txt, pyproject.toml), Node.js (package.json, package-lock.json v1/v2/v3), and Maven (pom.xml).
- Deterministic risk scoring engine (0-100 score mapped to Critical, High, Medium, Low, Clean).
- Automated CycloneDX SBOM generation with JSON schema validation.
- FastAPI asynchronous backend with SQLAlchemy SQLite/PostgreSQL persistence.
- Next.js 14 App Router dashboard with responsive layout.
- Standalone CLI utility (python -m app.cli scan <path>).
