# OAB Fixture Loader v0.1

## Classification

`STATIC_TYPED_FIXTURE_INGRESS`

This package is the constitutional ingress membrane between persisted OAB fixture bytes and any future runtime runner.

It implements the boundary:

```text
Persisted Fixture Bytes
  -> Frozen Battery Manifest
  -> Typed Fixture Loader
  -> LoadedFixture
```

It does **not** implement:

```text
Raw Fixture -> Runner
```

and it confers no interpretation, repair, admission, or execution authority.

## Governing law

> The loader may recover declared fixture meaning; it may not manufacture missing fixture meaning.

Load success is intentionally non-equivalent to scientific or runtime validity:

```text
FixtureLoadSuccess != FixtureValidity
FixtureValidity != RuntimeSuccess
RuntimeSuccess != ScientificStanding
```

## Frozen semantic bindings

The battery manifest binds ingress to these semantic identities:

```text
ORIENTATION_DELTA_CANONICAL_ENCODING_v0.1
JLK_ORIENTATION_DELTA_LOCALIZATION_HOOK_v0.1
ORIENTATION_INVALIDATION_MONITOR_v0.1
ORIENTATION_REPLAY_VALIDATOR_v0.1
```

The current OAB fixture files predate explicit per-fixture rule-identity fields. They are therefore left byte-for-byte untouched. The loader binds their semantic environment through `battery_manifest.json` rather than rewriting already-tested fixtures.

This preserves the distinction:

```text
Existing Fixture Lineage != Loader Semantic Binding
```

## Files

```text
battery_manifest.json
fixture_loader.py
loader_contract.schema.json
static_loader_battery.py
README.md
```

## Loader output

`fixture_loader.py` returns a `LoadedFixture` containing:

```text
fixture_id
source_path
sha256
manifest_id
battery_id
semantic_bindings
fixture
disposition
```

The only affirmative disposition currently emitted by successful ingress is:

```text
LOADED
```

Ingress deficiencies raise typed `FixtureIngressError` failures rather than being repaired or inferred.

## Jurisdiction hardening

Any jurisdiction member represented as a hexadecimal identifier beginning with `0x` must match:

```text
0x + exactly 32 hexadecimal nybbles
```

No padding or inferred width correction is allowed.

## Loader adversarial battery

`static_loader_battery.py` covers:

```text
FL1  missing required field
FL2  frozen semantic rule drift
FL3  fixture/delta identity divergence
FL4  jurisdiction width violation
FL5  unknown fixture type
FL6  fixture digest mismatch
FL7  missing semantic requirement is rejected, not inferred
FL8  affirmative valid-control ingress
```

FL8 is mandatory so the loader cannot qualify merely by rejecting every input.

## Authority posture

```text
INTERPRETATION_AUTHORITY: 0
REPAIR_AUTHORITY: 0
ADMISSION_AUTHORITY: 0
EXECUTION_AUTHORITY: 0
CANON_DELTA: 0
PP: BLOCKED
```

## Next lawful frontier

After this ingress membrane is independently conformed, the next artifact may be specified as:

```text
ORIENTATION_RUNTIME_RUNNER_v0.1
```

The future runner must consume `LoadedFixture` outputs. It must not consume raw fixture JSON directly.
