# Development compute results

**Executed synthetic development study. Independent human admission remains pending.**

Source: [results.json](results.json). [Frozen domain and reproduction](../../studies/development_compute/README.md).

## Reference sweep

| Model | Parameter variants | Numerically qualified | Failed inherited gate | Claim comparisons | Failed comparisons |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Cantilever | 72 | 72 | 0 | 864 | 0 |
| Pressure-only cylinder | 320 | 224 | 96 | 6720 | 372 |
| Layered wall | 486 | 486 | 0 | 5832 | 0 |

Counts are parameter variants and comparisons within existing development families.
Bending and conduction require exact rational agreement on every inherited partition.
Cylinder qualification retains every inherited radial-step budget. Extra finer steps
diagnose errors without changing a failed specification to a pass.

| Cylinder radial steps | Largest absolute error / declared budget [1] |
| ---: | ---: |
| 32 | 122.784 |
| 64 | 7.76653 |
| 128 | 0.483114 |
| 256 | 0.0300368 |
| 512 | 0.00187103 |

A complete minimal failure is retained in the numeric source, with all claim errors and diagnostics.
The first failure has a = 1 in, b = 4 in, E = 30000000 psi, nu = -1/2, internal pressure 300 psi and external pressure 0 psi.
The pressure-only, zero-end-resultant convention is unchanged. Radial tractions and
trapezoid integrated-equilibrium residuals are in the raw records; that quadrature
residual has its own error and is not the RK4 claim-error budget.

## Conditional synthetic detectability

Each nominal and changed specification passed its own independent numerical gate.
Only the frozen public nominal specimens enter these fault studies; failed sweep specimens do not.
The agreement tolerance is 1% of the declared scale, with bounded observation error of 0.2%.
Cylinder observations also include the verified numerical budget. Temperature uses
the outer-surface rise above ambient, avoiding a percentage of an affine absolute temperature.

| Model / observable | Exit guaranteed-pass boundary [reduction %] | Enter guaranteed-detection boundary [reduction %] |
| :--- | ---: | ---: |
| Cantilever / root stress | No crossing in domain | No crossing in domain |
| Cantilever / tip deflection | 0.79365075 to 0.79365373 | 1.18576884 to 1.18577182 |
| Pressure-only cylinder / inner hoop stress | No crossing in domain | No crossing in domain |
| Pressure-only cylinder / inner displacement | 0.79360008 to 0.79360306 | 1.18581951 to 1.18582249 |
| Layered wall / heat rate | 1.08881891 to 1.08882189 | 1.63085461 to 1.63085759 |
| Layered wall / outer surface temperature | 1.08881891 to 1.08882189 | 1.63085461 to 1.63085759 |

Reduction means E for bending/cylinder and layer-2 conductivity for the wall.
Each bracket runs from the last false predicate to the first true predicate in the
frozen bisection. Pass is inclusive at the tolerance. Between these two boundaries,
the decision depends on the bounded observation error; these are not probabilities.

Bending root stress and cylinder hoop stress have an exact modulus null space under
the specified loads. A nonzero deflection signal below tolerance has a different cause.
Correct, benign-refinement and nuisance controls passed their numerical checks.
All grid magnitudes, exact signals, tolerances, correctness decisions and control outcomes
are retained in JSON; no mutation name or selection policy supplies truth.

## Retained FEA eligibility

| Record | Mesh count | Solver completed | Reference agrees | Retained stability status | Richardson / GCI |
| :--- | ---: | :---: | :---: | :--- | :--- |
| mounting_plate_fea_result.json | 4 | True | True | not_converged | Unavailable |
| mounting_plate_holeref48_fea_result.json | 1 | True | True | insufficient_evidence | Unavailable |
| mounting_plate_holeref_fea_result.json | 1 | True | True | insufficient_evidence | Unavailable |

**mounting_plate_fea_result.json**

- max_von_mises_mpa_at_hole [MPa]: Successive observable changes reverse sign; a single monotone leading-error power is unsupported.
- max_displacement_mm [mm]: Finest-three changes admit no positive leading-error order using the recorded target sizes.

**mounting_plate_holeref48_fea_result.json**

- max_von_mises_mpa_at_hole [MPa]: Only one mesh in this local-refinement record; fewer than three grids.
- max_displacement_mm [mm]: Only one mesh in this local-refinement record; fewer than three grids.

**mounting_plate_holeref_fea_result.json**

- max_von_mises_mpa_at_hole [MPa]: Only one mesh in this local-refinement record; fewer than three grids.
- max_displacement_mm [mm]: Only one mesh in this local-refinement record; fewer than three grids.

The finest-three displacement-change ratio is 0.259934; a positive leading-error order with the recorded target sizes requires more than 1.40942.
Local records change hole divisions 24 to 48 while global size coarsens 3 to 5 mm; neither belongs to the global-only refinement sequence. Counts cannot establish a common refinement ratio.
The global unstructured meshes do not demonstrate systematic local similarity. No element-count-derived h or oscillation fit was used.

## Execution and gates

The full run completed in 2.737 s; recorded peak RSS was 42.73 MiB and raw artifacts occupied 5759266 bytes at completion.
One worker and one numerical thread were used. Sampling was deterministic; random seed and Monte Carlo are inapplicable.
Raw file hashes, source hashes and checkpoint/resource metadata are in the numeric source.

Coverage remains 4 development families and 0 admitted problems.

- Holed plate: Retained finite plate has geometry and load but no qualified exact reference or feasible authorized independent finite-domain solve. Heywood correlation and infinite Kirsch cannot supply one; VM142 is a different specified problem.
- Baselines: Labels, applicable-check matrix, independent truth admission and human review remain incomplete; no policy execution or M1.2/M2 completion.

The VM92 published outer-wall display discrepancy remains in the parent qualification report.
No new source-rights, naming, recruitment, publication, hardware or reserved-data decision is implied.
