# Adaptive Risk Gate V19 - stable, Holm-corrected, guarantee-calibrated evaluation

5,994 patients evaluated out of sample (cached embeddings only). Wording below is generated from the numbers.

| claim | evidence | supported |
|---|---|---|
| Finite-sample guarantee holds out of sample (cross-fit, primary scenario) | 72/72 gate configurations kept realised risk <= alpha | yes |
| Guarantee confirmed on untouched fresh patients | 8/8 full-gate targets met (2,000 patients) | yes |
| RQ1: full 5-signal gate needs less workload than the binary baseline at equal guaranteed risk | Holm-adjusted verdicts across 8 targets: {'inconclusive': 8} | no |
| RQ1 component: D adds to U | Holm-adjusted verdicts: {'inconclusive': 8} | no |
| RQ1 component: M adds to U+D | Holm-adjusted verdicts: {'inconclusive': 7, 'better': 1} | no |
| RQ1 component: S adds to U+D+M | Holm-adjusted verdicts: {'inconclusive': 7, 'worse': 1} | no |
| RQ2: ASK-CONTEXT lowers cost at the primary budget | delta cost -0.00009 [-0.00025, +0.00008] | no |
| RQ2: ASK-LATERAL lowers cost at the primary budget | delta cost -0.00000 [-0.00001, -0.00000] | yes |
| RQ2: both Ask actions lowers cost at the primary budget | delta cost -0.00009 [-0.00025, +0.00007] | no |
| RQ2: ASK-CONTEXT lowers workload at equal guaranteed risk | Holm-adjusted verdicts: {'inconclusive': 6, 'worse': 1, 'better': 1} | no |
| Cost-aware Ask beats cost-unaware "ask whenever context is missing" at the same workload | binary_UDMS: -0.00383 [-0.00481,-0.00288]; ask_both_UDMS: -0.00393 [-0.00486,-0.00300] | yes |
| ASK-CONTEXT pays off somewhere in the assumed cost grid | 15/30 cells | yes |
| ASK-LATERAL pays off somewhere in the assumed cost grid | 2/6 cells | yes |
| ASK-CONTEXT result holds in every deployment scheme (incl. the held-out structured-masking scheme) | natural: inconclusive; mcar30: inconclusive; mcar60: inconclusive; struct40: better | no |
| ASK-CONTEXT confirmed on untouched fresh patients | delta cost -0.00000 [-0.00020, +0.00021]; ask rate 1.5% | no |
| PRIMARY ENDPOINT (pooled cross-fit): Full gate vs binary baseline at fn target 0.03 | referral -0.0028 [-0.0075, +0.0018], Holm p=1.000; = 2.8 fewer escalations per 1,000 patients | no |
| PRIMARY ENDPOINT on untouched fresh patients | referral -0.0014 [-0.0058, +0.0028], Holm p=1.000 | no |
| Full gate vs a learning-to-defer surrogate-loss baseline (Madras/Mozannar-Sontag style) | Holm-adjusted verdicts: {'better': 7, 'inconclusive': 1} | yes |
| Stable across 3 independent fold assignments | full-vs-binary referral change at the primary target: mean -0.0001, sd 0.0028; same sign in all seeds: False | no |
| Guarantee survives a change of labeler (NegBio) | 16/16 met after recalibration; 16/16 met if the gate keeps its CheXpert calibration | yes |
| Asking for the missing context FIRST, then gating, lowers workload at equal guaranteed risk | verdicts: {'worse': 8}; break-even cost of one context request = 0.000 of a full review (median over targets) | no |
| EXTERNAL dataset (NIH ChestX-ray14, 6,000 patients, 8 shared labels): guarantee holds | 6/6 full-gate targets met with MIMIC calibration unchanged; 6/6 after recalibrating only the threshold; image-only macro AUROC 0.751 | yes |
| EXTERNAL dataset: full gate needs fewer escalations than the uncertainty-only gate | Holm-adjusted verdicts: {'worse': 3, 'better': 2, 'inconclusive': 1} | no |
| Per-critical-finding risk guarantees (Edema, Consolidation, Pneumonia, Pneumothorax) hold simultaneously | 4/4 union-gate and 4/4 shared-threshold configurations met all four targets; realised risk was on average 28% of the target (conservative); escalation 33%-60% | yes |
| A single shared threshold meets all per-finding targets with fewer escalations than a union of per-finding gates | target 0.75: union minus shared +0.076 [+0.068, +0.084]; target 0.5: union minus shared +0.068 [+0.060, +0.075] | yes |
| Per-finding guarantees: full signal set needs fewer escalations than uncertainty alone | Holm-adjusted verdicts: {'inconclusive': 3, 'worse': 1} | no |
| Ensemble-disagreement signal E: All signals incl. E vs U | Holm-adjusted verdicts: {'inconclusive': 8} | no |
| Ensemble-disagreement signal E: E adds to U | Holm-adjusted verdicts: {'inconclusive': 7, 'better': 1} | no |
| Ensemble-disagreement signal E: E adds to U+D+M+S | Holm-adjusted verdicts: {'inconclusive': 8} | no |
| Second labeler (NegBio) agrees closely with CheXpert on the evaluation patients | macro Cohen kappa 0.983 on 5,994 patients (both rule-based labelers: NOT an independent reference standard) | yes |
| EXTERNAL subgroup audit (NIH sex and age): risk targets hold in every subgroup | point estimate within target in 60/60 subgroup configurations; upper 95% bound within target in 45/60; 2/12 subgroup risk gaps had an interval excluding zero | yes |
| RQ3 (simulation only): workload-aware thresholds reduce harm at equal volume | 9/18 simulated settings | no |
| Signal 2 stress test: mismatched clinical context is detectable | detection AUROC 0.628 (0.5 = chance) | yes |
| Signal 3 under withheld context: gate predicts when asking helps (held-out structured scheme) | corr(predicted gain, true gain) = 0.188 | no |
| Signal 1: conformal sets reach nominal coverage | 0 labels with upper CI below nominal | yes |

## Standing limitations
- Retrospective, single-source (MIMIC-CXR); labels are report-derived (CheXpert). No clinician outcomes.
- ASK-CONTEXT is evaluated in a SIMULATED deployment in which the clinical history/indication is withheld at triage for some patients; the information it returns is the real cached context embedding.
- Expert accuracy, request cost/failure and queue/override behaviour are assumptions (sensitivity grids provided), not measurements.
- Whole-context absence is tested; partial section masking would need re-embedding of modified reports.
- Fresh-cohort confirmation has no lateral view (ASK-LATERAL untested there).
- The primary endpoint was declared after the V15 results were seen; confirmation needs new data (external dataset or new patients).
- NegBio and CheXpert are both rule-based labelers with near-identical output (kappa about 0.98), so the label-source check is weak evidence of robustness; an independent reference (CheXbert or radiologist labels) was not available.
- Subgroup (sex, age) audit on NIH is underpowered for rare findings; the MIMIC subgroup audit needs MIMIC-IV demographics and runs only if they are provided.
- Per-critical-finding guarantees are conservative (few miss events per calibration fold); the ensemble signal was evaluated on one fold assignment only.
- External validation covers 8 labels shared with NIH ChestX-ray14, image only (no clinical context, no lateral view); NIH labels differ in definition and are sparse.
- Head regularisation strengths were explored on tuning patients of the pooled development data; only the fresh cohort is untouched by any design choice.