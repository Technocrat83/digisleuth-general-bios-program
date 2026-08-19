# RAW_COUPLED03_TERMINAL_FAILURE_RESIDUE_v0.1

**EXPERIMENT:** `HD_COUPLED_OMISSION_EXPERIMENT_03`  
**BINDING ROOT:** `cd69b886effaac7b919d60adb0c821960657fa8fc80505d25bbfefe52649f875`  
**EXECUTION AUTHORIZATION:** `CONSUMED`  
**INVOCATIONS REMAINING:** `0`  
**EXECUTION RESULT CLASS:** `RAW_TERMINAL_FAILURE_RESIDUE`  
**SCIENTIFIC AUTHORITY:** `ZERO`  
**ADJUDICATION AUTHORITY:** `ZERO`  
**PP:** `BLOCKED`

## Invocation boundary

The one-shot execution authorization was consumed at invocation against the frozen binding root above.

The bound runner `R.run_once(...)` requires the following runtime inputs before scientific execution can occur:

- a pre-sealed `HelmCommitment`;
- `delta_phi_exposed_at_ns`;
- `specimen_a_pre` and `specimen_a_post` `Phi.PhenotypeState` values;
- `specimen_b_pre` and `specimen_b_post` `Phi.PhenotypeState` values.

No repository-resident frozen execution-input object containing those required values was found at invocation time. No Pentroforma/Helm commitment artifact or frozen pre/post phenotype-state bank was available to supply them.

## Terminal condition

The runner was therefore not supplied invented or post-hoc values. The invocation terminated at the execution-input boundary rather than repairing the missing upstream execution inputs.

`Missing frozen execution inputs != authority to synthesize execution inputs.`

No second invocation is authorized.

## Raw failure facts

```text
H_BIND03:
  cd69b886effaac7b919d60adb0c821960657fa8fc80505d25bbfefe52649f875

AUTHORIZATION_STATE_BEFORE_INVOCATION:
  AUTHORIZED_UNCONSUMED

AUTHORIZATION_STATE_AFTER_INVOCATION:
  CONSUMED

INVOCATIONS_REMAINING:
  0

RUNNER_ENTRYPOINT:
  R.run_once

ENTRYPOINT_BODY_EXECUTED:
  FALSE

TERMINAL_FAILURE:
  REQUIRED_FROZEN_EXECUTION_INPUTS_NOT_AVAILABLE

MISSING_AT_INVOCATION:
  PRESEALED_HELM_COMMITMENT
  DELTA_PHI_EXPOSURE_TIMESTAMP
  SPECIMEN_A_PRE_PHI_STATE
  SPECIMEN_A_POST_PHI_STATE
  SPECIMEN_B_PRE_PHI_STATE
  SPECIMEN_B_POST_PHI_STATE

REPAIR_ATTEMPTED:
  FALSE

SYNTHETIC_INPUT_SUBSTITUTION:
  FALSE

RERUN_ATTEMPTED:
  FALSE

C_03:
  (U,U,U,U)

PASS_COUPLED03:
  UNRESOLVED

LINEAGE_BRANCH:
  LOCKED

SCIENTIFIC_STANDING_DELTA:
  ZERO

PP:
  BLOCKED
```

## Closure

`Authorization consumption != successful execution != evidence adjudication.`

This residue records the terminal reality of the single authorized invocation attempt. It does not assign C1-C4 and does not authorize a retry.