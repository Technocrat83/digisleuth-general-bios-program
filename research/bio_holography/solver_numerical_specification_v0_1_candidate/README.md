# Solver Numerical Specification — candidate v0.1, revision 2

Selected branch: BH_CZ_KV_OPENING_FV_3D_V1. Calibration remains HOLD.

SOLVER_SPECIFICATION.md explains the cohesive contact law, finite cell/cleft water and solute coupling, initial/boundary conditions, topology rules, numerical scheme, and cohort requirements. solver_contract.json pins their candidate design constants. Physical coefficients and run scales remain unmeasured/unfrozen.

numerical_acceptance_tests.json defines 17 full-solver acceptance families, all NOT_EXECUTED. reference_laws.py and test_reference_specification.py exercise algebraic laws and cohort metadata boundaries only. They contain no tissue integrator, calibration optimizer, or execution authority enforcement.

parameter_roles.json maps all 18 parent parameter groups and lists 25 groups required or derived by this branch. cohort_requirements.json and cohort_member.schema.json define the solver-specific data requirements. cohort_manifest_template.json has no actual members. cohort_audit.py checks dam/litter/harvest/dish grouping and reports batch diagnostics; metadata completeness never grants admission.

Run the reference fixture checks with Python 3 standard library:

```bash
python3 -m unittest -v test_reference_specification
```

reference_check_receipt.json records the actual result. standing_receipt.json separates reference verification from full numerical solver qualification, biological calibration, validation, and authority enforcement. parent_lineage.json binds the unchanged parent archive. SHA256SUMS hashes this package's files; it is not an authenticated parameter or cohort freeze.

Revision 2 adds specimen-level genotype/treatment declarations and a treatment-record digest. Both baseline partitions require wild-type, unperturbed declarations subject to authenticated review. The numerical branch is unchanged. SPECIFICATION_REVIEW.md and revision_lineage.json record the revision and previous artifact digest. Cohort membership remains unmaterialized.
