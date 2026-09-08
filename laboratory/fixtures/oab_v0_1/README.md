# OAB1–OAB8 Fixture Family v0.1

These fixtures are compiled **after** `JLK_ORIENTATION_DELTA_LOCALIZATION_HOOK_v0.1` and the lifecycle monitor semantics.

Each fixture carries two independent oracle surfaces: `expected_localization` and `expected_monitor`.

A chamber passes only when the implementation reaches the correct lifecycle disposition **for the correct localized geometric reason**.

`Correct Disposition != Correct Localization`

The family is single-fault by construction.

## Lifecycle algebra

`CURRENT | SUSPENDED | WITHDRAWN`

Historical witnesses are never rewritten by these fixtures.

OAB4 withdraws current orientation while preserving epistemic standing. OAB7 suspends current use after unauthorized execution attempt without falsifying prior orientation. OAB8 is the mandatory affirmative continuity control.

`PASS_OAB = L0 ∧ D0 ∧ R0 ∧ A0 ∧ H0 ∧ M_continuity`
