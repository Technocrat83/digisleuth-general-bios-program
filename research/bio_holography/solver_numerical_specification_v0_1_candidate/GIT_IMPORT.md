# Prospective Git import — candidate specification

This record imports the current solver specification candidate v0.1, revision 2.
The original reviewed archive is preserved under artifacts/, and its 20 source
snapshot files are preserved byte-for-byte in this directory. GIT_IMPORT_RECEIPT.json
binds the archive digest, source revision, branch base and reproduced checks.
GIT_SHA256SUMS.txt covers the import files and archive; SHA256SUMS is the original
source package manifest.

The containing commit supplies the prospective Git ancestry. Historical package
receipts stating that their preparation run performed no Git write remain accurate
and unchanged. They do not describe the later import event.

Validation: 31/31 algebraic and cohort-bookkeeping reference tests reproduced;
19 source content digests verified; all JSON parsed; the 34-field schema and
baseline wild-type/unperturbed declarations were checked for contract consistency.
No automated JSON Schema Draft 2020-12 qualification is claimed.

Standing: candidate specification. Calibration and release: HOLD. Full solver
implementation and numerical qualification remain unexecuted. Cohort membership,
physical parameters and authenticated freezes remain pending. Authority enforcement:
NOT_EVALUATED. Promotion authority: false.
