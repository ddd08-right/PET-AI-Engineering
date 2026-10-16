# PET/CT Segmentation Reliability: A Development Pilot and Research Roadmap

Can scores derived from fixed whole-body PET/CT segmentation outputs prioritize examinations with larger spatial errors for review? This repository presents an audited 20-case FDG development pilot and a staged research plan. Engineering feasibility is demonstrated in this setting; clinical benefit, independent validation, and cross-tracer transfer remain untested.

## Research question and evidence status

The project asks whether reference-free signals from a fixed segmentation can rank cases by their observed spatial error, and what those signals miss. The FDG20 pilot is **DEVELOPMENT / TRAINING_EXPOSURE_NOT_EXCLUDED**: it is not an independent test, an out-of-fold evaluation, or an estimate of population prevalence. The cohort was availability-sampled, with 10 reference-foreground and 10 empty-reference annotations; an empty annotation is not evidence of clinical negativity.

## Workflow

CT/SUVbw input and QC → fixed five-fold model path with TTA enabled → two
separate branches: official logits integration → fixed final mask → Predicted
MTV size baseline; and member probabilities/masks → entropy, fold variance, and
Pairwise disagreement. Scores order the same cases under a simulated review
budget; the reference enters evaluation and post-hoc error analysis only, never
prediction or reference-free scoring. Public workflow is described in text
because the revised SVG has not had independent render QA.

## FDG20 development pilot

The same official five-fold, TTA-enabled path and official logits integration produced each fixed final mask. Five folds are not five independent seeds. Member probability summaries support the reference-free scores; the reference enters evaluation only. The primary evaluated spatial risk is `R_spatial = FPV + FNV` in mL. It differs from absolute net MTV error, `E_MTV = |FPV − FNV|`, and from FNV alone.

| Score | Analysis status | Discrete AURC (mL) | Mean retained risk at 80% coverage (mL) |
|---|---|---:|---:|
| Entropy | Frozen primary analysis | 9.022248091583466 | 15.253468764473348 |
| Fold probability variance | Frozen primary analysis | 9.630056379120802 | 21.512857231313863 |
| Predicted MTV | Post-hoc size baseline; not UQ | 5.9740424771029508 | 10.098220871907802 |
| Pairwise disagreement | Post-hoc | 58.642476696090327 | 35.701841174531971 |

Lower AURC is better. The analytic random-order expectation was 28.626166246512675 mL; the reference-informed oracle was 5.7986986346595488 mL and is not deployable. Pairwise disagreement's result above the random expectation is retained. Predicted MTV's proximity to the oracle is a descriptive result for this development cohort, not evidence that a size baseline is generally optimal.

At a simulated 20% review budget (4 referred, 16 retained), the post-hoc share of cohort FNV assigned to the four referrals was 49.18% for entropy, 23.68% for variance, 65.52% for Predicted MTV, and 0% for Pairwise disagreement. This allocation is not observed clinical correction, lesion sensitivity, or reduced missed disease. Computational common-uncovered regions are candidate mechanisms only; without clinically validated reference completeness and matching, they are not complete lesion misses. No clinically major false-negative endpoint was assessed. See [methods and evidence boundaries](docs/FDG20_PILOT_METHODS.md) and the source-bound [aggregate figure](docs/figures/fdg20_pilot_aggregate.png).

## Engineering evidence

| Evidence | What is available | Boundary |
|---|---|---|
| Geometry, quantification, and binary segmentation | Public implementation with synthetic/analytic tests | Does not establish clinical registration or reference completeness |
| Risk–coverage and tie handling | Public utility and synthetic tests | Tests mathematics, not patient-level reliability |
| FDG20 fixed predictions | Aggregate results and methods summary | Protected patient inputs and predictions are not included; full calculations cannot be independently rerun here |
| Public aggregate figure | Source-bound historical PNG; aggregate-JSON-to-SVG renderer and schema checks | The PNG is the source-bound historical release figure. The current script reads public aggregate JSON and generates SVG only; it did not generate this PNG. The SVG has structural checks but no rendered visual QA and is not in the public whitelist. |

## Research roadmap

**Q1 — Does UQ add error-ordering value over a low-cost size baseline, and where are its blind spots?** Audit training and model-selection exposure, freeze a comparison (Entropy versus Predicted MTV is a proposal, not an approved primary endpoint), and evaluate fixed scores on independent FDG patients with an expert-reviewed reference. Separate spatial error, FNV, absolute net-volume error, and lesion-level errors.

**Q2 — After a blind spot is clinically confirmed, can complementary evidence improve review yield without unacceptable burden?** Only then propose separately approved cue-generation or auxiliary-model work, keeping the primary mask fixed. Measure false prompts, residual false-negative burden, candidate count, and actual reader time. No auxiliary method is assumed to help. PSMA and external-centre transfer are later, separate validation stages; no independent FDG cohort, lesion-level clinical adjudication, reader-time study, or transfer validation is complete.

The [research design candidate](docs/RESEARCH_DESIGN_CANDIDATE.md) remains **PROPOSED / NOT RUN**; SAP and clinical-reference SOP approval are pending.

## Reproduce the public artifacts

The aggregate JSON can generate an SVG summary, and the public test checks the JSON contract and renderer output:

```powershell
python scripts/render_fdg20_public_figure.py --input docs/fdg20_pilot_aggregate_summary.json --output .\fdg20_summary.svg
python -m pytest tests/test_fdg20_public_artifacts.py tests/test_risk_coverage.py
```

These commands exercise public aggregate display and synthetic ranking behavior only. They do not reproduce protected patient calculations. A complete run requires separately governed inputs, historical execution code and permitted model artifacts.

## Scope and provenance

The public repository contains no patient images, masks, member probabilities, case mapping, private orchestration, or model weights. Historical adaptation-code byte identity and checkpoint redistribution rights remain unresolved. Hashes support artifact traceability, not clinical validity. The earlier [five-case 40-epoch development case](docs/DEVELOPMENT_BASELINE_40E_CASE.md) remains a separate historical engineering record; it is not pooled with FDG20. See [architecture](docs/ARCHITECTURE.md), [programming evidence](docs/PROGRAMMING_EVIDENCE.md), [metrics](docs/METRICS.md), [data provenance](docs/DATA_PROVENANCE.md), and [third-party attribution](THIRD_PARTY.md).
