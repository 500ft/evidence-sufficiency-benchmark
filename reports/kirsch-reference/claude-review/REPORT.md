# Scoped Claude AI technical review: Kirsch derived development reference

**Reviewed commit:** `190871bed8de6a3e350322b2fd17ac6840dcad28` (branch `feat/kirsch-derived-reference`, worktree `/Users/redhose/Projects/evidence-sufficiency-kirsch`, clean).
**Scope:** owner-authorized reference-admission technical review. This is not a scored pilot, human review, external peer review or physical validation. The repository was not edited. No reserved cases, unrelated studies, CAD/FEA hosts or messages were used.

## Provenance and exposure
- **Model:** Claude Opus 5.5 (`claude-opus-5-5`) in Claude Code, run headless by `launch_review.py` (`claude -p --model opus`, allowed tools Read/Bash/WebFetch, 900 s timeout). The model build is unknown. The session ID is probably `82b83c51-fd15-4b9c-99cf-76cf8fdadf78`, inferred from the newest transcript file and not otherwise confirmed.
- **Exposure: non-blind.** I read the spec, `reference.py`, `run.py`, results, pilot, matrix and tests before doing my own derivation. The earlier admission review (README) also reports Claude Opus 5.5. This session has no memory of that review beyond reading the README.
- **Independent derivation versus independent authorship.** The derivations and script below are mine. They do not import or call any repository routine. They also use a different method (Kolosov–Muskhelishvili complex potentials, exact Fraction arithmetic, closed-form Airy resultants). However, the author had seen the repository formulas. This is therefore a separately derived calculation, **not independent authorship and not an independent human review.**
- **Time limit:** the launcher's 900 s timeout cut the review short. The LE1 external pages (NAFEMS, CoFEA) were **not fetched**, so the LE1 audit below rests on the repository text alone.

## Input hashes (SHA-256)
```
233d6d7d90f90a220b8e09df7cca416d47742fc9f7cb37dd94603bac9439c921 ROADMAP.md
2c29f2cc674d07aefb802dada4bb755722f7abf0fc1c1e2d8f2f169a47b593d7 reports/reference-admission/README.md
fff4f1314c00df8c5ce657e82ecaa6cf3013220fee8d4aafdde079b7e81a49ee reports/artifact-rule-witnesses/matrix.md
d4cb8e3c4d4646fdc3e26fe5b672ecc2bc1b5df6bb74d6bdb46e50679f47a3fc studies/kirsch_reference/spec.json   (amended; original d251d562...a9d6c5 at 3ee2e1b/def6031)
a55d6bad5869ab772b10dd7d6e7097c2c5ad1e9f349dc9fa09d6a59777cfe6da studies/kirsch_reference/reference.py
6df1204bd616c6e9094f5205a60b9deac9650a073b59402a3b8f15bd35ed9188 studies/kirsch_reference/run.py
6f904d78ff94682f921c77a32719f4698ba62e1c3bf1e6b26c4b3e0542dbe36c reports/kirsch-reference/pilot-failures.json
05dde3d19a0c0705290b034edd7b5d93498be57c7d5e93e20b9e36d72cb527b1 reports/kirsch-reference/results.json
6ab25afe7a049828e261f1cd7b712b159dfaf591e877e60eafc5a4798d81ea26 reports/kirsch-reference/matrix.md
c33f2211ca8f4cc087411738511ba408751a0071a463c1c3fcea4709afdd153c reports/kirsch-reference/le1-audit.md
ee8eba926f0d54cfc5984a52cbac2af428e872af5f086c5f6aad8dffc7e2ab7f tests/test_kirsch_reference.py
c580ffbdd328b4ef0741a7a3278d66a467db9121c61edc0a851fbb1771bc9408 review-evidence/kirsch_independent_check.py
69fd99e5020076ac6427e64ca8576ecceab11d9ceffbf2d7585f4a5cb6847438 review-evidence/kirsch_independent_results.json
```
These are also saved in `input-hashes.txt`. Note that the existing `claude-response.json` and `claude-stderr.log` belong to the launcher; I did not write them.

