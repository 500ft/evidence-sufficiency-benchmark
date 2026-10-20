"""Independent route, boundary and retained-failure checks for Kirsch development."""
import json
from math import isclose
from pathlib import Path

import pytest

from studies.kirsch_reference.reference import Jet, airy_cartesian, polar, polar_cartesian, traction
from studies.kirsch_reference.run import build

ROOT = Path(__file__).resolve().parents[1]


def test_airy_jet_is_a_second_derivative_route():
    x, y = Jet(2, x=1), Jet(3, y=1)
    f = x*x*y*y
    assert (f.xx, f.xy, f.yy) == (18, 24, 8)
    for point in ((1,0),(0,1),(1.2,1.3),(5,2.5)):
        p = polar_cartesian(*point, 1, 10)
        a = airy_cartesian(*point, 1, 10)
        assert all(isclose(u,v,abs_tol=1e-11) for u,v in zip(p,a))
    with pytest.raises(ValueError, match="outside"):
        airy_cartesian(0.5,0,1,10)


def test_exact_hole_and_nonuniform_outer_shear():
    assert polar(1,0,1,10) == (0,30,0)
    assert polar(0,1,1,10) == (0,-10,0)
    xx, yy, xy = airy_cartesian(5,2.5,1,10)
    assert abs(xy) > 0.1
    assert traction((xx,yy,xy),1,0)[1] == xy
    assert airy_cartesian(1,0,1,0) == (0,0,0)


def test_committed_result_and_pilot_failure_are_preserved():
    results = build()
    assert results == json.loads((ROOT/"reports/kirsch-reference/results.json").read_text())
    pilot = json.loads((ROOT/"reports/kirsch-reference/pilot-failures.json").read_text())
    assert not pilot["cases"][1]["checks"]["free_body_force"]
    assert all(all(row["checks"].values()) for row in results["cases"])
    assert results["cases"][1]["free_body_gate_by_panels"]["256"]["force"] is False
    assert results["cases"][1]["free_body_gate_by_panels"]["1024"]["force"] is True
