# Scoped Claude AI technical review: SDLV302 first flexural frequency (analytical Timoshenko reference)

**Repository:** `500ft/evidence-sufficiency-benchmark`, branch `feat/sdlv302-modal-reference`, worktree `/Users/redhose/Projects/evidence-sufficiency-sdlv302`.
**Reviewed technical commit:** `93afbc8e42b32167f2f9729079bd1215b6421ce3`. I verified the full SHA with `git rev-parse HEAD`. `git status --porcelain=v1 --untracked-files=all` printed 0 lines before the review and 0 lines after it.
**Scope:** an owner-authorized (AUD-7) reference-admission technical review of one candidate claim. This is not a scored pilot, a human review, external peer review, FE validation or physical validation. I did not edit the repository. I did not use reserved cases, a 3D FE host, labels, costs, a reviewer pilot or messages to anyone. All my files are under `/tmp/sdlv302-claude-review/`.

## 1. Provenance and exposure

- **Model:** Claude Opus 5.5 (`claude-opus-5-5`) in Claude Code `2.1.304`, running as an interactive agent session with bypass permissions. The model build is unknown.
- **Session ID:** `d9bd23ac-3272-41d0-a20c-85b2ab0f9800`. This comes from the transcript file `~/.claude/projects/-Users-redhose-Projects-evidence-sufficiency-sdlv302/d9bd23ac-….jsonl`. That file contains strings unique to this session (for example the checker key `f4_cowper`) and records `"model":"claude-opus-5-5"`.
- **Exposure: non-blind.** Before deriving anything, I read the following:
  - `ROADMAP.md`, `spec.json`, `reference.py`, `run.py`, `results.json`, `matrix.md` and `tests/test_sdlv302_modal.py`;
  - the AUD-7 section of `docs/OPEN_QUESTIONS.md`;
  - the prior Kirsch Claude review (`REPORT.md` lines 1–60 and `README.md`), used as a format precedent;
  - grep excerpts of the bending family (`studies/reference_qualification/{spec.json,README.md}`) and of `reports/reference-admission/README.md`;
  - the branch's commit diffs.

  I therefore knew the repository's value, 115.70929292854 Hz, and its 2×2 energy-matrix construction before writing my own checker. I have no memory of any earlier SDLV302 review.
- **Independent derivation versus independent authorship.** The derivation in §3 and the checker in §4 are mine. The checker imports no repository module, and it types the physical inputs from the official problem page rather than reading `spec.json`. It reads `results.json` only as JSON, for comparison.
  - Route D (Euler–Lagrange determinant) is the same physics as the repository's energy route. Its float arithmetic differs (60-digit `decimal` against float64), but it is not methodologically distinct.
  - Route F (cubic-Lagrange Galerkin FE, with no modal ansatz) is a genuinely different method.

  Because I was exposed to the implementation first, this is **a separately derived calculation by an exposed AI reviewer. It is not independent authorship, not blind, and not human review.**

## 2. Sources inspected (actual pages, retrieved 2026-10-20)

Raw downloads stay local in `/tmp/sdlv302-claude-review/downloads/` and are not redistributed. All hashes are SHA-256.

