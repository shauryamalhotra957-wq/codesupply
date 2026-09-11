import argparse
import json
import sys
from pathlib import Path

from app.scanners.discovery import discover_manifests
from app.scanners.go.parser import GoParser
from app.scanners.maven.parser import MavenParser
from app.scanners.npm.parser import NpmParser
from app.scanners.python.parser import PythonParser
from app.scanners.rust.parser import RustParser
from app.services.normalizer import ComponentNormalizer
from app.services.relationships import RelationshipBuilder


def print_banner():
    print("""
  +--------------------------------------------------------------+
  |         CodeSupply - Supply-Chain Security Platform          |
  |         CycloneDX 1.7 * SPDX 2.3 * Vulnerability Engine      |
  +--------------------------------------------------------------+
    """)


def scan_directory(
    target_path: Path,
    export_sbom: str | None = None,
    sbom_format: str = "cyclonedx",
    export_csv: str | None = None,
):
    target_path = target_path.resolve()
    if not target_path.exists():
        print(f"Error: Target path '{target_path}' does not exist.")
        sys.exit(1)

    print(f"[*] Discovering manifests in: {target_path} ...")
    manifests = discover_manifests(target_path)
    supported = [m for m in manifests if m.is_supported]

    print(f"[+] Found {len(manifests)} manifest(s) ({len(supported)} supported ecosystem manifests)")
    for m in supported:
        print(f"    - {m.ecosystem:7s} | {m.path} ({m.manifest_type})")

    npm_parser = NpmParser()
    py_parser = PythonParser()
    mvn_parser = MavenParser()
    go_parser = GoParser()
    rust_parser = RustParser()

    all_packages = []
    all_relationships = []
    npm_declarations = []
    npm_lockfile_pkgs = []
    npm_lockfile_rels = []
    cargo_declarations = []
    cargo_lockfile_pkgs = []
    cargo_lockfile_rels = []

    for m in supported:
        file_path = target_path / m.path
        if not file_path.exists():
            continue
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            file_name = file_path.name

            if m.ecosystem == "npm":
                if file_name == "package.json":
                    pkgs, rels = npm_parser.parse_package_json(content, m.path)
                    npm_declarations.extend(pkgs)
                    all_relationships.extend(rels)
                elif file_name == "package-lock.json":
                    pkgs, rels = npm_parser.parse_package_lock(content, m.path)
                    npm_lockfile_pkgs.extend(pkgs)
                    npm_lockfile_rels.extend(rels)
            elif m.ecosystem == "python":
                if file_name == "requirements.txt":
                    all_packages.extend(py_parser.parse_requirements_txt(content, m.path))
                elif file_name == "pyproject.toml":
                    all_packages.extend(py_parser.parse_pyproject_toml(content, m.path))
            elif m.ecosystem == "maven":
                all_packages.extend(mvn_parser.parse_pom_xml(content, m.path))
            elif m.ecosystem == "golang":
                pkgs, rels = go_parser.parse_go_mod(content, m.path)
                all_packages.extend(pkgs)
                all_relationships.extend(rels)
            elif m.ecosystem == "cargo":
                if file_name == "Cargo.toml":
                    cargo_declarations.extend(rust_parser.parse_cargo_toml(content, m.path))
                elif file_name == "Cargo.lock":
                    pkgs, rels = rust_parser.parse_cargo_lock(content, m.path)
                    cargo_lockfile_pkgs.extend(pkgs)
                    cargo_lockfile_rels.extend(rels)
        except Exception as e:
            print(f"[!] Warning: Failed to parse {m.path}: {e}")

    if npm_lockfile_pkgs:
        merged_pkgs, merged_rels = npm_parser.merge_declarations_with_lockfile(
            npm_declarations, npm_lockfile_pkgs, npm_lockfile_rels
        )
        all_packages.extend(merged_pkgs)
        all_relationships.extend(merged_rels)
    else:
        all_packages.extend(npm_declarations)

    if cargo_lockfile_pkgs:
        merged_c, merged_r = rust_parser.merge_manifest_with_lockfile(
            cargo_declarations, cargo_lockfile_pkgs, cargo_lockfile_rels
        )
        all_packages.extend(merged_c)
        all_relationships.extend(merged_r)
    else:
        all_packages.extend(cargo_declarations)

    from app.models.models import Component, DependencyEdge

    normalizer = ComponentNormalizer()
    components: list[Component] = []
    component_map: dict[str, str] = {}

    for pkg in all_packages:
        comp_data, _ = normalizer.normalize(pkg, scan_id="cli_scan")
        comp = Component(
            id=comp_data["id"],
            scan_id="cli_scan",
            name=comp_data["name"],
            version=comp_data["version"],
            ecosystem=comp_data["ecosystem"],
            package_manager=comp_data["package_manager"],
            dependency_type=comp_data["dependency_type"],
            source_file=comp_data["source_file"],
            source_location=comp_data.get("source_location"),
            version_confidence=comp_data["version_confidence"],
            purl=comp_data.get("purl"),
            original_declaration=comp_data.get("original_declaration"),
            normalized_name=comp_data["normalized_name"],
            risk_level="unknown",
            license=comp_data.get("license"),
        )
        components.append(comp)
        component_map[comp.normalized_name] = comp.id

    rel_builder = RelationshipBuilder()
    raw_edges, _ = rel_builder.build_edges(all_relationships, component_map, scan_id="cli_scan")
    edges = [
        DependencyEdge(
            id=e["id"],
            scan_id="cli_scan",
            source_component_id=e["source_component_id"],
            target_component_id=e["target_component_id"],
            relationship_type=e["relationship_type"],
            confidence=e["confidence"],
            source_file=e["source_file"],
            evidence_method=e["evidence_method"],
        )
        for e in raw_edges
    ]

    direct_count = sum(1 for c in components if c.dependency_type == "direct")
    transitive_count = len(components) - direct_count

    print("\n" + "=" * 62)
    print("                SCAN AUDIT SUMMARY RESULTS                ")
    print("=" * 62)
    print(f"  Total Components Analyzed : {len(components)}")
    print(f"  Direct Dependencies       : {direct_count}")
    print(f"  Transitive Dependencies   : {transitive_count}")
    print(f"  Dependency Edges Resolved : {len(edges)}")
    print("=" * 62)

    # Display Top sample components
    print("\n  Sample Components Inventory:")
    print(f"  {'Ecosystem':<10} {'Name':<28} {'Version':<14} {'Type':<10}")
    print("  " + "-" * 64)
    for c in components[:12]:
        print(f"  {c.ecosystem:<10} {c.name[:27]:<28} {c.version or 'unresolved':<14} {c.dependency_type:<10}")

    if len(components) > 12:
        print(f"  ... and {len(components) - 12} more components")

    if export_sbom:
        out_path = Path(export_sbom)
        from app.models.models import Scan

        mock_scan = Scan(id="cli_scan", filename=target_path.name, project_name=target_path.name)
        if sbom_format.lower() == "spdx":
            from app.sbom.spdx import SPDX23Generator

            generator = SPDX23Generator()
            sbom_data = generator.generate(mock_scan, components, edges)
        else:
            from app.sbom.generator import CycloneDXGenerator

            generator = CycloneDXGenerator()
            sbom_data = generator.generate(mock_scan, components, edges)

        out_path.write_text(json.dumps(sbom_data, indent=2))
        print(f"\n[OK] Exported {sbom_format.upper()} SBOM to: {out_path.resolve()}")

    if export_csv:
        import csv

        csv_path = Path(export_csv)
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "version", "ecosystem", "dependency_type", "purl", "risk_level", "license"])
            for c in components:
                writer.writerow(
                    [
                        c.name,
                        c.version or "",
                        c.ecosystem,
                        c.dependency_type,
                        c.purl or "",
                        c.risk_level or "none",
                        c.license or "UNKNOWN",
                    ]
                )
        print(f"\n[OK] Exported CSV Inventory to: {csv_path.resolve()}")

    print("\n[OK] Scan completed successfully.\n")


def main():
    print_banner()
    parser = argparse.ArgumentParser(description="CodeSupply - Software Supply-Chain Intelligence CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    scan_parser = subparsers.add_parser("scan", help="Scan a directory or project archive for dependencies")
    scan_parser.add_argument("path", help="Path to project directory")
    scan_parser.add_argument("--export-sbom", help="Save generated SBOM to specified file path")
    scan_parser.add_argument(
        "--format", choices=["cyclonedx", "spdx"], default="cyclonedx", help="SBOM output format (default: cyclonedx)"
    )
    scan_parser.add_argument("--export-csv", help="Save components inventory to specified CSV file path")

    subparsers.add_parser("version", help="Show CodeSupply platform version")

    args = parser.parse_args()

    if args.command == "scan":
        scan_directory(
            Path(args.path),
            export_sbom=args.export_sbom,
            sbom_format=args.format,
            export_csv=args.export_csv,
        )
    elif args.command == "version":
        print("CodeSupply v1.3.0 (CycloneDX 1.7, SPDX 2.3 & VEX Ready)")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