## Independent derivation
**Airy potential.** Remote σyy = S gives Φ∞ = S x²/2 = (S/4) r²(1 + cos2θ).
- Axisymmetric part: A r² + C ln r with A = S/4. σrr(a) = 2A + C/a² = 0, so C = −S a²/2.
- cos2θ part: f(r) = D r² + E + F r⁻² (the r⁴ term is excluded because stress must stay bounded), with D = S/4. For Φ = f cos2θ:
  - σrr coefficient = f′/r − 4f/r² = −2D − 4E/r² − 6F/r⁴
  - σrθ coefficient = 2(f/r)′ = 2(D − E/r² − 3F/r⁴)
  - Setting both to zero at r = a gives E = −2D a² and F = D a⁴.
- Result: **Φ = (S/4)[r² − 2a² ln(r/a) + (r² − 2a² + a⁴/r²) cos2θ]**, which is identical to `reference.py`.
- On r = a this Φ equals S a²/4 (a constant) and ∂Φ/∂r = 0. That is the traction-free condition stated directly.

**Stresses from Φ** (θ measured counterclockwise from +x, load along +y, q = a²/r²):
- σrr = S/2(1−q) − S/2(1−4q+3q²)cos2θ
- σθθ = S/2(1+q) + S/2(1+3q²)cos2θ
- σrθ = +S/2(1+2q−3q²)sin2θ

These match `polar()` and the OpenGeoSys 6.5.7 page term for term; I fetched that page during this review and it states the y-axis loading case. At r = a, σθθ = S(1 + 2cos2θ), giving **3S at θ = 0** and −S at θ = 90°. The y-loaded form is the x-loaded form with θ → θ − π/2. Applying the x-loaded form without that rotation gives −S at (a,0), which is the convention trap; the repository avoids it.

**Third route (complex potentials).**
- φ = Γz − Γ′a²/z and ψ = Γ′z − 2Γa²/z − Γ′a⁴/z³, with Γ = (Sx+Sy)/4 and Γ′ = (Sy−Sx)/2.
- For this problem (Sx = 0, Sy = S): φ = Sz/4 − S a²/(2z) and ψ = Sz/2 − S a²/(2z) − S a⁴/(2z³).
- Displacement: 2G(ux + i uy) = κφ − z·conj(φ′) − conj(ψ), with plane-stress κ = (3−ν)/(1+ν).
- On x = 0 every term is purely imaginary, so **ux = 0 exactly**. On y = 0 every term is real, so **uy = 0 exactly**.
- The potentials are single-valued (no log terms), so the displacement is single-valued.

**BVP and exact restriction.** The quarter-domain restriction satisfies, everywhere in the domain:
- equilibrium;
- compatibility, i.e. ∇²(σxx+σyy) = 0 (valid for plane stress with no body force);
- plane-stress Hooke's law, through the displacement above;
- the BCs: zero traction on the hole, the full field traction on x = B and y = B (including nonuniform shear), and ux = 0 / uy = 0 with zero shear on the symmetry edges.

Rigid motions are excluded: on x = 0, ux = c1 − ωy = 0 for all y ∈ [a,B] forces c1 = ω = 0, and on y = 0, uy = c2 = 0. By Kirchhoff uniqueness for this mixed problem, the specified BVP has exactly this stress field. **The claim σθθ(a,0) = 3S is therefore exact for the finite BVP as specified, for every E > 0 and admissible ν.**

The ν-independence holds here because the symmetric solution satisfies the displacement BCs for every ν. Mixed BVPs are not ν-independent in general. Units: a and B in m, S in MPa, force per unit thickness in MPa·m. E is in MPa but enters only the displacements.