| Item | URL | SHA-256 | Note |
|---|---|---|---|
| Problem page | code-aster.org/doc/v17/manuals/man_v/v2/v2.04.302/Probl_me_de_r_f_rence.html | `da87fe28…b595fa` | **Matches** `spec.retrieved_problem_html_sha256` byte-for-byte |
| Solution page | …/Solution_de_r_f_rence.html | `a609810a…b1a475` | **Matches** `spec.retrieved_answer_html_sha256` byte-for-byte |
| Modélisation A | …/Mod_lisation_A.html | `90b400b1…62ef74f` | 3D HEXA20, tested against "ANALYTIQUE" with 1.0 % tolerance |
| Modélisation B | …/Mod_lisation_B.html | `7ac5d5ac…b67d` | Craig–Bampton; same reference table |
| Synthèse | …/Synth_se_des_r_sultats.html | `8c456b78…5a19` | "maximum error less than 0.5 %" (3D against analytic) |
| Index | …/index.html | `e48cb719…d80d` | Abstract; reference is a Timoshenko beam with shear and rotary inertia |
| Geometry figures 1.1-1, 1.1-2 | …/_images/…523…083.png, …182…1E2.png | `a60a3139…a8fd`, `c4e9d72c…cad` | Viewed. **h is along Y and b along Z**, so XY bending uses b·h³/12 |
| docaster LICENSE.txt (main and v17) | gitlab.com/codeaster/doc/docaster/-/raw/{main,v17}/LICENSE.txt | `11053552…06a4` (identical) | GNU FDL 1.3 |
| docaster SDLV302 RST (main and v17) | …/source/manuals/man_v/v2/v2.04.302/{Probl_me…,Solution…}.rst | `6a469e74…af92`, `18403300…edfc0` (main = v17) | Same printed values as the HTML |
| docaster `source/conf.py` (main, v17) | raw | (inspected only) | `license = GNU FDL` link; rendered footer shows only "© Copyright 1989-2026, EDF R&D" |
| src LICENSE | gitlab.com/codeaster/src/-/raw/main/LICENSE | `8ceb4b9e…0206` | GNU GPL v3 |
| src `astest/sdlv302a.comm` | gitlab.com/codeaster/src/-/raw/main/astest/sdlv302a.comm | `6ecbadeb…3677` | GPL v3-or-later header. Inspected for terms, reference tags and 3D `VALE_CALC`; not reproduced |
| Repository heads (GitLab API, at review) | docaster `main` / `v17`; src `main` | `9df3460d…6edc` / `9c8c179f57ef7ca1d2891cac275ee4823a57967c` (tag 17.4.0) / `56f6e2be…75e6` | docaster `main` and src `main` **match** the spec's "head at audit" |

Full hashes are in `input-hashes.txt`. I did **not** inspect Modélisation C or D, `sdlv302b.comm` or `sdlv302a.export` beyond downloading them. The Samtech report (Robert, report no. 121, 1996) was not available and was not inspected.

**What the source says, paraphrased with numbers only:**
- Inputs: L = 2 m, h = 0.2 m, b = 0.1 m, k′ = 5/6, E = 2.1e11 Pa, ν = 0.3, ρ = 7800 kg/m³, G = E/(2(1+ν)).
- Printed displays: A = 0.02 "m"; I = b·h³/12 = 1.66e-5 "m"; G printed as 8.076e10 Pa.
- Reference method: an analytic Timoshenko beam with dimensionless j = I/(AL²), g = EI/(k′AGL²) and Ω = ρAL⁴ω²/(EI). The lower root is printed as Ω = [(g+j)λ² + 1 − √((g−j)²λ⁴ + 2(g+j)λ² + 1)]/(2gj), with λ = nπ. Extension modes are f = (2n−1)√(E/ρ)/(4L).
- Table: 115.7 (flexion), 442.2 (flexion), 648.6 (extension), 931.6 (flexion), 1534.0 (flexion) Hz.
- Uncertainty is stated as "analytical solution".
- The 3D boundary conditions allow only XY flexion and X extension, with DZ = 0 on Z = b/2, supports at the mid-height line and plane-section constraints at both ends.

## 3. Independent derivation

The model is a uniform Timoshenko beam bending in XY, with x along the axis, transverse deflection w(x,t) and section rotation φ(x,t). With S = k′GA, the energies are:

- U = ½∫₀ᴸ [EI φ′² + S (w′ − φ)²] dx
- T = ½∫₀ᴸ [ρA ẇ² + ρI φ̇²] dx

Hamilton's principle gives two field equations:
- δw: ρA ẅ − S(w″ − φ′) = 0
- δφ: ρI φ̈ − EI φ″ − S(w′ − φ) = 0

