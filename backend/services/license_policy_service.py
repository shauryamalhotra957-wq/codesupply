import re
from typing import Any, Dict, List, Optional


class LicensePolicyService:
    """
    Evaluates license compliance, copyleft contamination risks, and license compatibility
    across discovered dependencies.
    """

    PERMISSIVE = {
        "mit",
        "apache-2.0",
        "apache 2.0",
        "bsd-2-clause",
        "bsd-3-clause",
        "bsd",
        "isc",
        "cc0-1.0",
        "unlicense",
        "python-2.0",
        "zlib",
        "0bsd",
        "wtfpl",
    }

    WEAK_COPYLEFT = {
        "lgpl-2.0",
        "lgpl-2.1",
        "lgpl-3.0",
        "mpl-1.1",
        "mpl-2.0",
        "epl-1.0",
        "epl-2.0",
        "cddl-1.0",
    }

    STRONG_COPYLEFT = {
        "gpl-2.0",
        "gpl-3.0",
        "agpl-3.0",
        "eupl-1.2",
        "sspl-1.0",
    }

    PROPRIETARY = {
        "proprietary",
        "commercial",
        "all rights reserved",
    }

    @classmethod
    def categorize_license(cls, raw_license: Optional[str]) -> str:
        """Returns category: permissive, weak_copyleft, strong_copyleft, proprietary, or unknown."""
        if not raw_license:
            return "unknown"

        lic = raw_license.strip().lower()
        # Clean up common prefixes / punctuation
        lic_clean = re.sub(r"[()]", "", lic).strip()

        for perm in cls.PERMISSIVE:
            if perm in lic_clean:
                return "permissive"

        for weak in cls.WEAK_COPYLEFT:
            if weak in lic_clean:
                return "weak_copyleft"

        for strong in cls.STRONG_COPYLEFT:
            if strong in lic_clean:
                return "strong_copyleft"

        for prop in cls.PROPRIETARY:
            if prop in lic_clean:
                return "proprietary"

        return "unknown"

    @classmethod
    def evaluate_project_licenses(cls, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes component licenses and returns distribution, risk flags, and copyleft warnings.
        """
        category_counts = {
            "permissive": 0,
            "weak_copyleft": 0,
            "strong_copyleft": 0,
            "proprietary": 0,
            "unknown": 0,
        }
        high_risk_components: List[Dict[str, Any]] = []

        for comp in components:
            raw_lic = comp.get("license") or ""
            cat = cls.categorize_license(raw_lic)
            category_counts[cat] = category_counts.get(cat, 0) + 1

            if cat == "strong_copyleft":
                high_risk_components.append(
                    {
                        "name": comp.get("name"),
                        "version": comp.get("version"),
                        "license": raw_lic,
                        "risk": "Strong Copyleft (Viral GPL/AGPL constraint on downstream distribution)",
                        "severity": "HIGH",
                    }
                )
            elif cat == "unknown":
                high_risk_components.append(
                    {
                        "name": comp.get("name"),
                        "version": comp.get("version"),
                        "license": "Unspecified",
                        "risk": "Missing license metadata (potential legal ambiguity)",
                        "severity": "LOW",
                    }
                )

        compliance_score = 100
        if category_counts["strong_copyleft"] > 0:
            compliance_score -= min(40, category_counts["strong_copyleft"] * 15)
        if category_counts["weak_copyleft"] > 0:
            compliance_score -= min(15, category_counts["weak_copyleft"] * 5)
        if category_counts["unknown"] > 0:
            compliance_score -= min(20, category_counts["unknown"] * 2)

        compliance_score = max(0, compliance_score)

        return {
            "compliance_score": compliance_score,
            "distribution": category_counts,
            "risk_flags": high_risk_components,
            "total_evaluated": len(components),
        }
