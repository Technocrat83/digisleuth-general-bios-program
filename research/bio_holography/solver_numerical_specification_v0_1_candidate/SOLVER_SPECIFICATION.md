# Bio Holography Solver Numerical Specification — candidate v0.1, revision 2

## Standing and parent

Selected branch: BH_CZ_KV_OPENING_FV_3D_V1. This selection pins a candidate mathematical and numerical design. Physical parameter values, cohort admission, software/environment bindings, and authenticated execution freezes remain unestablished. Calibration is HOLD; ratification is withheld. No tissue solver is implemented or run by this package.

Parent: BIO_HOLOGRAPHY_MECHANICAL_STATE_MACHINE_v0.1_candidate.zip. Authoritative parent bytes were retrieved and all 13 member digests verified. Parent archive SHA-256: 9ff3df41eec507477c9d212fb8af97587677a5d71e4d48b17d9529b0b2c91d88. The parent remains unchanged. The selected branch specializes its formerly unselected contact and transport laws.

The 2021 hydro-osmotic model concerns existing lumens and separates hydraulic exchange from membrane permeation and active solute pumping [1]. The 2023 membrane-adhesion study provides a useful physical comparison using lipid vesicles [2]. This specification is an independently proposed reduction for mouse embryo evaluation; it is not a reproduction of either study's solver.

## 1. Branch, domain, and scope

Use three-dimensional triangulated cell/cortex surfaces and finite-volume fluid compartments. Each initial adhesive interface contains a positive, fluid-filled molecular cleft of independently constrained resting thickness h0. All interstitial clefts and junction reservoirs exist in the initial water inventory. A visible microlumen is an expanded region of this fluid domain, not water created by an event.

Cell cytoplasm is a finite, well-mixed water/solute compartment. The external culture bath supplies prescribed pressure p_b, effective osmolyte concentration c_b, and temperature Theta. Each cell has a fixed independently constrained non-osmotic volume V_dry,i and tracked water volume W_i. Mechanical cell volume is V_dry,i + W_i; c_i=N_i/W_i. This avoids silently holding cell volume fixed while transferring its water into lumens.

Branch limits: opening-dominated adhesive separation, positive wet clefts, Newtonian fluid, one effective osmolyte, well-mixed cell and lumen compartments, constant cortical tensions and active pumping per declared cell/interface class within the admitted observation window, and no cell division or adhesive repair. These are candidate approximations requiring independent adequacy assessment. Biological observation of repair, division, substantial shear, concentration gradients inconsistent with mixing, or unresolved wetting produces MODEL_SCOPE_EXCEEDED or UNRESOLVED. It does not automatically count as a failed biological prediction.

Three-dimensional geometry is retained because cavity position is an outcome. A chain model alone cannot establish a three-dimensional position prediction. Pressure is solved through coupled mechanical and volume constraints; a spherical Laplace formula is reserved for an analytic verification fixture.

## 2. Contact/debonding law — alpha

For an initially bound material patch, let delta = h-h0 >= 0 be its normal opening. Enforce nonpenetration of the resting cleft by a complementarity reaction. This is a finite-gap molecular-contact reduction, not a numerical aperture floor that may be tuned to rescue a fit.

Specify independent parameters K_n > 0 (Pa/m), t0 > 0 (Pa), W0 > 0 (J/m2), and eta_n >= 0 (Pa s/m). Define

\[
\delta_0=t_0/K_n,\qquad \delta_f=2W_0/t_0,\qquad \delta_f>\delta_0.
\]

The equilibrium loading envelope is

\[
t_{eq}(\delta)=
\begin{cases}
K_n\delta & 0\le\delta\le\delta_0,\\
t_0(\delta_f-\delta)/(\delta_f-\delta_0)&\delta_0<\delta<\delta_f,\\
0&\delta\ge\delta_f.
\end{cases}
\]

Use maximum opening kappa(t)=max_{s<=t} delta(s). Damage is 0 for kappa<=delta0, 1 for kappa>=deltaf, and otherwise

\[
d(\kappa)=\frac{\delta_f(\kappa-\delta_0)}{\kappa(\delta_f-\delta_0)}.
\]

