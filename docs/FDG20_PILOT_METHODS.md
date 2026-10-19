# FDG20 fixed-prediction development pilot

**Status: completed development-exposed engineering and analysis; not independent validation.** Aggregate development-pilot results and methods are publicly released. The study remains development-exposed and is not independent clinical validation. Release through [PR #6](https://github.com/ddd08-right/PET-AI-Engineering/pull/6) was merged on 2026-10-19 at 07:24:48 UTC ([merge commit](https://github.com/ddd08-right/PET-AI-Engineering/commit/45aaf382a55220d07d05e533d9a06b0bc1bd7eb4)). Public release does not approve the future SAP or clinical-reference SOP, establish clinical benefit or PSMA transfer, or grant model-weight redistribution rights.

## Research question and completed analysis

This availability-sampled pilot asked whether reference-free case scores order fixed-prediction spatial error under a common simulated review budget. The completed analysis used the official five-fold model path with TTA enabled and official mean-logits integration. Five fold members have overlapping training sets; patient training exposure was not excluded. The cohort has 20 cases: 10 reference-foreground annotations and 10 empty-reference annotations. This is not a prevalence sample; an empty annotation does not establish clinical negativity.

The frozen scores were full-evaluation-grid entropy of the mean member foreground probability and full-grid population variance (`ddof=0`) across member probabilities. Post-hoc scores were Predicted MTV from the same fixed official final mask (a size/burden baseline, not a UQ score) and Pairwise disagreement, defined as the mean `1 − Dice` over ten unordered pairs of five member masks. Pairwise member masks use the existing `p > 0.5` decision rule; a double-empty pair has Dice 1 and a single-empty pair Dice 0. Reference did not enter any score.

The evaluated risk is frozen spatial error `R = FPV + FNV` in mL. It is distinct from absolute net MTV error and from FNV alone. Lower discrete AURC is better. A 20% simulated review budget is 4 referred and 16 retained cases; it is not observed reader time, corrected error, or clinical benefit. Panel B reports the post-hoc fraction of total cohort FNV assigned to the four referrals.

| Score | Status | Discrete AURC (mL) | Mean retained R at 80% coverage (mL) | FNV share in 4 referrals |
|---|---|---:|---:|---:|
| Entropy | Frozen analysis | 9.022248091583466 | 15.253468764473347 | 49.1799021941403% |
| Fold probability variance | Frozen analysis | 9.630056379120802 | 21.512857231313866 | 23.6811355866188% |
| Predicted MTV | Post-hoc size baseline; not UQ | 5.974042477102951 | 10.098220871907802 | 65.5169429177306% |
| Pairwise disagreement | Post-hoc | 58.64247669609033 | 35.70184117453197 | 0% |

The analytic random-order expected AURC is 28.626166246512675 mL. The reference-informed oracle AURC is 5.798698634659549 mL and is not deployable. Pairwise disagreement ranked this development cohort worse than the analytic random expectation; this negative result is retained. Predicted MTV was descriptively near the oracle on this cohort, but is a simple volume-size baseline rather than an uncertainty measure. No causal explanation or transportable advantage follows from these observations. Referral FNV share is only an error-allocation summary, not observed clinical correction.

The analytic random reference is the expected AURC under a uniformly random case order, equal to cohort mean R. The oracle sorts by observed reference-derived risk and is reference-informed. Neither changes the patient selection or evaluation set.

## Metric-level analysis provenance

Entropy and fold variance AURC and retained risk at 80% coverage are `FROZEN_ANALYSIS` under the existing frozen contract. Predicted MTV and Pairwise comparisons are `POST_HOC`. The FNV share in four referrals is `POST_HOC` for **all four methods**, including Entropy and fold variance. JSON row-level `analysis_status` is retained for compatibility and describes AURC/retained risk only; `metric_analysis_status` labels each metric explicitly. This is development evidence, not confirmatory clinical research.

## Figure provenance and display

The [released PNG](figures/fdg20_pilot_aggregate.png) is the source-bound historical figure. Its same-content historical visual QA is reused; no image was redrawn for this revision. The current renderer reads public aggregate JSON and generates SVG only; it did not generate the historical PNG and does not byte-reproduce it. SVG structural checks are not rendered visual QA; an unreviewed SVG is not added to the released figure set. A browser viewport check for this revision is NOT_OBSERVED. README display values use decimal round-half-up (AURC/risk: two decimals; FNV percentage: one decimal); JSON retains original numeric precision.

## Limits and next evidence gates

This is not OOF, an untouched test set, clinical utility, an estimate of lesion sensitivity, or PSMA/external-centre validation. Five folds are not independent seeds. Full-grid scores can be affected by background and field-of-view. Input QC is not blinded evaluation of prediction quality, and error volume is not clinical severity. Reference completeness, lesion matching, and clinically major-FN definitions have not been clinically validated. Historical adaptation-code byte identity remains incomplete; model/checkpoint redistribution rights are not established.

Computational common-uncovered regions are post-hoc candidate mechanisms only.
Without clinically validated reference completeness and lesion matching, they
are not complete lesion misses. No clinically major false-negative endpoint
was assessed.

Future work is proposed, not run: (1) audit patient/examination exposure and model selection; (2) obtain PI/statistician approval and validate fixed scores on independent FDG data; (3) resolve complete lesion references and clinical safety definitions; (4) only if a blind spot is clinically confirmed, seek separate approval for complementary evidence while keeping the primary mask fixed and measuring false prompts, remaining FN, and actual reader time; (5) treat PSMA and external-centre transfer as separately designed studies. Sample size, centre count, budget, thresholds, and major-FN definition remain TBD. The SAP and clinical-reference SOP remain approval candidates.

Full discrete curves, per-case ranks, identifiers, images, masks, probabilities, private paths, and weights are excluded. The released scope is aggregate results, methods, code and figures; patient-level artifacts and model weights remain excluded. Future data access and expanded disclosure require their own permissions.
