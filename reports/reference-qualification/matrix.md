# Development reference qualification

**Pending independent human review. M1.2 remains incomplete.**

4 distinct development families; 0 admitted problems; 0 independent human reviews.

The axial family reuses [M1.1](../claim-sufficiency/matrix.md), including its original
loading conventions, tolerances and stiffness cross-checks. Its configurations
are counted once. No axial outputs or figures were regenerated.

Source: [results.json](results.json). [Contract, derivations and limitations](../../studies/reference_qualification/README.md).

The controls compare closed-form answers with separate stiffness, heat-balance or
radial boundary-value solutions. Fractions in JSON retain exact references.

## cantilever uniform load

| Control | Observable [unit] | Reference | Claim tolerance | Cross-check passes |
| :--- | :--- | ---: | ---: | :---: |
| nominal | tip deflection [m] | 0.000486 | 5.42e-20 | 3/3 |
| nominal | root stress [Pa] | 5400000 | 9.31e-10 | 3/3 |
| nominal | support force [N] | -6 | 8.88e-16 | 3/3 |
| nominal | support moment [N*m] | -1.8 | 2.22e-16 | 3/3 |
| zero load | tip deflection [m] | 0 | 4.94e-324 | 3/3 |
| zero load | root stress [Pa] | 0 | 4.94e-324 | 3/3 |
| zero load | support force [N] | 0 | 4.94e-324 | 3/3 |
| zero load | support moment [N*m] | 0 | 4.94e-324 | 3/3 |
| reversed load | tip deflection [m] | -0.000486 | 5.42e-20 | 3/3 |
| reversed load | root stress [Pa] | 5400000 | 9.31e-10 | 3/3 |
| reversed load | support force [N] | 6 | 8.88e-16 | 3/3 |
| reversed load | support moment [N*m] | 1.8 | 2.22e-16 | 3/3 |
| double modulus | tip deflection [m] | 0.000243 | 2.71e-20 | 3/3 |
| double modulus | root stress [Pa] | 5400000 | 9.31e-10 | 3/3 |
| double modulus | support force [N] | -6 | 8.88e-16 | 3/3 |
| double modulus | support moment [N*m] | -1.8 | 2.22e-16 | 3/3 |

## slab dirichlet

| Control | Observable [unit] | Reference | Claim tolerance | Cross-check passes |
| :--- | :--- | ---: | ---: | :---: |
| nominal | midpoint temperature [K] | 350 | 5.68e-14 | 3/3 |
| nominal | heat flux [W/m^2] | 100 | 1.42e-14 | 3/3 |
| equal face temperatures | midpoint temperature [K] | 400 | 5.68e-14 | 3/3 |
| equal face temperatures | heat flux [W/m^2] | 0 | 4.94e-324 | 3/3 |
| reversed gradient | midpoint temperature [K] | 350 | 5.68e-14 | 3/3 |
| reversed gradient | heat flux [W/m^2] | -100 | 1.42e-14 | 3/3 |
| double conductivity | midpoint temperature [K] | 350 | 5.68e-14 | 3/3 |
| double conductivity | heat flux [W/m^2] | 200 | 2.84e-14 | 3/3 |

## vm25 pressure only

| Control | Observable [unit] | Reference | Claim tolerance | Cross-check passes |
| :--- | :--- | ---: | ---: | :---: |
| nominal | inner displacement [in] | 0.00786666667 | 4e-09 | 3/3 |
| nominal | inner radial stress [psi] | -30000 | 0.03 | 3/3 |
| nominal | inner hoop stress [psi] | 50000 | 0.03 | 3/3 |
| nominal | mid radial stress [psi] | -7777.77778 | 0.03 | 3/3 |
| nominal | mid hoop stress [psi] | 27777.7778 | 0.03 | 3/3 |
| nominal | outer radial stress [psi] | 0 | 0.03 | 3/3 |
| nominal | outer hoop stress [psi] | 20000 | 0.03 | 3/3 |
| zero pressure | inner displacement [in] | 0 | 0 | 3/3 |
| zero pressure | inner radial stress [psi] | 0 | 0 | 3/3 |
| zero pressure | inner hoop stress [psi] | 0 | 0 | 3/3 |
| zero pressure | mid radial stress [psi] | 0 | 0 | 3/3 |
| zero pressure | mid hoop stress [psi] | 0 | 0 | 3/3 |
| zero pressure | outer radial stress [psi] | 0 | 0 | 3/3 |
| zero pressure | outer hoop stress [psi] | 0 | 0 | 3/3 |
| half modulus | inner displacement [in] | 0.0157333333 | 8e-09 | 3/3 |
| half modulus | inner radial stress [psi] | -30000 | 0.03 | 3/3 |
| half modulus | inner hoop stress [psi] | 50000 | 0.03 | 3/3 |
| half modulus | mid radial stress [psi] | -7777.77778 | 0.03 | 3/3 |
| half modulus | mid hoop stress [psi] | 27777.7778 | 0.03 | 3/3 |
| half modulus | outer radial stress [psi] | 0 | 0.03 | 3/3 |
| half modulus | outer hoop stress [psi] | 20000 | 0.03 | 3/3 |
| zero poisson | inner displacement [in] | 0.00666666667 | 4e-09 | 3/3 |
| zero poisson | inner radial stress [psi] | -30000 | 0.03 | 3/3 |
| zero poisson | inner hoop stress [psi] | 50000 | 0.03 | 3/3 |
| zero poisson | mid radial stress [psi] | -7777.77778 | 0.03 | 3/3 |
| zero poisson | mid hoop stress [psi] | 27777.7778 | 0.03 | 3/3 |
| zero poisson | outer radial stress [psi] | 0 | 0.03 | 3/3 |
| zero poisson | outer hoop stress [psi] | 20000 | 0.03 | 3/3 |