On loading and unloading,

\[
t_n=(1-d)K_n\delta+(1-d)\eta_n\dot\delta.
\]

The signed viscous term resists relative velocity and has nonnegative dissipation (1-d) eta_n dot(delta)^2. It is not an additional damage trigger. Damage follows the equilibrium opening history, so t0 is the equilibrium peak rather than a universal maximum dynamic traction. W0 is the area under the quasistatic loading envelope; finite-rate work also includes viscous dissipation. Unloading preserves damage and follows the degraded stiffness. No healing or bond-occupancy kinetics are fitted in this branch.

Tangential relative motion has only residual viscous drag t_s=(1-d) eta_s v_s, eta_s>=0, independently constrained. This branch has no shear-induced damage law. Its admission/scope bound is ||t_s||/t0 <= 0.1 for every material patch. Exceeding the bound halts that branch. The value 0.1 is a pinned candidate scope criterion, not an experimental constant.

Contact dissipation is integrated over reference patch area. The effective Kelvin-Voigt retardation scale eta_n/K_n is reportable; it is not a stress-relaxation time. Fixed-opening stress relaxation or significant adhesion recovery requires another branch.

Use bare cortical surface tensions on all cell membrane patches, including both sides of adhesive interfaces. Adhesion contributes once through the cohesive law. An effective gamma_cc already containing adhesion is excluded as an independent optimizer parameter. Derived contact-angle descriptors may be compared with observations, with their constitutive mapping stated explicitly.

## 3. Geometry and pressure coupling

With X the surface-node coordinates and p_r the pressure of each finite compartment, solve the overdamped force balance

\[
M_\zeta\dot X+\nabla_XE_\gamma+F_{cohesive}+F_{viscous}-\sum_r p_r\nabla_XV_r^{geom}+F_{constraint}=0.
\]

Here E_gamma=sum_f gamma_f A_f; cohesive forces use the equilibrium degraded stiffness, while contact viscosity and global drag are separate positive dissipative terms. All force assembly uses patch-area quadrature and a frozen surface/incidence map. Fluid and cell compartment volumes must satisfy

\[
V_q^{geom}(X)=V_q,\qquad V_i^{geom}(X)=V_{dry,i}+W_i.
\]

Pressure multipliers load adjoining surfaces with opposing orientations. Set the pressure gauge p_b=0 and report all pressures relative to it. Geometry assembly must pass a pressure-work check using dV/dX. Surface curvature comes from this geometric force discretization; do not impose an extra spherical pressure closure on top of it.

Unilateral surface contact, hard resting-cleft bounds, rigid-motion removal, and volume constraints are enforced explicitly. Remove rigid translation/rotation using a reference frame derived from initial data. Boundaries for confinement are prescribed obstacle surfaces and contact reactions. Future observed geometry must not be fed into a prediction run.

## 4. Water–solute coupling — beta

Finite-volume compartments include expanded lumen regions, background interstitial clefts, and finite cells. All geometries, concentrations, and inventories use SI units. Flux signs are positive from source to target.

For an interstitial slit edge a->b with height h, width w, length ell, and viscosity mu,

\[
Q_{a\to b}=H_{ab}(p_a-p_b),\qquad H_{ab}=wh^3/(12\mu\ell).
\]

H has units m3/(Pa s). The slit reduction requires h/ell<=0.1 and h/w<=0.1 and a declared low-inertia validity bound Re<=0.1. Those are candidate scope bounds. Resolved cavities may be well mixed; their connecting necks must meet the slit assumptions or require a different edge model.

Define slit Re using characteristic height h as rho |Q| h/(w h mu). Fluid density is independently constrained. For a diffusively mixed lumen, require its independently bounded mixing time to be <=0.1 of the exchange timescale; cells require their own tracer/mixing adequacy review. A scope failure triggers an alternate model rather than a hidden transport-coefficient adjustment.

With A_ab=wh and c_a=n_a/V_a,

\[
J_{a\to b}=D A_{ab}(c_a-c_b)/\ell+Q_{a\to b}c_{upwind}.
\]

