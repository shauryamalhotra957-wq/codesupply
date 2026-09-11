"""Tests for the License Compliance and Risk Classification Policy Engine."""

from app.risk.license_policy import LicenseCategory, LicensePolicyEngine


def test_permissive_license_classification():
    mit = LicensePolicyEngine.evaluate("MIT")
    assert mit.category == LicenseCategory.PERMISSIVE
    assert mit.is_viral is False
    assert mit.commercial_friendly is True
    assert mit.requires_source_distribution is False

    apache = LicensePolicyEngine.evaluate("Apache-2.0")
    assert apache.category == LicenseCategory.PERMISSIVE
    assert apache.commercial_friendly is True

    bsd = LicensePolicyEngine.evaluate("BSD-3-Clause")
    assert bsd.category == LicenseCategory.PERMISSIVE


def test_strong_copyleft_classification():
    gpl3 = LicensePolicyEngine.evaluate("GPL-3.0")
    assert gpl3.category == LicenseCategory.STRONG_COPYLEFT
    assert gpl3.is_viral is True
    assert gpl3.commercial_friendly is False
    assert gpl3.requires_source_distribution is True

    agpl = LicensePolicyEngine.evaluate("AGPL-3.0")
    assert agpl.category == LicenseCategory.STRONG_COPYLEFT
    assert agpl.is_viral is True


def test_weak_copyleft_classification():
    mpl = LicensePolicyEngine.evaluate("MPL-2.0")
    assert mpl.category == LicenseCategory.WEAK_COPYLEFT
    assert mpl.is_viral is False
    assert mpl.requires_source_distribution is True

    lgpl = LicensePolicyEngine.evaluate("LGPL-2.1")
    assert lgpl.category == LicenseCategory.WEAK_COPYLEFT


def test_unknown_or_missing_license():
    none_lic = LicensePolicyEngine.evaluate(None)
    assert none_lic.category == LicenseCategory.UNKNOWN
    assert none_lic.spdx_id == "UNKNOWN"

    empty_lic = LicensePolicyEngine.evaluate("")
    assert empty_lic.category == LicenseCategory.UNKNOWN

    custom_lic = LicensePolicyEngine.evaluate("Proprietary-Acme-Corp-License")
    assert custom_lic.category == LicenseCategory.UNKNOWN
