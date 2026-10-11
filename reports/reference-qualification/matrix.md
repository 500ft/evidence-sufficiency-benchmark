# Development reference qualification

**Pending independent human review. M1.2 remains incomplete.**

3 distinct development families; 0 admitted problems; 0 independent human reviews.

The axial family reuses [M1.1](../claim-sufficiency/matrix.md), including its original
loading conventions, tolerances and stiffness cross-checks. Its configurations
are counted once. No axial outputs or figures were regenerated.

Source: [results.json](results.json). [Contract, derivations and limitations](../../studies/reference_qualification/README.md).

The following controls compare exact closed-form answers with separately assembled
stiffness or heat-balance systems. Fractions in JSON retain the exact values.

## Beam bending

| Control | Observable [unit] | Reference | Binary64 tolerance | Exact cross-checks |
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

## Steady heat conduction

| Control | Observable [unit] | Reference | Binary64 tolerance | Exact cross-checks |
| :--- | :--- | ---: | ---: | :---: |
| nominal | midpoint temperature [K] | 350 | 5.68e-14 | 3/3 |
| nominal | heat flux [W/m^2] | 100 | 1.42e-14 | 3/3 |
| equal face temperatures | midpoint temperature [K] | 400 | 5.68e-14 | 3/3 |
| equal face temperatures | heat flux [W/m^2] | 0 | 4.94e-324 | 3/3 |
| reversed gradient | midpoint temperature [K] | 350 | 5.68e-14 | 3/3 |
| reversed gradient | heat flux [W/m^2] | -100 | 1.42e-14 | 3/3 |
| double conductivity | midpoint temperature [K] | 350 | 5.68e-14 | 3/3 |
| double conductivity | heat flux [W/m^2] | 200 | 2.84e-14 | 3/3 |

Exact equality is the qualification criterion. The tolerance column applies only
to binary64 serialization of each exact claim; it is one ULP in that row's unit.
It is not a physical allowable or a tolerance for an approximate FEA model.
Changing partitions tests assembly and boundary handling; these polynomial
problems do not establish general mesh convergence or statistical independence.

The thermal HTML source omits x in its printed solution; the pinned PDF includes
it. The implemented solution satisfies both face temperatures and heat balance.

Reproduce: `python -m studies.reference_qualification.run`.