Use source concentration for positive Q and target concentration for negative Q. Diffusion and conservative advection are both retained. No membrane osmotic-pressure jump is inserted across an open fluid bridge.

Across a cell i -> interstitial compartment q membrane,

\[
Q_{i\to q}=L_pA[(p_i-p_q)-s_rR_g\Theta(c_i-c_q)],
\]

\[
J_{i\to q}=A[j_a+P_s(c_i-c_q)]+(1-s_r)c_{upwind}Q_{i\to q}.
\]

The reflection coefficient s_r is in [0,1]. Lp, Ps, and s_r are independently constrained for each declared membrane class. Active j_a is an internal solute transfer; the receiving interstitial amount increases exactly as the source-cell amount decreases. Solvent drag uses the same signed solvent flux. Water flux contains no separate fitted pumping source. Active pumping changes concentration and hence osmotic flux. Bath-cell transport uses the same passive form with baseline j_a=0; any alternate bath pumping requires another declared input.

Balance dV_q/dt and dn_q/dt by summing signed edge and membrane fluxes. Balance dW_i/dt and dN_i/dt with the opposite membrane fluxes plus bath-cell exchange. Cell concentration uses positive W_i rather than total geometric volume. Bath exchange is the sole unbounded source/sink in the baseline finite-system budget.

An exterior leak, if admitted, is an explicit bath-fluid edge with independently constrained conductance and conservative solute flux. A sealed baseline requires independent seal evidence and a leakage bound; setting leak conductance to zero is conditional on that admission. Record the admitted numerical bound and its measurement uncertainty.

Global finite-system water and solute inventories must equal their initial inventories plus integrated signed bath transfers. Internal hydraulic exchange, passive membrane transfer, active ion pumping, and event reclassification cancel in this budget. Active transport and prescribed active tensions can supply chemical/mechanical power; a passive energy-decay check applies only when those sources and bath driving are disabled.

## 5. Initial and boundary conditions

Initialize only from independently annotated pre-prediction data: cell identities/classes, surface/contact geometry, material patch pairing, cleft/junction network, fluid volumes, cell water and dry volumes, solute amounts, initial separation history, and uncertainty. Solve a consistent mechanical/volume state at t0 before advancing. No earlier damage history may be silently set to zero unless a pre-rupture intact-contact observation supports it.

Bath p_b, c_b, temperature, culture composition, gas conditions, and passive bath membrane classes are fixed input records. Baseline cortical gamma and active j_a are constant per declared class over the window. Interventions are separately bound boundary/parameter changes, not automatic scalar equivalents of genetic knockdowns.

No lumen seeds, imposed asymmetry, unobserved contact noise, or favorable future cavity location are injected. The resting wet cleft is measured/bounded physical initial fluid. A symmetric initial condition produces an equivariant trajectory or a symmetry-preserving outcome distribution; it cannot justify a unique directional prediction. If unresolved nucleation physics requires extra heterogeneity, change the branch and preregister that input before testing.

## 6. Topology changes and observable classification

Numerical fluid-domain inventory and biological observables are separate layers. A background cleft becomes a resolved lumen when its reconstructed extent/volume exceeds the frozen observation operator's resolution threshold; classification reassigns inventory without adding water or solute.

Partial patch damage/separation preserves the cell-contact edge while resolved adhesive area remains. A fully failed patch has d=1. Delete a cell-pair adhesive edge only when all remaining paired adhesive patches are fully failed; maintain a separate uncertainty-aware observed-contact graph. Shrinking projected area alone cannot delete a material patch's residual adhesion.

Hydraulic connections persist as signed transport edges while their wet geometry exists. Positive hydraulic conductance between cavities does not merge their anatomical labels. A merger requires an actual open neck after the intervening adhesive partition fully fails, conservative redistribution, and a successful post-event mechanical constraint solve. Its event time is localized; if a connected union needs multiple pressure cells, retain them inside one anatomical cavity rather than forcing instantaneous pressure equality.

