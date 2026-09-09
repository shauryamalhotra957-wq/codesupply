"""SBOM exporter abstraction with CycloneDX implementation."""

from abc import ABC, abstractmethod

from app.sbom.generator import CycloneDXGenerator
from app.sbom.validator import SBOMValidationResultData, SBOMValidator


class SBOMExporter(ABC):
    """Abstract base for SBOM exporters."""

    @abstractmethod
    def export(self, scan, components, edges) -> tuple[dict, SBOMValidationResultData]:
        """Generate and validate an SBOM."""
        ...

    @abstractmethod
    def get_format(self) -> str: ...

    @abstractmethod
    def get_spec_version(self) -> str: ...


class CycloneDXExporter(SBOMExporter):
    """CycloneDX 1.7 SBOM exporter."""

    def __init__(self):
        self.generator = CycloneDXGenerator()
        self.validator = SBOMValidator()

    def export(self, scan, components, edges) -> tuple[dict, SBOMValidationResultData]:
        """Generate CycloneDX SBOM and validate it.

        Returns:
            (sbom_dict, validation_result)
        """
        sbom_dict = self.generator.generate(scan, components, edges)
        validation = self.validator.validate(sbom_dict)
        return sbom_dict, validation

    def get_format(self) -> str:
        return "CycloneDX"

    def get_spec_version(self) -> str:
        return "1.7"
