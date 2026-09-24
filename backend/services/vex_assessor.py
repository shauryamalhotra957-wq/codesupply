"""
VEX (Vulnerability Exploitability eXchange) Assessment Engine.
Provides automated justification scoring and exploitability status mapping
according to CycloneDX v1.5 and v1.6 VEX standards.
"""
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class VexStatus(str, Enum):
    NOT_AFFECTED = "not_affected"
    AFFECTED = "affected"
    FIXED = "fixed"
    UNDER_INVESTIGATION = "under_investigation"

class VexJustification(str, Enum):
    CODE_NOT_PRESENT = "code_not_present"
    CODE_NOT_REACHABLE = "code_not_reachable"
    REQUIRES_CONFIGURATION = "requires_configuration"
    REQUIRES_DEPENDENCY = "requires_dependency"
    REQUIRES_ENVIRONMENT = "requires_environment"
    PROTECTED_BY_COMPILER = "protected_by_compiler"
    PROTECTED_AT_RUNTIME = "protected_at_runtime"
    PROTECTED_AT_PERIMETER = "protected_at_perimeter"
    PROTECTED_BY_MITIGATING_CONTROL = "protected_by_mitigating_control"

class VexStatement(BaseModel):
    vulnerability_id: str
    component_name: str
    status: VexStatus
    justification: Optional[VexJustification] = None
    detail: str
    remediation: Optional[str] = None

class VexEngine:
    """Evaluates component call-graph reachability and outputs VEX statements."""

    @staticmethod
    def assess_vulnerability(
        vuln_id: str,
        component_name: str,
        is_imported: bool,
        is_called_in_runtime: bool,
        has_runtime_guard: bool = False
    ) -> VexStatement:
        if not is_imported:
            return VexStatement(
                vulnerability_id=vuln_id,
                component_name=component_name,
                status=VexStatus.NOT_AFFECTED,
                justification=VexJustification.CODE_NOT_PRESENT,
                detail=f"Package {component_name} is in dependencies but never imported in active execution paths."
            )
        
        if not is_called_in_runtime:
            return VexStatement(
                vulnerability_id=vuln_id,
                component_name=component_name,
                status=VexStatus.NOT_AFFECTED,
                justification=VexJustification.CODE_NOT_REACHABLE,
                detail=f"Package {component_name} is imported but the vulnerable functions are not reachable in the call-graph."
            )
        
        if has_runtime_guard:
            return VexStatement(
                vulnerability_id=vuln_id,
                component_name=component_name,
                status=VexStatus.NOT_AFFECTED,
                justification=VexJustification.PROTECTED_AT_RUNTIME,
                detail=f"Vulnerable function in {component_name} is shielded by input validation sanitizer or runtime firewall."
            )

        return VexStatement(
            vulnerability_id=vuln_id,
            component_name=component_name,
            status=VexStatus.AFFECTED,
            justification=None,
            detail=f"Component {component_name} contains reachable vulnerability {vuln_id}. Immediate patch required.",
            remediation=f"Upgrade {component_name} to the latest non-vulnerable patched release."
        )
