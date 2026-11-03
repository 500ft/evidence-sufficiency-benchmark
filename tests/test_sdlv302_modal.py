import hashlib
import json
from pathlib import Path

from studies.sdlv302_modal.reference import energy_matrix_hz, source_formula_hz
from studies.sdlv302_modal.run import build


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "studies/sdlv302_modal/spec.json"
RESULT = ROOT / "reports/sdlv302-modal/results.json"


def test_registered_result_reproduces_and_keeps_source_contradictions_visible():
    saved = json.loads(RESULT.read_text())
    reproduced = build()
    assert saved["spec_sha256"] == hashlib.sha256(SPEC.read_bytes()).hexdigest()
    for actual, expected in zip(reproduced["flexural_modes"], saved["flexural_modes"]):
        assert actual["flexural_n"] == expected["flexural_n"]
        for key in ("source_expression_Hz", "independent_energy_matrix_Hz",
                    "route_difference_Hz", "eigen_residual_relative"):
            assert abs(actual[key] - expected[key]) < 1e-9
    assert all(reproduced["checks"].values())
    assert saved["source_display_inertia_diagnostic"]["printed_value_matches_derived_section"] is False
    assert saved["fourth_display_interval_excludes_derived"] is True


def test_inertia_display_cannot_explain_published_first_mode():
    spec = json.loads(SPEC.read_text())
    p = spec["geometry_and_material"]
    L, h, width, E, nu, rho = (p[k] for k in
        ("L_m", "h_m", "b_m", "E_Pa", "nu", "rho_kg_per_m3"))
    A, I, G = width*h, width*h**3/12, E/(2*(1+nu))
    args = (1, L, A, I, E, G, rho, 5/6)
    derived = source_formula_hz(*args)
    independently_derived, residual = energy_matrix_hz(*args)
    lo, hi = spec["claim"]["published_display_interval_Hz"]
    assert lo <= derived < hi
    assert lo <= independently_derived < hi
    assert residual < 1e-11
    printed = json.loads(RESULT.read_text())["source_display_inertia_diagnostic"]["printed_numeric_value_m4_if_reinterpreted"]
    from_printed = source_formula_hz(1, L, A, printed, E, G, rho, 5/6)
    assert not lo <= from_printed < hi