It also gives the end terms [S(w′ − φ)δw]₀ᴸ = 0 and [EI φ′ δφ]₀ᴸ = 0. Simple supports prescribe w = 0 and leave φ free, so the natural condition is EIφ′ = 0 (zero moment) at x = 0 and x = L.

The functions w = W sin kx·e^{iωt} and φ = P cos kx·e^{iωt} with k = nπ/L satisfy all four boundary conditions exactly. Substituting them gives:

- (S k² − ρAω²) W − S k P = 0
- −S k W + (EI k² + S − ρIω²) P = 0

Setting the determinant to zero gives (ρA)(ρI) ω⁴ − [S ρI k² + ρA EI k² + ρA S] ω² + S EI k⁴ = 0. Dividing by S·EI/L⁴ and substituting λ = kL and Ω = ρAL⁴ω²/(EI) gives:

**g j Ω² − [1 + (g+j) λ²] Ω + λ⁴ = 0.**

Its smaller root is exactly the source's printed expression. The discriminant reduces to (g−j)²λ⁴ + 2(g+j)λ² + 1, as printed. The larger root is the second-spectrum (shear) branch.

**Mode order.**
- The XY-flexural lower branch increases with n.
- The n = 1 upper branch lies at 8233 Hz.
- The fixed-free axial modes, from DX = 0 at X = 0 only, lie at 648.59 Hz and 1945.8 Hz.

So the first XY-flexural mode is the global first mode of the source's constrained model. Bending about the weak axis (XZ, I_y = h·b³/12) would give 58.57 Hz, but the source suppresses it with DZ = 0 on Z = b/2. The claim is therefore "first **XY-plane** flexural frequency" (see F10).

**Units.** The cyclic frequency is f = ω/(2π) in Hz, with ω in rad/s. For n = 1, ω = 727.0229 rad/s, so the Hz/rad·s⁻¹ mix-up value would be 727.0, nowhere near the display.

## 4. Independent computation (checker output)

The checker is `checker/independent_check.py`, using the stdlib and numpy 2.5.3. Its output is `independent_results.json`, and a rerun reproduces it byte-for-byte.

| Quantity | Value | Gate/comparison |
|---|---|---|
| f₁, route D (60-digit) | **115.709292928542690939…** Hz | — |
| Strong-form residuals of both field equations at f₁ | 0 and 0 (n = 1); ≤ 1.4e-60 (n ≤ 4) | exact to working precision |
| Route S (source formula as printed, naive "minus" root, float64) | 115.70929292855432 Hz; \|Δ\| = 1.16e-11 Hz | cancellation loss ≈ 1e-13 relative; harmless |
| Route F (ansatz-free cubic FE, w = 0 at ends only), N = 2/4/8/16/32/64 | error in f₁: 1.9e-1, 4.6e-3, 8.2e-5, 1.3e-6, **2.4e-8**, 7.0e-9 Hz | observed order 5.81, 5.95, 5.82 (theory 6); N = 64 is the float64 floor |
| FE first-mode shape | w projects onto sin(πx/L); modes 1–5 tag n = 1…5 | mode identity confirmed without ansatz |
| FE matrix residual ‖Kv − λMv‖/(‖K‖‖v‖), mode 1 | 5.4e-16 (N = 32) | ≤ 1e-11 |
| 2×2 float64: \|det(K−ω²M)\|/max(k₁₁k₂₂, k₁₂²) | 4.6e-17 (repository: 1.1e-16) | ≤ 1e-11. det/k₁₁k₂₂ = 0.025, so the repository's normalization is adequate |
| 2×2 pencil residual ‖(K−ω²M)v‖/(‖K‖‖v‖) | 2.8e-17 | — |
| Display: f₁ ∈ [115.65, 115.75) | **yes**; margins +0.0593 / −0.0407 Hz | holds under round-half-up, round-half-even, nearest-tenth or 4 significant figures |
| Euler–Bernoulli n = 1 / Rayleigh (rotary only) n = 1 | 117.6418 / 117.1610 Hz | EB > Rayleigh > Timoshenko as expected; shear ≈ 1.45 Hz, rotary ≈ 0.48 Hz |
| Derived global order (first five) | flex 1, flex 2, extension 1, flex 3, flex 4 | **matches the source table order** |
| Scaling (registered in spec, not executed by the repository) | ρ×4 → f×½; (E,G)×4 → f×2; geometry×4 → f×¼ | relative error ≤ 1e-59 |
| Agreement with repository `results.json` | n = 1…4: ≤ 5.1e-13 Hz; axial 0; EB 0; printed-I diagnostic 1.4e-14 Hz | agrees |