Drainage removes the resolved-lumen label when excess volume falls below the fixed observation threshold. All remaining water and solute stay in explicit cleft/junction compartments. Collective lumen collapse can therefore leave background interstitial fluid. Exterior-seal opening is a separate event/outcome; internal contact debonding never silently creates an exterior leak.

The six parent event types remain distinguishable: partial separation, complete debonding, repair, nucleation, drainage/collapse, merger. Five are representable in this branch; repair triggers MODEL_SCOPE_EXCEEDED. Cell division triggers the same scope halt as a separate lineage event. The five biological milestone labels and four milestone transitions remain observational; they do not force S5 or confer authority.

## 7. Numerical scheme and pinned candidate controls

Use monolithic implicit backward Euler for surface coordinates, cell/fluid water, solute amounts, compartment pressures, and opening-history damage. Solve algebraic volume/contact constraints together with transport. Use a semismooth Newton active-set iteration with residual-scaled line search and maximum 50 nonlinear iterations. Trial negative volume, cell water, solute, or invalid geometry rejects the trial; no clipping, abs-value repair, or unlogged floor is allowed.

Choose run scales from frozen initial data: L*=median equivalent-volume cell radius, V*=L*^3, p*=independently constrained reference cortical tension/L*, n*=c_b V*, and t*=reference acquisition frame interval. Physical run scales are unset until cohort admission. Zero/invalid scales cause input rejection.

The JSON numerical profile pins candidate dimensionless controls: nonlinear residual 1e-8; constraint residual 1e-8; step error rtol 1e-4 and normalized atol 1e-8; event-time tolerance 1e-4 t*; final global water/solute budget residual 1e-7; event remap residual 1e-10. These are numerical design criteria, not calibrated biological tolerances.

Scale coordinates/opening by L*, volume/water by V*, solute by n*, pressure by p*, and force by p* L*^2. Scale all assembled residual blocks by their corresponding run scales before applying the max norm. History and graph conditions are checked separately. Normalize global inventory discrepancies by initial inventory plus integrated absolute bath transfer plus the reference inventory scale; maintain local compartment residual checks so a large total cell inventory cannot hide a bad small-lumen balance.

Use full-step versus two-half-step error estimation; accept the two-half-step result. The error norm is the maximum scaled difference over X, fluid/cell water, and solute; separately require the contact-history, geometry, and global-budget conditions. Initial dt<=0.1 t*, maximum dt<=0.25 t*, minimum dt=1e-6 t*. Event bracketing refines to the event tolerance. Ambiguous simultaneous topology events are resolved as one conservative event group or cause UNRESOLVED_EVENT_GROUP; array iteration order cannot choose biology.

Align immutable cell/material-patch IDs and conservatively map trial fluid states to a common comparison partition. An unreconciled event-group difference or an unavailable conservative comparison map rejects the step and triggers event refinement. A graph-size mismatch must never be treated as an ordinary vector subtraction or silently ignored in the error estimate.

At most 20 step rejections, 1,000,000 accepted steps, 10,000 topology events, and 3,600 seconds wall time per synthetic numerical acceptance job. Exceeding a bound produces NUMERICAL_HALT with last accepted checkpoint and budget residuals. Biological job resource bounds must be separately frozen before execution. Missing solver implementation hash, environment lock, run manifest, or execution binding preserves HOLD.

Checkpoint and rollback include X, all fluid/cell water and solute, patch kappa/d, pressures, graph incidences, classifications, cumulative bath transfers, and event ledger. A rejected trial cannot mutate the accepted checkpoint. Replay pins binary/environment, mesh/partition ordering, optimizer seed if used, and output observation operator.

## 8. Acceptance tests and their standing

numerical_acceptance_tests.json defines 17 full-solver acceptance families: capillary balance, cohesive energy, irreversible unloading, osmotic equilibrium, closed/open budgets, analytic diffusion, advection/positivity, passive dissipation, spatial refinement, time/event refinement, rejection/rollback, partial debonding, conservative event maps, scope refusal, symmetry equivariance, cohort lineage boundaries, and replay.

Every full-solver acceptance family is NOT_EXECUTED. A small reference-law implementation and synthetic fixtures verify formulas and cohort bookkeeping only. Their results cannot be promoted to a tissue-solver PASS. A full-solver implementation must pass every applicable family and report non-applicable items with justified scope before any data-fitting request is admitted.

