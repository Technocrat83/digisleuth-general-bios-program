# JLK_ORIENTATION_DELTA_LOCALIZATION_HOOK_v0.1

**Class:** JURISDICTIONAL_BOUNDARY_LOCALIZATION_APPARATUS  
**Parent:** JLK_OMEGA_LOCALIZATION_CONTRACT_v0.1  
**Authority:** LOCALIZE_PERTURBATION_ONLY  
**Admission Authority:** NONE  
**Invalidation Authority:** NONE  
**Execution Authority:** NONE  
**Repair Authority:** NONE  
**PP:** BLOCKED  

## Constitutional ordering

`Boundary Semantics -> Witness-Producing Hook -> Fixture Oracle -> Concrete Fixtures`

`Perturbation Detection != Localization != Invalidation`

JLK consumes an observed field delta and emits:

`L_delta = <I_O, I_delta, C-_delta, C+_delta, dXi_delta, S_delta, U_delta, epsilon>`

JLK may identify demonstrated intersections with causal/provenance and jurisdictional consequence cones. It may not withdraw orientation, repair orientation, grant authority, change jurisdiction, admit an object, or execute an object.

## Localization standing

`LocalizationStanding in {LOCALIZED, NO_MATERIAL_INTERSECTION, UNRESOLVED}`

- `LOCALIZED`: demonstrated material intersection exists.
- `NO_MATERIAL_INTERSECTION`: sufficient evidence establishes that the perturbation does not intersect orientation-relevant surfaces.
- `UNRESOLVED`: available evidence cannot establish either material intersection or non-intersection.

`UNRESOLVED != LOCALIZED != NO_MATERIAL_INTERSECTION`

## 128-bit jurisdiction identifier

Jurisdiction members are exactly 16 bytes. JSON serialization is lowercase or uppercase hexadecimal with the `0x` prefix plus exactly 32 hexadecimal nybbles.

Padding, truncation, inference, or flexible-width coercion is prohibited.

## Zero-authority interfaces

Intentionally absent:

- `withdraw_orientation`
- `repair_orientation`
- `grant_authority`
- `change_jurisdiction`
- `admit_object`
- `execute_object`

## Lifecycle handoff

The Orientation Lifecycle Monitor consumes the localization witness and independently emits one of:

`CURRENT | SUSPENDED | WITHDRAWN`

JLK does not decide lifecycle status.