**Printed inertia.**
- b·h³/12 = 6.6667e-5 m⁴, which is 4.016 times the printed 1.66e-5.
- The printed value **equals h·b³/12 = 1.66667e-5 truncated to three significant figures.** That is the weak-axis inertia I_y with b and h swapped. Correct rounding would give 1.67e-5.
- The printed G = 8.076e10 is also truncated (exact 8.07692e10).
- Using the printed numeric I as m⁴ with the strong-axis A gives f₁ = **58.4574 Hz** (Timoshenko) or 58.7031 Hz (EB). The exact weak-axis I_y gives 58.5737 Hz.
- The source's printed 115.7 is reproduced only with b·h³/12. Its stated formula, its dimensions and its printed frequency all agree, and only the displayed number disagrees.
- The printed G changes f₁ by −0.00016 Hz, which is immaterial.

**Higher printed modes.**

| Source mode | Printed | Derived (Hz) | Nearest-tenth interval | 4 significant figures |
|---|---|---|---|---|
| 1 flexion | 115.7 | 115.70929 | in | in |
| 2 flexion | 442.2 | 442.17156 | in | in |
| 3 extension | 648.6 | 648.59315 | in | in |
| 4 flexion | 931.6 | 931.57358 | in | in |
| 5 flexion | 1534.0 | 1533.64793 | **out** [1533.95, 1534.05) | **in** [1533.5, 1534.5) |

- A shear factor of 0.834623, instead of 5/6 = 0.833333, would bring flex n = 4 to 1533.95 while keeping f₁ = 115.7115. I found no evidence that the source used that value.
- Cowper's ν-dependent factor (0.849673) gives f₄ = 1537.42 Hz and does not explain 1534.0.
- The printed G gives f₄ = 1533.63 Hz and does not explain it either.

**Model-form context (not tolerances).**
- The display half-width is 0.05 Hz, which is 0.0432 % of f₁.
- Cowper's k′ instead of 5/6 shifts f₁ by +0.0274 Hz (0.024 %).
- Euler–Bernoulli instead of Timoshenko shifts f₁ by +1.93 Hz (1.67 %).
- The source's 3D HEXA20 `VALE_CALC` values in `sdlv302a.comm` differ from the 1D values by −0.0435 %, −0.153 %, −0.0115 %, −0.292 % and −0.437 % for modes 1–5. Its mode 1, 115.659 Hz, happens to lie **0.009 Hz inside** the display interval.
- The source's own 3D test tolerance is 1 % (`PRECISION=1.0e-2`).

## 5. Findings and dispositions

There is **no claim-breaking issue.** Severity is judged against the first-mode claim only.

