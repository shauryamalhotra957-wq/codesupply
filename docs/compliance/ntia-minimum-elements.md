# NTIA Minimum Elements for SBOM — Compliance Attestation

## Overview

The **National Telecommunications and Information Administration (NTIA)** published the official *Minimum Elements for a Software Bill of Materials (SBOM)* pursuant to **Executive Order 14028** (*Improving the Nation's Cybersecurity*).

**CodeSupply** is engineered to strictly satisfy and exceed all required NTIA baseline elements across both its **CycloneDX 1.7** and **SPDX 2.3** output formats.

---

## 1. Data Fields Compliance Matrix

| NTIA Minimum Element | Definition & Requirement | CodeSupply Implementation | CycloneDX 1.7 JSON Path | SPDX 2.3 JSON Path |
|---|---|---|---|---|
| **Supplier Name** | Name of the entity that created or published the component. | Extracted from manifest namespaces, author fields, or ecosystem registry origins. | components[].publisher or components[].group | packages[].packageSupplier |
| **Component Name** | Primary identifier designating the unit of software. | Normalized package name per ecosystem rules (e.g. @angular/core, lask). | components[].name | packages[].packageName |
| **Version of the Component** | Specific release identifier or commit hash. | Extracted from lockfiles or manifests; flagged with confidence score (exact, declared_range, inferred). | components[].version | packages[].packageVersion |
| **Other Unique Identifiers** | Canonical pointers such as Package URL (PURL) or CPE. | Generated canonical PURLs per standard (pkg:npm/..., pkg:pypi/..., pkg:maven/...). | components[].purl | packages[].externalRefs[referenceType="purl"] |
| **Dependency Relationship** | Characterization of relationship between software modules. | Dual synthesis: direct declarations vs transitive DAG links. | dependencies[].ref + dependencies[].dependsOn[] | elationships[relationshipType="DEPENDS_ON"] |
| **Author of SBOM Data** | The tool or organization producing the manifest. | Stamped automatically as CodeSupply-1.2.0 under Smart India Hackathon (SIH1449). | metadata.tools.components[] | creationInfo.creators |
| **Timestamp** | Exact date and time when the SBOM data was assembled. | UTC timestamp in ISO 8601 format generated at completion of analysis. | metadata.timestamp | creationInfo.created |

---

## 2. Operational & Process Considerations

### Frequency of Generation
- **Requirement**: SBOM must be updated whenever software components change.
- **CodeSupply**: Automatic re-generation on every repository commit or archive upload; includes **Diff & Drift Analysis** (/scans/compare) to highlight version increments, added libraries, and emerging CVEs between builds.

### Depth of Dependencies
- **Requirement**: All primary dependencies must be traversed down to all transitive layers until terminal nodes.
- **CodeSupply**: Native lockfile parsers (package-lock.json v1/v2/v3, Cargo.lock, go.mod indirects) reconstruct complete recursive trees, eliminating supply-chain blind spots.

### Known Unknowns
- **Requirement**: The SBOM must explicitly disclose where dependencies could not be resolved or version data is missing.
- **CodeSupply**: Built-in **Version Confidence Engine** tags unresolved ranges as declared_range or unknown, and surfaces them in the UI and executive audit reports as *"Unresolved Version Disclosures"*.

---

## 3. Cryptographic Verification & Standard Formats

CodeSupply exports in two universally recognized machine-readable formats:
1. **OWASP CycloneDX 1.7 JSON**: Optimized for application security and automated vulnerability ingestion.
2. **Linux Foundation SPDX 2.3 JSON**: International Standard **ISO/IEC 5962:2021** optimized for software supply-chain governance, licensing, and intellectual property compliance.
