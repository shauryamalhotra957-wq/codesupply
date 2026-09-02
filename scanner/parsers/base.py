from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ParsedDependency:
    """Represents a dependency parsed directly from a manifest or lockfile."""
    name: str
    version: Optional[str] = None
    specifier: Optional[str] = None
    ecosystem: str = "unknown"
    direct: bool = True
    source_file: str = ""
    scope: str = "required"  # required, dev, optional
    license: Optional[str] = None
    integrity: Optional[str] = None
    resolved_url: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "specifier": self.specifier,
            "ecosystem": self.ecosystem,
            "direct": self.direct,
            "source_file": self.source_file,
            "scope": self.scope,
            "license": self.license,
            "integrity": self.integrity,
            "resolved_url": self.resolved_url,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
        }


class BaseParser(ABC):
    """Abstract base class for manifest and lockfile parsers."""

    @abstractmethod
    def can_parse(self, filename: str) -> bool:
        """Check if this parser handles the given filename."""
        pass

    @abstractmethod
    def parse(self, file_path: Path, relative_path: str) -> List[ParsedDependency]:
        """Parse dependencies from the given file."""
        pass
