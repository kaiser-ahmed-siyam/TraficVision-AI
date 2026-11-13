"""Acceptance checks for project documentation and licensing files."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_readme_documents_verified_phase_one_usage():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8").lower()

    for phrase in (
        "python 3.11",
        "streamlit run app.py",
        "pytest",
        "cpu",
        "local-only",
        "phase 1",
    ):
        assert phrase in readme


def test_project_includes_agpl_license_and_third_party_notices():
    license_text = (PROJECT_ROOT / "LICENSE").read_text(encoding="utf-8")

    assert "GNU AFFERO GENERAL PUBLIC LICENSE" in license_text
    assert "Version 3" in license_text
    assert (PROJECT_ROOT / "THIRD_PARTY_NOTICES.md").is_file()
