import pytest
from services.vex_assessor import VexEngine, VexStatus, VexJustification

def test_vex_assessor_code_not_present():
    statement = VexEngine.assess_vulnerability(
        vuln_id="CVE-2026-1234",
        component_name="requests",
        is_imported=False,
        is_called_in_runtime=False
    )
    assert statement.status == VexStatus.NOT_AFFECTED
    assert statement.justification == VexJustification.CODE_NOT_PRESENT

def test_vex_assessor_code_not_reachable():
    statement = VexEngine.assess_vulnerability(
        vuln_id="CVE-2026-5678",
        component_name="pillow",
        is_imported=True,
        is_called_in_runtime=False
    )
    assert statement.status == VexStatus.NOT_AFFECTED
    assert statement.justification == VexJustification.CODE_NOT_REACHABLE

def test_vex_assessor_protected_at_runtime():
    statement = VexEngine.assess_vulnerability(
        vuln_id="CVE-2026-9999",
        component_name="sqlparse",
        is_imported=True,
        is_called_in_runtime=True,
        has_runtime_guard=True
    )
    assert statement.status == VexStatus.NOT_AFFECTED
    assert statement.justification == VexJustification.PROTECTED_AT_RUNTIME

def test_vex_assessor_affected_with_remediation():
    statement = VexEngine.assess_vulnerability(
        vuln_id="CVE-2026-4444",
        component_name="urllib3",
        is_imported=True,
        is_called_in_runtime=True,
        has_runtime_guard=False
    )
    assert statement.status == VexStatus.AFFECTED
    assert statement.justification is None
    assert statement.remediation is not None