## Commands and actual results
1. `python3 -I review-evidence/kirsch_independent_check.py <repo>/reports/kirsch-reference/results.json <repo>/reports/kirsch-reference/pilot-failures.json > review-evidence/kirsch_independent_results.json` (Python 3.13.7, stdlib only; exit 0). Results for all four cases:
   - **Exact (Fraction) checks:**
     - the claim tuple at (a,0) is exactly (0, 3S, 0): 30, 30, −21, 0 MPa;
     - hole traction is exactly zero at 8 rational points on r = a;
     - symmetry shear is exactly zero at 12 points;
     - divergence and the Laplacian of the trace are exactly 0 at 4 interior rational points.
   - **Complex-potential route versus polar route** on a 41×41 grid that includes the corners: maximum difference 7.1e-15 MPa.
   - **Hoop stress on the hole** at 0/30/45/60/90° (nominal): 30, 20, 10, ~1e-14, −10 MPa.
   - **Displacements:** |ux| on x = 0 and |uy| on y = 0 are 0.0 m. The plane-stress Hooke residual is 5.1e-15, against a strain scale of 5e-5.
     - Mutant: substituting the plane-strain κ gives a residual of 6.6e-6, so the Hooke check does discriminate plane stress from plane strain.
   - **Outer edges:** the maximum shear over the repository's 9-point outer grid is 0.444477 MPa (nominal; repository value 0.4444767012154019) and 0.114546 MPa (scaled). On the top edge, σyy runs from 9.024 to 10.194 MPa (nominal). A uniform-edge model is therefore a different BVP.
   - **Per-segment resultants:** closed-form Airy endpoint values agree with 20-point × 8-panel Gauss–Legendre integration on complex-potential tractions to ≤5.3e-13. Total free-body force and moment residuals are ≤4.8e-13.
   - **Simpson reproduction:** my own Simpson implementation on the complex-potential field reproduces every retained repository residual (64 to 1024 panels) to ≤4.1e-13. It also reproduces every per-level pass/fail gate. Force-error ratio 256→512 = 15.98, i.e. h⁴ convergence.
2. `git archive 190871b | tar -x -C /tmp/kirsch-review-u7fm`, then in that copy run `build() == results.json` → **True**. Then `/Users/redhose/Projects/engineering-audit/.venv/bin/pytest -q -p no:cacheprovider tests/test_kirsch_reference.py` → **3 passed**. The worktree has no `.venv`; I used the main checkout's pytest (v9.1.1).
3. `git archive def6031 | tar -x -C /tmp/kirsch-pilot-q9aM`, then run `case_result()` on the original spec → it **reproduces `pilot-failures.json`** (panel values and checks), which is byte-unchanged since def6031.
4. Spec hashes by commit: 3ee2e1b and def6031 = `d251d562…`, which matches `pilot-failures.json:spec_sha256`. f919cfc and 190871b = `d4cb8e3c…`, which matches `results.json`.

**Budgets at the finest registered level (1024 panels).** The unchanged budgets are met with wide margin:

| Case | Force residual / budget (MPa·m) | Moment residual / budget (MPa·m²) |
| :--- | :--- | :--- |
| Nominal | 2.5e-9 / 5e-6 | 2.3e-9 / 2.5e-5 |
| Scaled | 1.3e-7 / 2e-5 | 2.4e-7 / 4e-4 |
| Reversed | 1.7e-9 / 3.5e-6 | 1.6e-9 / 1.75e-5 |
| Zero load | 0 | 0 |

