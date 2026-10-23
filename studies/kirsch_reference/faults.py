"""Bounded synthetic fault detectability for the admitted Kirsch nominal specimen.

Reuses the retained development-compute fault budgets, magnitudes and bisection
unchanged. The registered Kirsch route budget is the numerical error. Truth is
the exact rational claim; every changed artifact must pass the registered gates.
"""
import copy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

from studies.development_compute.experiment import MANIFEST, boundary, bounded_decision, fault_study
from studies.kirsch_reference.run import SPEC, case_result

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REGISTRATION = json.loads((HERE / "faults.json").read_text())
OUT = ROOT / REGISTRATION["output"]
FAULTS = MANIFEST["faults"]


def spec_and_nominal():
    spec = json.loads(SPEC.read_text())
    assert spec["claim"]["exact_reference"] == "3*sigma"
    return spec, next(c for c in spec["cases"] if c["id"] == "nominal")


def exact_claim(sigma):
    return 3 * F(sigma)


def route_budget(sigma):
    # spec budgets.stress_route_abs_MPa, as applied by run.case_result.
    return F("1e-9") * max(1, abs(F(sigma)))


def evaluate(spec, nominal, parameter, magnitude):
    changed = copy.deepcopy(nominal)
    value = F(str(nominal[parameter])) * (1 - magnitude)
    changed[parameter] = float(value)
    executed = case_result(changed, spec)
    if not all(executed["checks"].values()):
        raise ValueError(f"Fault specification failed Kirsch gates: {parameter}, {magnitude}")
    sigma_nominal = F(str(nominal["remote_sigma_MPa"]))
    sigma = value if parameter == "remote_sigma_MPa" else sigma_nominal
    scale = abs(exact_claim(sigma_nominal))
    assert scale > 0
    tolerance = scale * F(FAULTS["claim_tolerance_fraction"])
    observation_error = scale * F(FAULTS["bounded_observation_error_fraction"])
    numerical_error = route_budget(sigma)
    assert abs(F(executed["claim_sigma_theta_MPa"]) - exact_claim(sigma)) <= numerical_error
    signal = abs(exact_claim(sigma) - exact_claim(sigma_nominal))
    return {"magnitude": str(magnitude), "parameter_value_exact": str(value),
            "unit": spec["claim"]["unit"], "scale_exact": str(scale),
            "signal_exact": str(signal), "tolerance_exact": str(tolerance),
            "bounded_observation_error_exact": str(observation_error),
            "numerical_budget_exact": str(numerical_error),
            "artifact_correct_for_synthetic_claim": signal <= tolerance,
            "decision": bounded_decision(signal, tolerance, observation_error + numerical_error),
            "exact_zero_signal": signal == 0, "registered_gates_passed": True}


def study(spec, nominal, parameter):
    cache = {}

    def at(magnitude):
        if magnitude not in cache:
            cache[magnitude] = evaluate(spec, nominal, parameter, magnitude)
        return cache[magnitude]

    rows = [at(F(m)) for m in FAULTS["magnitudes"]]
    low, high = map(F, FAULTS["boundary_search"]["bracket"])
    boundaries = {
        name: boundary(lambda m: at(m)["decision"] in decisions, low, high,
                       FAULTS["boundary_search"]["bisections"])
        for name, decisions in (("leaves_guaranteed_pass", {"error_dependent", "guaranteed_detection"}),
                                ("enters_guaranteed_detection", {"guaranteed_detection"}))}
    return {"parameter": parameter, "status": "provisional_numerically_qualified",
            "exact_null_space": all(cache[m]["exact_zero_signal"] for m in cache),
            "rows": rows, "boundaries": boundaries, "evaluations": len(cache)}


def build():
    spec, nominal = spec_and_nominal()
    retained = json.loads((ROOT / "reports/development-compute/results.json").read_text())
    committed = {f["case_id"]: f["boundaries"] for f in retained["faults"]}
    reproduced = {case_id: fault_study(case_id)["boundaries"] == committed[case_id]
                  for case_id in FAULTS["cases"]}
    faults = [study(spec, nominal, p) for p in REGISTRATION["fault_parameters"]]
    nominal_run = case_result(nominal, spec)
    nuisance = {**copy.deepcopy(nominal), "density_kg_per_m3": "12345"}
    nuisance_run = case_result(nuisance, spec)
    controls = {"correct": faults[0]["rows"][0],
                "nuisance": {"registered_gates_passed": all(nuisance_run["checks"].values()),
                             "claim_equal_to_nominal": nuisance_run["claim_sigma_theta_MPa"] == nominal_run["claim_sigma_theta_MPa"]}}
    assert controls["correct"]["decision"] == "guaranteed_pass" and controls["correct"]["exact_zero_signal"]
    assert all(controls["nuisance"].values())
    digest = lambda p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
    return {"status": "executed provisional development detectability for the admitted Kirsch nominal specimen; no label, score or new admission",
            "registration_sha256": digest("studies/kirsch_reference/faults.json"),
            "spec_sha256": digest("studies/kirsch_reference/spec.json"),
            "manifest_sha256": digest("studies/development_compute/manifest.json"),
            "retained_sweep": {"results_sha256": digest("reports/development-compute/results.json"),
                               "boundaries_reproduced": reproduced},
            "faults": faults, "controls": controls,
            "evaluations": sum(f["evaluations"] for f in faults) + 2}


def main():
    OUT.write_text(json.dumps(build(), indent=2) + "\n")


if __name__ == "__main__":
    main()
