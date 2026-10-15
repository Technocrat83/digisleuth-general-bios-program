# Specification review — candidate v0.1, revision 2

The existing numerical branch BH_CZ_KV_OPENING_FV_3D_V1 specifies the contact/debonding law, water–solute coupling, initial/boundary conditions, topology-change rules and 17 full-solver acceptance families. Revision 2 retains those equations and numerical controls.

The cohort schema previously recorded treatment batches and a genotype-record digest, but did not require a specimen treatment record or explicit genotype/treatment classification. Revision 2 requires genotype_status, treatment_condition and treatment_record_sha256. Both baseline partitions require WILD_TYPE and BASELINE_UNPERTURBED declarations. These declarations require authenticated evidence review before admission. A valid digest establishes byte identity only.

Dam, litter, harvest-event and culture-dish grouping remains the split rule. Collection, acquisition and treatment batches remain explicit diagnostics. Batch entropy cannot establish independence or effective sample size. Actual cohort membership, design sufficiency, physical coefficients and authenticated freezes remain pending.

Review verification is limited to package content consistency, reference fixture rerun, JSON/contract consistency, and the unchanged parent link. JSON Schema Draft 2020-12 validator execution was unavailable in the review environment; no automated schema-conformance result is claimed. Full-solver acceptance, biological calibration, blind validation and authority enforcement remain unexecuted or not evaluated as recorded in standing_receipt.json.
