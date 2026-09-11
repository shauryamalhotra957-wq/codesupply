"""Software Supply Chain License Compliance and Risk Classification Policy Engine."""

from dataclasses import dataclass
from enum import Enum


class LicenseCategory(str, Enum):
    PERMISSIVE = "permissive"
    WEAK_COPYLEFT = "weak_copyleft"
    STRONG_COPYLEFT = "strong_copyleft"
    PROPRIETARY = "proprietary"
    UNKNOWN = "unknown"


@dataclass
class LicenseAssessment:
    spdx_id: str
    category: LicenseCategory
    is_viral: bool
    commercial_friendly: bool
    requires_source_distribution: bool
    description: str


class LicensePolicyEngine:
    """Classifies licenses based on intellectual property risk and copyleft obligations."""

    PERMISSIVE_LICENSES = {
        "mit": "MIT License - highly permissive, commercial-friendly",
        "apache-2.0": "Apache 2.0 - permissive with explicit patent grant",
        "bsd-2-clause": "Simplified BSD License - permissive",
        "bsd-3-clause": "Modified BSD License - permissive with no-endorsement clause",
        "isc": "ISC License - functionally equivalent to MIT",
        "cc0-1.0": "Creative Commons Zero - public domain dedication",
        "unlicense": "The Unlicense - public domain dedication",
        "0bsd": "Zero-Clause BSD - fully public domain equivalent",
    }

    WEAK_COPYLEFT_LICENSES = {
        "lgpl-2.1": "GNU Lesser General Public License 2.1 - copyleft limited to library modifications",
        "lgpl-3.0": "GNU Lesser General Public License 3.0 - copyleft limited to library modifications",
        "mpl-2.0": "Mozilla Public License 2.0 - file-level copyleft",
        "epl-1.0": "Eclipse Public License 1.0 - module-level copyleft",
        "epl-2.0": "Eclipse Public License 2.0 - module-level copyleft",
        "cddl-1.0": "Common Development and Distribution License - file-level copyleft",
    }

    STRONG_COPYLEFT_LICENSES = {
        "gpl-2.0": "GNU General Public License 2.0 - strong copyleft, mandates source distribution of linked code",
        "gpl-3.0": "GNU General Public License 3.0 - strong copyleft with patent & anti-tivoization clauses",
        "agpl-3.0": "GNU Affero General Public License 3.0 - network-triggered copyleft",
        "sspl-1.0": "Server Side Public License - source disclosure triggered by cloud/network hosting",
    }

    @classmethod
    def evaluate(cls, raw_license: str | None) -> LicenseAssessment:
        """Evaluate a license string and return full compliance assessment."""
        if not raw_license or raw_license.strip().lower() in ("unknown", "none", ""):
            return LicenseAssessment(
                spdx_id="UNKNOWN",
                category=LicenseCategory.UNKNOWN,
                is_viral=False,
                commercial_friendly=False,
                requires_source_distribution=False,
                description="License undeclared or unidentified; represents unresolved legal risk.",
            )

        clean = raw_license.strip().lower()

        # Check Permissive
        for lic, desc in cls.PERMISSIVE_LICENSES.items():
            if lic in clean or clean in lic:
                return LicenseAssessment(
                    spdx_id=raw_license,
                    category=LicenseCategory.PERMISSIVE,
                    is_viral=False,
                    commercial_friendly=True,
                    requires_source_distribution=False,
                    description=desc,
                )

        # Check Weak Copyleft
        for lic, desc in cls.WEAK_COPYLEFT_LICENSES.items():
            if lic in clean:
                return LicenseAssessment(
                    spdx_id=raw_license,
                    category=LicenseCategory.WEAK_COPYLEFT,
                    is_viral=False,
                    commercial_friendly=True,
                    requires_source_distribution=True,
                    description=desc,
                )

        # Check Strong Copyleft
        for lic, desc in cls.STRONG_COPYLEFT_LICENSES.items():
            if lic in clean:
                return LicenseAssessment(
                    spdx_id=raw_license,
                    category=LicenseCategory.STRONG_COPYLEFT,
                    is_viral=True,
                    commercial_friendly=False,
                    requires_source_distribution=True,
                    description=desc,
                )

        return LicenseAssessment(
            spdx_id=raw_license,
            category=LicenseCategory.UNKNOWN,
            is_viral=False,
            commercial_friendly=True,
            requires_source_distribution=False,
            description=f"Custom or unclassified license: {raw_license}",
        )
