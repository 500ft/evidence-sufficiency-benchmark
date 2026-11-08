# CAD host follow-up

The current host uses SOLIDWORKS 2026, build 34.2.1, through
`SldWorks.Application.34`. A second 2024 installation exists, so the shared
connection helper now accepts a version-specific ProgID and defaults to 34.
`cadloop/host_session.py` holds an OS lock for each native job; its owner JSON
is diagnostic history and does not prove that a process is still running.

The native pilot found a material gap: correct body geometry at an explicitly
supplied density coexisted with an unassigned document material. The material
helper assigns from the installed database, reads the actual document density
and mass overrides, and supports a clean-session persistence check. Do not infer
that assignment succeeded from the void setter's return value.

Executed host evidence is in the CAD handoff's Desktop analysis folders:

- `native-material-audit/result.json`: clamp, tube and sleeve assignment/readback.
- `native-material-audit/assembly_mass_result.json`: reopened assembly mass sum.
- `native-sleeve-verification/result.json`: all saved sleeve variables changed,
  matched against the oracle, restored and checked after a fresh launch; native
  file bytes stayed unchanged.
- `S2R-SIM-05/model_02_weak_springs/S2R-SIM-05_workbench_verification.json`:
  actual solver loads, constraints, material and controls matched the Mechanical
  review deck and archive reopen. The strength result remains unqualified.

`cadloop/fea/local_session.py` launches the installed Student MAPDL locally and
closes its own session. It deliberately omits an explicit IP argument: the
installed PyMAPDL treats that argument as a request to connect to a remote
instance. The solver path is a host setting in this helper; no licence is
installed or changed.

`cadloop/fea/expand_load_blocks.py` expands the real static model's CDB constraint
and force blocks for External Model import while preserving numeric literals
and the remaining file. Its conversion report records hashes and counts. It
rejects unfamiliar record formats and nonzero imaginary loads; it is not a
general harmonic-load converter.

`cadloop/render_step.py` creates STEP review images. The installed host Python
needs CadQuery/OCP, NumPy and PyVista for that optional script, and pywin32 for
native material access. The core verifier's dependency list is unchanged.
These helpers do not turn a CAD check or a solver result into physical validation.
