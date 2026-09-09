"""CycloneDX SBOM structural validator."""

from dataclasses import dataclass, field


@dataclass
class SBOMValidationResultData:
    """Result of SBOM validation."""

    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class SBOMValidator:
    """Validate CycloneDX SBOM against structural requirements.

    Checks:
    1. Required top-level fields (bomFormat, specVersion)
    2. Correct specVersion value
    3. Valid serialNumber format
    4. Component required fields (type, name)
    5. PURL format validation
    6. bom-ref uniqueness
    7. Dependency ref integrity (all refs point to valid bom-refs)
    """

    REQUIRED_TOP_LEVEL = {"bomFormat", "specVersion"}
    REQUIRED_COMPONENT_FIELDS = {"type", "name"}

    def validate(self, sbom_dict: dict) -> SBOMValidationResultData:
        """Validate the SBOM document."""
        result = SBOMValidationResultData()

        if not isinstance(sbom_dict, dict):
            result.is_valid = False
            result.errors.append("SBOM must be a JSON object")
            return result

        # Check required top-level fields
        for field_name in self.REQUIRED_TOP_LEVEL:
            if field_name not in sbom_dict:
                result.is_valid = False
                result.errors.append(f"Missing required field: {field_name}")

        # Validate bomFormat
        if sbom_dict.get("bomFormat") != "CycloneDX":
            result.is_valid = False
            result.errors.append(f"bomFormat must be 'CycloneDX', got '{sbom_dict.get('bomFormat')}'")

        # Validate specVersion
        spec_version = sbom_dict.get("specVersion")
        if spec_version and spec_version != "1.7":
            result.warnings.append(f"specVersion is '{spec_version}', expected '1.7'")

        # Validate serialNumber
        serial = sbom_dict.get("serialNumber")
        if serial and not serial.startswith("urn:uuid:"):
            result.warnings.append(f"serialNumber should be in urn:uuid: format, got '{serial}'")

        # Validate version
        version = sbom_dict.get("version")
        if version is not None and not isinstance(version, int):
            result.warnings.append(f"version should be an integer, got {type(version).__name__}")

        # Collect all bom-refs for reference integrity checking
        all_bom_refs: set[str] = set()
        duplicate_refs: list[str] = []

        # Check metadata
        metadata = sbom_dict.get("metadata", {})
        if metadata:
            meta_comp = metadata.get("component", {})
            if meta_comp:
                ref = meta_comp.get("bom-ref")
                if ref:
                    all_bom_refs.add(ref)

        # Validate components
        components = sbom_dict.get("components", [])
        if not isinstance(components, list):
            result.is_valid = False
            result.errors.append("components must be an array")
        else:
            for i, comp in enumerate(components):
                if not isinstance(comp, dict):
                    result.is_valid = False
                    result.errors.append(f"components[{i}] must be an object")
                    continue

                # Required fields
                for field_name in self.REQUIRED_COMPONENT_FIELDS:
                    if field_name not in comp:
                        result.is_valid = False
                        result.errors.append(f"components[{i}].{field_name} is required")

                # bom-ref uniqueness
                bom_ref = comp.get("bom-ref")
                if bom_ref:
                    if bom_ref in all_bom_refs:
                        duplicate_refs.append(bom_ref)
                    all_bom_refs.add(bom_ref)

                # PURL validation
                purl = comp.get("purl")
                if purl and not purl.startswith("pkg:"):
                    result.is_valid = False
                    result.errors.append(f"components[{i}].purl must start with 'pkg:', got '{purl[:50]}'")

                # Valid component type
                comp_type = comp.get("type")
                valid_types = {
                    "application",
                    "framework",
                    "library",
                    "container",
                    "platform",
                    "device",
                    "firmware",
                    "file",
                    "machine-learning-model",
                    "data",
                }
                if comp_type and comp_type not in valid_types:
                    result.warnings.append(
                        f"components[{i}].type '{comp_type}' is not a standard CycloneDX component type"
                    )

        if duplicate_refs:
            result.is_valid = False
            result.errors.append(f"Duplicate bom-ref values: {', '.join(duplicate_refs[:5])}")

        # Validate dependencies
        dependencies = sbom_dict.get("dependencies", [])
        if isinstance(dependencies, list):
            for i, dep in enumerate(dependencies):
                if not isinstance(dep, dict):
                    result.is_valid = False
                    result.errors.append(f"dependencies[{i}] must be an object")
                    continue

                ref = dep.get("ref")
                if ref and ref not in all_bom_refs:
                    result.warnings.append(f"dependencies[{i}].ref '{ref}' does not match any component bom-ref")

                depends_on = dep.get("dependsOn", [])
                if isinstance(depends_on, list):
                    for target_ref in depends_on:
                        if target_ref not in all_bom_refs:
                            result.warnings.append(
                                f"dependencies[{i}].dependsOn contains '{target_ref}' which does not match any component bom-ref"
                            )

        return result