| # | Finding | Severity | Recommended disposition |
|---|---|---|---|
| F1 | **First-mode value independently reproduced.** Route D (exact), route S (as printed) and ansatz-free route F agree with the repository's 115.709292928543 Hz to ≤ 2.4e-8 Hz, at FE order ≈ 6. The value lies inside the registered display interval with 0.04 Hz margin under every rounding convention considered. Mode order, units (Hz cyclic) and matrix residual are confirmed. | — (confirms claim) | Accept. |
| F2 | **Origin of the printed inertia.** The printed 1.66e-5 is the weak-axis h·b³/12, truncated (an axis swap), not an arbitrary arithmetic error. The bare "m" unit is shared with A = 0.02 "m", so the "dimensional" part is a systematic omission of the unit exponent. The substantive defect is the numeric value. The repository's exclusion, and its 58.457 Hz diagnostic, are correct (my value is 58.4574 Hz). | Low (documentation) | Add the axis-swap observation to `spec.json`/`matrix.md`, and note that A is printed with the same unit omission. No change to computation or gate. Optionally retain it as a natural "wrong-axis I" fault witness for M1.3 (58.46–58.57 Hz). |
| F3 | **"Fourth printed flexural discrepancy" depends on the display convention.** 1534.0 is outside nearest-tenth rounding but inside 4-significant-figure rounding, and all five printed values are consistent with 4 significant figures. The source states no convention. The first-mode interval [115.65, 115.75) is identical under both, so the first-mode gate is unaffected. The issue affects only the excluded n = 4 diagnostic. | Low–Medium (interpretation) | Reword `matrix.md` and the spec so that 1534.0 is called "inconsistent with nearest-tenth display; consistent with 4-significant-figure display; convention unstated", rather than an established source discrepancy. Keep `fourth_display_interval_excludes_derived` as a nearest-tenth diagnostic. No interval widening is needed or recommended. |
| F4 | **Registered controls not fully executed.** The spec registers "zero-density and zero-stiffness limits checked by scaling", but `run.py` and the tests do not implement it. The axial frequency is computed but not gated: there is no order check against flexural modes and no comparison with the printed 648.6. `matrix.md` lists the axial mode as a control. | Low (process) | Either implement the scaling and global-order checks, or record them as not executed. My checker executes both and both pass: scaling exact to 1e-59, derived order equals the source table, 648.593 ∈ [648.55, 648.65). |
| F5 | **Independence of the repository's two routes.** The "source expression" and "energy matrix" routes solve the same quadratic from the same sin/cos ansatz. Their 1e-13 Hz agreement checks transcription, not modelling. | Low (wording) | State this in `matrix.md`. My ansatz-free FE (route F) closes the gap; any mistake shared in k′, A, I or G would still be common to all routes, and the source display is the only external check on those. |
| F6 | **Licence provenance precision.** The spec links docaster `main` (head matches), but the published manual is v17, which has its own branch `v17` at `9c8c179f…` (tag 17.4.0). LICENSE.txt and both SDLV302 RST files are byte-identical on `main` and `v17`. The HTML page itself shows only "© Copyright 1989-2026, EDF R&D". The FDL designation comes from the repository's LICENSE.txt and the Sphinx `conf.py` `license` field, which is not rendered in the footer. The code is GPL v3 (src LICENSE), and `sdlv302a.comm` is GPL v3-or-later. | Low (provenance) | Record the v17 branch head and the fact that the licence is inferred from the repository rather than shown on the page. The repository copies no text, figures or deck; it uses numbers, the formula and its own paraphrase, which is consistent with both licences. This is not legal advice. |
| F7 | **Inconsistent reference-type label and unavailable primary report.** The manual tags the values "ANALYTIQUE", while the GPL deck tests the same values with `REFERENCE="NON_DEFINI"`. Its header credits independent validation by Samtech (H. Drion). The cited Samtech report no. 121 was not obtained, so who computed 115.7 rests on the manual alone. | Low (provenance) | Record it. This does not break the claim, because the formula is re-derivable from first principles (§3) and the printed first value is reproduced. No rights in the Samtech report are needed or inferred. |
| F8 | **3D against 1D.** The reference is unambiguously the 1D analytic Timoshenko value (manual §2.1, Synthèse). The 3D HEXA20 is an approximation compared at 1 %. Its first mode differs from 1D by −0.0435 %, about the display half-width, and happens to fall 0.009 Hz inside the interval. | Info | The spec already excludes 3D. Add one sentence saying the display interval is not an acceptance band for 3D or other model-form artifacts, since agreement or disagreement of a 3D solve within it is coincidental. |
| F9 | **Numerical comparison against physical tolerance.** The display interval (0.043 %) is a reporting-precision gate and is tighter than the plausible model-form spread (shear-factor convention 0.024 %, 3D 0.04–0.44 %, EB 1.67 %). It cannot discriminate shear-factor conventions. The repository correctly declares no physical decision tolerance. | Info (M1.3 input) | No change for admission. For M1.3, the k′ convention is a compatible explanation that is undetectable at display precision. Any decision tolerance must be declared separately. |
| F10 | **The observable should name the plane.** `claim.observable` says "first flexural cyclic eigenfrequency". The XY-plane restriction appears only in `model`. With both bending planes free, the first flexural mode would be weak-axis bending at 58.57 Hz. | Low (wording) | Change the wording to "first XY-plane (strong-axis, about z) flexural cyclic eigenfrequency". |
| F11 | **Spec hygiene.** `status` still reads "…pending_execution…". The interval is stored as a closed JSON list `[115.65, 115.75]`, with half-open semantics given in a separate string. | Low | Update the status, or note that it is historical. The code uses `lo <= f < hi` consistently. Optionally rename the field `…_half_open`. |
| F12 | **Distinct from the static bending family.** The existing case is an Euler–Bernoulli static cantilever under uniform load (clamped-free, repository-authored parameters, stress and tip deflection). SDLV302 differs in its equations (inertia, shear, rotary inertia), boundary conditions (pinned-pinned), observable (eigenfrequency) and source (published). It is not a parameter or loading variant. The only common ingredient is I = b·h³/12, and F2 shows that a fault in it is detectable here. | Info | It counts as a distinct base problem. Whether it is labelled under "bending" or as a new "beam dynamics" category is the owner's decision. |
| F13 | **Prospective registration and amendment.** Registration (125eea7, 17:52:52) and pinning (c227216, 17:53:14) precede execution (63d2d8d, 17:53:53) in commit order. The post-execution amendment (8c63a73…93afbc8) changed only the inertia description and `source_displays`. I verified with `git diff 63d2d8d HEAD` that the gate interval, A/I/G and `reference.py` are unchanged. The original spec wrongly called the printed I a "rounded display", and the correction is preserved in history. | Info | Accept. Note that the commit timestamps are author-controlled and only about 1 minute apart, so prospectivity rests on commit order alone. |