## 9. Parameter roles and cohort requirements

parameter_roles.json maps all 18 parent parameter groups and the additional quantities required by this branch. Mechanical and membrane coefficients generally need independent measurements or matched ancillary calibration, with uncertainty propagated. Only the declared active-pumping rates are conditionally fit from baseline trajectories after transport/mechanics bindings and concentration/inventory constraints are available. Rank/sensitivity profiles and profile-likelihood checks can still reject that fit as unidentifiable. Derived delta0, deltaf, and retardation scales are not additional free optimizer parameters.

The cohort requirements and member schema are finalized against this candidate branch. Actual membership, sample size, sampling adequacy, authenticated review, and cohort freeze remain pending. Every member requires embryo ID, dam ID, sire identity/status, litter ID, harvest/fertilization event, culture dish, collection batch, acquisition batch, treatment batch, operator/session, genotype/strain, age/stage, viability/seal evidence, physical voxel sizes, timestamps, instrument calibration, full-volume coverage, annotated cell/contact/lumen identities, and source/annotation hashes.

Every member also declares genotype_status and treatment_condition, bound to genotype_record_sha256 and treatment_record_sha256. Both baseline partitions require WILD_TYPE and BASELINE_UNPERTURBED declarations. The specimen-linked treatment record must state control/intervention identity, timing and applicable dose or boundary conditions. A treatment batch label does not supply that evidence. Holdout conditions require their separately frozen intervention mapping and scope review. Unresolved or unreviewed declarations never grant admission; structural schema validity and hash presence do not authenticate record contents.

Independent mechanical/transport measurement records bind specimens, methods, units, uncertainty, conditions, and material/interface classes. Optical data cannot invent nanoscale aperture, cohesive opening length, or absolute tension. Unknown physical quantities require measurements or defensible independent bounds plus sensitivity qualification.

Group split assignment by connected components sharing a dam, litter, harvest/fertilization event, or culture dish. Entire connected groups occupy one partition. Repeated litters from one dam stay grouped. Images, frames, cells, multiple crops, or technical repeats do not increase the biological replicate count. Relatedness via sire/pedigree is recorded and its effect on the claim assessed separately.

Collection/acquisition/treatment batch IDs and dam/litter IDs are explicit and cross-tabulated. Batch entropy is a diagnostic only. It does not establish unrelatedness, independent sampling, or effective sample size. Batch sharing across partitions prevents an unseen-batch claim for those records; it does not turn batch into a biological parent ID. An unseen-batch generalization claim requires separately frozen disjoint relevant batch membership.

Before admission, preregister dam/litter cluster counts, embryos per cluster, batch counts, crossed/nested analysis, exclusions, and a power/precision justification. No universal minimum count is invented here. If design sufficiency has not been reviewed, the cohort is PENDING_ADMISSION even when required fields exist. Cluster-aware analysis and uncertainty estimation must retain dam/litter dependence and account for batch effects; equal counts or high entropy cannot substitute for this review.

Baseline calibration and baseline validation precede hidden perturbation outcomes. Initial holdout data and ancillary coefficients may be supplied only through an explicitly frozen prediction-input contract. Dam-group separation is stricter than the parent's embryo-only minimum and is an explicit candidate refinement. Existing public/example data exposed during design are excluded from fresh blind-holdout claims. Finalized requirements are not finalized biological membership.

## Sources

1. Le Verge-Serandour and Turlier (2021), A hydro-osmotic coarsening theory of biological cavity formation. https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1009333
2. Dinet et al. (2023), Patterning and dynamics of membrane adhesion under hydraulic stress. https://doi.org/10.1038/s41467-023-43246-7 . Author-repository abstract: https://www.repository.cam.ac.uk/items/f62d21c9-98fc-4b1f-aca0-c1283e1494f9

All branch equations, numerical thresholds, scope limits, and cohort rules above are candidate design choices. Selection and content hashes establish a reviewable specification; calibration and enforcement require their own evidence.