Cylinder claims and cross-checks use the declared numerical budget; step refinement is shown separately:

| Control | Radial steps | Inner displacement error [in] | Budget [in] | Inner hoop error [psi] | Budget [psi] |
| :--- | ---: | ---: | ---: | ---: | ---: |
| nominal | 32 | 2.88e-10 | 4e-09 | 0.00216 | 0.03 |
| nominal | 64 | 1.79e-11 | 4e-09 | 0.000135 | 0.03 |
| nominal | 128 | 1.12e-12 | 4e-09 | 8.39e-06 | 0.03 |
| zero_pressure | 32 | 0 | 0 | 0 | 0 |
| zero_pressure | 64 | 0 | 0 | 0 | 0 |
| zero_pressure | 128 | 0 | 0 | 0 | 0 |
| half_modulus | 32 | 5.75e-10 | 8e-09 | 0.00216 | 0.03 |
| half_modulus | 64 | 3.59e-11 | 8e-09 | 0.000135 | 0.03 |
| half_modulus | 128 | 2.24e-12 | 8e-09 | 8.39e-06 | 0.03 |
| zero_poisson | 32 | 2.12e-10 | 4e-09 | 0.00159 | 0.03 |
| zero_poisson | 64 | 1.33e-11 | 4e-09 | 9.95e-05 | 0.03 |
| zero_poisson | 128 | 8.29e-13 | 4e-09 | 6.21e-06 | 0.03 |

Published targets are coarse source evidence, separate from qualification:

| Observable | Published display | Derived value | Difference | Display unit | Within half unit | Within one unit |
| :--- | ---: | ---: | ---: | ---: | :---: | :---: |
| inner_displacement | 0.0078666 | 0.007866666667 | 6.67e-08 | 0.0000001 | False | True |
| inner_radial_stress | -30000 | -30000 | 0 | 1 | True | True |
| mid_radial_stress | -7778 | -7777.777778 | 0.222 | 1 | True | True |
| outer_radial_stress | 0 | 0 | 0 | 1 | True | True |
| inner_hoop_stress | 50000 | 50000 | 0 | 1 | True | True |
| mid_hoop_stress | 27778 | 27777.77778 | 0.222 | 1 | True | True |
| outer_hoop_stress | 20000 | 20000 | 0 | 1 | True | True |

Units match the claim table above. A one-unit comparison does not establish the source's rounding mode.

## vm92 layered wall

| Control | Observable [unit] | Reference | Claim tolerance | Cross-check passes |
| :--- | :--- | ---: | ---: | :---: |
| nominal | heat rate [Btu/hr] | 513.406593 | 1.14e-13 | 3/3 |
| nominal | inner surface temperature [degF] | 2957.21612 | 4.55e-13 | 3/3 |
| nominal | interface temperature [degF] | 2475.89744 | 4.55e-13 | 3/3 |
| nominal | outer surface temperature [degF] | 336.703297 | 5.68e-14 | 3/3 |
| equal fluid temperatures | heat rate [Btu/hr] | 0 | 4.94e-324 | 3/3 |
| equal fluid temperatures | inner surface temperature [degF] | 3000 | 4.55e-13 | 3/3 |
| equal fluid temperatures | interface temperature [degF] | 3000 | 4.55e-13 | 3/3 |
| equal fluid temperatures | outer surface temperature [degF] | 3000 | 4.55e-13 | 3/3 |
| reversed heat flow | heat rate [Btu/hr] | -513.406593 | 1.14e-13 | 3/3 |
| reversed heat flow | inner surface temperature [degF] | 122.783883 | 1.42e-14 | 3/3 |
| reversed heat flow | interface temperature [degF] | 604.102564 | 1.14e-13 | 3/3 |
| reversed heat flow | outer surface temperature [degF] | 2743.2967 | 4.55e-13 | 3/3 |
| double area | heat rate [Btu/hr] | 1026.81319 | 2.27e-13 | 3/3 |
| double area | inner surface temperature [degF] | 2957.21612 | 4.55e-13 | 3/3 |
| double area | interface temperature [degF] | 2475.89744 | 4.55e-13 | 3/3 |
| double area | outer surface temperature [degF] | 336.703297 | 5.68e-14 | 3/3 |

Published targets are coarse source evidence, separate from qualification:

| Observable | Published display | Derived value | Difference | Display unit | Within half unit | Within one unit |
| :--- | ---: | ---: | ---: | ---: | :---: | :---: |
| heat_rate | 513 | 513.4065934 | 0.407 | 1 | True | True |
| inner_surface_temperature | 2957 | 2957.216117 | 0.216 | 1 | True | True |
| outer_surface_temperature | 336 | 336.7032967 | 0.703 | 1 | False | True |

Units match the claim table above. A one-unit comparison does not establish the source's rounding mode.

Rational stiffness/conduction comparisons require exact equality; the cylinder uses its stated budget.
Claim tolerances are one ULP for exact-route binary64 serialization, and the
declared characteristic-scale budget for the cylinder, in each row's unit.
It is not a physical allowable or a tolerance for an approximate FEA model.
Partition and step refinements test the declared observables and boundary handling;
they do not establish general FEA convergence or statistical independence.

The thermal HTML source omits x in its printed solution; the pinned PDF includes
it. The implemented solution satisfies both face temperatures and heat balance.

Reproduce: `python -m studies.reference_qualification.run`.