## 6. Recommendation

**Admit**, at the stated scope, one published-reference base problem: the first XY-plane flexural cyclic eigenfrequency, 115.7 Hz printed and 115.70929292854 Hz exact, of an ideal, undamped, uniform, simply supported 1D Timoshenko beam with k′ = 5/6 and the SDLV302 inputs. Before admission, make the documentation corrections F2, F3, F4 and F10 (F4 either way: execute or record). F5, F6, F7, F8 and F11 are optional clarifications.

- No tolerance, gate or computation needs to change.
- The printed first-mode target is reproduced from the source's own dimensions and formula, so this differs from VM92, whose target is disputed. Whether the source's input-display error (F2) and the unstated display convention (F3) still allow counting it as a *firm* published reference is the owner's call. In my judgement they do, because neither touches the first-mode target.
- The admission does not cover higher modes, the 3D model, any physical tolerance, labels, costs or a pilot.

## 7. Exact commands

Everything was run from `/Users/redhose/Projects/evidence-sufficiency-sdlv302` unless a `cd` is shown. Network access consisted only of GET requests to code-aster.org and gitlab.com.

```sh
git rev-parse HEAD && git status --porcelain=v1 --untracked-files=all | wc -l
git log --oneline main..HEAD
git show --stat --format= <c>   # for c in 125eea7 c227216 63d2d8d 8c63a73 424d729 8251c2e 93afbc8
git show 125eea7:studies/sdlv302_modal/spec.json
git diff 125eea7 63d2d8d -- studies/sdlv302_modal/spec.json
git diff 63d2d8d HEAD -- studies/sdlv302_modal/spec.json studies/sdlv302_modal/reference.py studies/sdlv302_modal/run.py
# repository reproduction without writing to the worktree
PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json,hashlib; from studies.sdlv302_modal.run import build; out=json.dumps(build(),indent=2,sort_keys=True)+"\n"; print(out==open("reports/sdlv302-modal/results.json").read(), hashlib.sha256(out.encode()).hexdigest())'
#   -> True eee527692a188b62702580d9784313037aaa905e77f6de3eccf657dac834b89a
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/test_sdlv302_modal.py   # -> 2 passed
# sources
cd /tmp/sdlv302-claude-review/downloads && for p in Probl_me_de_r_f_rence Solution_de_r_f_rence Mod_lisation_A Synth_se_des_r_sultats Mod_lisation_B index; do curl -sS -L -o "$p.html" "https://code-aster.org/doc/v17/manuals/man_v/v2/v2.04.302/$p.html"; done
curl -sS -o img/<id>.png "https://code-aster.org/doc/v17/manuals/man_v/v2/v2.04.302/_images/<id>.png"   # the two figure ids in §2
curl -sS -o gitlab/docaster_LICENSE.txt https://gitlab.com/codeaster/doc/docaster/-/raw/main/LICENSE.txt   # and /raw/v17/
curl -sS -o gitlab/src_LICENSE https://gitlab.com/codeaster/src/-/raw/main/LICENSE
curl -sS https://gitlab.com/api/v4/projects/codeaster%2Fdoc%2Fdocaster/repository/branches/main   # also /branches/v17, /branches, /tags, codeaster%2Fsrc
curl -sS -o gitlab/docaster_<f>.rst https://gitlab.com/codeaster/doc/docaster/-/raw/{main,v17}/source/manuals/man_v/v2/v2.04.302/<f>.rst
curl -sS https://gitlab.com/codeaster/doc/docaster/-/raw/{main,v17}/source/conf.py | grep -n 'license\|copyright'
curl -sS -o gitlab/src_sdlv302a.comm https://gitlab.com/codeaster/src/-/raw/main/astest/sdlv302a.comm
cd /tmp/sdlv302-claude-review && python3 -I tools/html_text.py downloads/<page>.html   # text extraction, stdlib only
# independent check
cd /tmp/sdlv302-claude-review && python3 -I checker/independent_check.py /Users/redhose/Projects/evidence-sufficiency-sdlv302/reports/sdlv302-modal/results.json > independent_results.json
python3 -I checker/independent_check.py /Users/redhose/Projects/evidence-sufficiency-sdlv302/reports/sdlv302-modal/results.json | cmp - independent_results.json   # byte-identical
shasum -a 256 REPORT.md > REPORT.sha256    # after writing this report
```