## Findings
| ID | Severity | Finding | Reproducer | Disposition |
| :--- | :--- | :--- | :--- | :--- |
| F1 | Medium (registration disclosure) | The amendment changed the free-body **decision rule** as well as the level list. The pilot runner (def6031) gated on the maximum over *all* levels, and original hypothesis 3 said "close … at the registered quadrature levels". The amended runner gates on the finest level only. Under the original all-levels rule, loaded cases still fail even with 512/1024 added. Hypothesis 3 remains in the amended spec verbatim and is false for 64/128 (and 256 for the scaled case). `matrix.md` says only "added finer levels while keeping every previous level and the same budgets". Separately, commit timestamps are author-set (pilot 22:08:53, amendment 22:08:59), and the 512/1024 outcome was predictable from the retained h⁴ ratio, so "prospective" carries little evidential weight here. | `git diff def6031 190871b -- studies/kirsch_reference/run.py`; script field `original_all_levels_rule_would_pass_with_512_1024 = false` | **Correction required (documentation only).** State the all-levels→finest-level rule change and mark hypothesis 3 as failed under the original rule. The claim value is unaffected: the exact integral is zero, as shown by the closed-form resultants. |
| F2 | Medium (evidence gap, resolved here) | The repository never computes displacements, and E and ν are unused. The symmetry displacement BCs and the plane-stress law behind the exact-restriction claim are therefore asserted, not executed. | Script fields `max_abs_ux_on_x0_m`, `max_abs_uy_on_y0_m`, `hooke_*` | **Resolved by independent derivation** (exact symmetry displacement; Hooke residual 5e-15). Recommend that the admission record cite this review, or that a displacement check be added later. Not blocking. |
| F3 | Low | `run.py` contains gates and sample settings that are not in the spec: far-field budget 1e-3·scale at 100a, 9-point hole/symmetry/outer grids, finite-difference step a·1e-4, interior angles 30/45/60°. `matrix.md` nevertheless says "All tolerance expressions and sample settings live in the specification." | `run.py` lines 64-89, 99, 109 | **Correction required (documentation):** either register these settings or qualify the statement. No value is affected. |
| F4 | Low | Some gates hold identically on the Airy route. The divergence of Airy stresses, and free-body closure of Airy tractions over the simply connected contour, vanish for *any* smooth Φ. They therefore test jet and boundary bookkeeping, not Kirsch correctness. The discriminating gates are route agreement, hole traction, the compatibility (biharmonic) gate, the claim gate and far-field. | Analytic: t = (dΦy/ds, −dΦx/ds) | Scope note. My exact-arithmetic divergence check on the *polar* route is the non-tautological equilibrium test, and it passes. |
| F5 | Low | The zero-load case cannot detect any error proportional to S, such as a factor-of-2 error or a sign flip. With budgets of max(1,\|S\|)·ε against exact zeros, it is only a no-offset control. | Script `mutants`: both detectable flags are false | Scope note. It must not be counted as evidence of correctness. |
| F6 | Low | The command that generated `pilot-failures.json` is not retained. `def6031` `build()` asserts that all checks pass, so it cannot have written a failing record. | Step 3 above reproduces the file via `case_result()` | Record the generating command. The numbers are genuine (reproduced). |
| F7 | Info | Wording and implementation mismatches with negligible effect: (a) the 1e-14 relative r² guard applies to *all* inputs of `polar` and `airy_cartesian`, not only to points on the hole circle as the spec says (effect ≤1e-14 relative); (b) hypothesis 3 says "four" boundary tractions but there are five segments; (c) "intersecting" symmetry constraints: the lines intersect, the edges do not; (d) "stress independent of E, ν" is true here only because of the symmetry solution (see derivation). | Inspection | Optional wording fixes. |

No code defect alters any claim value or numeric result. The tolerances are numerical-reproduction gates, 3 to 8 orders above observed roundoff. They are loose but not claim-enlarging, because the claim is exact and checked in rational arithmetic. Domain and sample scope:
- 3 loaded parameter variants of one problem (B/a = 5 and 10);
- route samples at r/a ∈ {1, 1.2, 2, 4} and 0–90°;
- the claim is a single point.

These are variants of **one** base problem, not several. Plane stress is the stated ideal model; this review does not cover thin-plate 3D effects.

**LE1 exclusion.** I checked only the repository text, and did not fetch external pages within the time limit. The exclusion does not count LE1, copies no deck, figure or target, and does not treat the CoFEA CC BY-NC-SA licence as a grant of rights in NAFEMS material. It is conservative, and no action is needed for this review.

## Recommendation
**Admit within scope as one derived (not published-reference) development base problem.** The admitted claim is the circumferential stress σθθ = 3S MPa at (a,0) for the specified ideal, linear-elastic, plane-stress quarter-domain exact-restriction BVP (Kirsch field traction on x = B and y = B including shear, traction-free hole, symmetry edges). The admission covers only the registered inputs.

The physics, sign and angle convention, BCs, uniqueness and finest-level budgets are independently verified. **Before the admission record is written, the F1 and F3 documentation corrections are required.** They change no numeric value, budget or claim. F2 is resolved by this review. F4–F7 are scope notes.

If admitted, the coverage count would become 5/10 with published-reference problems still at 1/2. This is a non-blind Claude computation, not independent human review.
