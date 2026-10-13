"""VM92 artifact-class boundaries without policy labels or new cases."""

import json
from fractions import Fraction as F
from pathlib import Path

import pytest

from studies.artifact_evidence import (
    bounded, claim_decision, displayed, exact,
)
from studies.vm92_artifact_evidence import build, table

ROOT = Path(__file__).resolve().parents[1]


def test_display_ties_and_open_ends_are_declared():
    nearest = displayed(336, 1, "nearest_half_away_from_zero")
    assert nearest.contains(F(671, 2))  # 335.5 rounds away from zero to 336.
    assert not nearest.contains(F(673, 2))  # 336.5 rounds to 337.
    truncate = displayed(336, 1, "truncate_toward_zero")
    assert truncate.contains(336)
    assert not truncate.contains(337)
    negative = displayed(-336, 1, "nearest_half_away_from_zero")
    assert not negative.contains(F(-673, 2))
    assert negative.contains(F(-671, 2))
    assert not displayed(0, 1, "truncate_toward_zero").contains(1)
    with pytest.raises(ValueError, match="rounding convention"):
        displayed(336, 1, "unknown")


def test_acceptance_error_output_error_and_reference_error_stay_separate():
    assert claim_decision(exact(0), exact(0), 0) == "accept"
    assert claim_decision(bounded(0, 1), exact(0), 0) == "ambiguous"
    assert claim_decision(exact(0), bounded(0, 1), 0) == "ambiguous"
    assert claim_decision(bounded(0, 1), exact(0), 1) == "accept"
    assert claim_decision(exact(2), exact(0), 1) == "reject"
    assert claim_decision(exact(1), exact(0), 1) == "accept"
    assert claim_decision(exact(F(1001, 1000)), exact(0), 1) == "reject"
    with pytest.raises(ValueError, match="nonnegative"):
        bounded(0, -1)


def test_vm92_exact_control_and_unknown_display_convention():
    result = build()
    assert result["reference_exact_F"] == "30640/91"
    assert result["heat_rate_exact_Btu_per_hr"] == "46720/91"
    assert result["exact_control_decision"] == "accept"
    assert result["unknown_convention_source_compatibility"] == "ambiguous"
    modes = result["possible_display_conventions"]
    assert not modes["nearest_half_away_from_zero"]["exact_reference_compatible"]
    assert modes["truncate_toward_zero"]["exact_reference_compatible"]
    assert modes["truncate_toward_zero"]["claim_decision_if_this_were_an_artifact"] == "ambiguous"
    assert result["illustrative_solver"]["decision"] == "ambiguous"


def test_committed_vm92_artifact_result_reproduces():
    result = build()
    out = ROOT / "reports/vm92-artifact-evidence"
    assert result == json.loads((out / "results.json").read_text())
    assert table(result) == (out / "matrix.md").read_text()