The checker contains `assert` gates on residuals, FE order, display, scaling and repository agreement, so it exits non-zero if any of them fail. My first run failed one of these: a 1e-8 Hz FE gate at N = 32. I traced it to the float64 floor and convergence rate (the table in §4), not to a modelling error, and replaced it with an order check in (5.5, 6.5) plus 1e-7 Hz at N = 32. The retained output comes from the corrected checker.

## 8. Output file hashes (SHA-256)

```
659efe53fe466257c82fa82f9cd88822c40bd03dd80a8af5ac5fa8052c57cd89  checker/independent_check.py
1f26bc83557d5d15f9f8fc078071b8d31f9db97d6253c60aeb7557758f63520e  independent_results.json
7134f8cd9b52c7c402ebcfeff6c6c8a1e155aef3e7064029c51e1fc7797ee801  tools/html_text.py
```
A report cannot contain its own hash, so the hash of `REPORT.md` is in `REPORT.sha256`, written after this file was finalized. Input and source hashes are in `input-hashes.txt`.

`prompt.txt` (SHA-256 `f7b1c76b…db343`) and an empty `response.json` were already in this directory when I first wrote to it, at 17:55. I did not write them; they presumably belong to whatever launched this session. A `checker/__pycache__` left by a debugging import was deleted, and it does not affect any hashed output.
