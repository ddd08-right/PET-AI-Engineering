# Candidate Research Design

**Status: `PROPOSED / NOT RUN`.** This is a planning note, not a preregistered
protocol, confirmed novelty claim, or completed reliability study. Current
patient evidence remains a post-hoc, development-exposed five-case result from
one seed/fold; no independent or external validation is available. The public
`PARTIAL_RECIPE` does not reproduce the protected run.

No expert-opinion attachment or paper PDF was present among readable inputs for
this update. Decisions below use the checked sources and repository methods;
they are not attributed to an unseen reviewer. Source checking was scoped, not a
comprehensive prior-art search.

## Question and source support

For a locked PET/CT segmentation pipeline, can a patient-level score rank
examinations with larger absolute whole-body mask-volume error toward review,
reducing error among examinations retained at fixed coverage? In the
repository's five-case development analysis, EMA-selected and final checkpoints
ranked differently on the same cases by Mean Dice and Volume MAE; this remains
a development observation, not independent evidence ([case report](DEVELOPMENT_BASELINE_40E_CASE.md)).
False-positive and false-negative volumes can also cancel in net-volume error.
“Mask volume” means generic physical mask volume here; it is not automatically
MTV, TLV, or a clinically validated burden measure.

Selective-prediction literature motivates risk-versus-coverage analysis, but its
classification results do not validate PET segmentation or this repository's
AURC [1]. PET segmentation studies assess reference agreement and test–retest
repeatability as different properties [5].

## Evidence status

**Completed:** synthetic risk–coverage utilities and tests, generic volume and
segmentation metrics, and the development-exposed case above. These do not
validate patient-level reliability.

**Proposed:** a locked, patient-isolated evaluation cohort, independently
generated ensemble predictions, a selective-review ranking analysis, and a
separate comparison of any complete pipelines on the same patients. Cohort,
model count, fold count, performance target, and compute budget are unknown.

## Candidate design and controls

Before analysis, freeze eligibility, the patient-versus-examination estimand,
reference-mask policy, physical units, preprocessing, model/checkpoint
selection, thresholds, post-processing, and failure handling. Verify patient
linkage across examinations, annotations, label and affine validity, PET
quantitative scaling, and data governance. The reference is an expert
segmentation, not pathology truth. A ground-truth-centred crop is unavailable at
unlabelled inference and is not an inference-time option.

Reserve evaluation patients before development. Every ensemble member
contributing to an evaluated patient's score must exclude that patient and all
their examinations from training, validation, checkpoint or threshold
selection, calibration, and preprocessing adaptation. Keep auditable patient
splits for every member. Out-of-fold predictions remain development evidence
when they guide choices; OOF does not itself mean unexposed test data. Use an
untouched patient-level holdout; external-site validation remains a later need.

Keep two analyses separate:

1. **Fixed-prediction scoring:** freeze predictions and references, then compare
   candidate risk rankings on identical cases and errors. Candidate signals
   include ensemble mask disagreement and predicted-volume variability;
   evaluate entropy only with genuine probability maps. Include reproducible
   random ranking and the repository's oracle/reversed controls. The oracle
   uses true errors and is a diagnostic bound, never a deployable score.
2. **Cross-pipeline comparison:** freeze complete systems and compare them on
   the same patients, reporting each system's segmentation/volume performance
   separately from its ability to rank its own errors. This changes the
   predictions and is not fixed-prediction scoring. Paired comparisons use the
   same resampled patient clusters for every system.

The candidate decision unit is an examination. If patients contribute multiple
examinations, set their weighting before analysis and resample the patient with
all examinations as one cluster. Do not treat examinations or ensemble members
as independent patients. Use paired patient-cluster bootstrap intervals for
population metrics only with adequate independent patients and a prespecified
interval method [3, 4]. Report patient and examination counts and interval
limitations; an unstable interval is inconclusive, not evidence of equivalence.
Bootstrap intervals do not resolve small-cluster limitations, development
exposure, or variation from retraining models; those require separate design
and evidence.

## Candidate endpoints

**Primary:** repository-convention discrete AURC for absolute mask-volume error
`|V_pred - V_ref|`, in mL. Prespecify coverage grid and tie policy. AURC has
the unit of its risk outcome: volume-error AURC is mL; Dice-error AURC is
dimensionless. Do not compare values across different outcomes, units, cohorts,
coverage grids, or conventions. The risk-score scale itself does not set AURC's
unit.

**Secondary:** retained-set risk at clinically selected review budgets; Mean
Dice on non-empty references; FPV and FNV separately in mL; absolute volume
error and relative error only when reference volume is positive; and, if
justified, method-agreement summaries. A low net-volume error alone does not
show useful foreground segmentation. Bland–Altman limits require a defined
measurement pair and acceptable limits set with domain input; agreement is not
correlation, segmentation accuracy, or repeatability [2]. Current aggregates
lack paired rows for such plots.

Interpret these quantities separately:

- **Predictive uncertainty:** a per-examination signal from model outputs.
  Ensemble disagreement is a candidate signal, not assumed to be pure
  epistemic uncertainty or a calibrated probability of error [6].
- **Statistical confidence interval:** uncertainty in a population estimate
  from patient sampling, not uncertainty for one scan.
- **Ranking stability:** ordering changes under a stated perturbation, such as
  patient resampling or ensemble-member variation; report separately from CIs.
- **Measurement repeatability:** variation across repeated acquisitions or
  independently repeated references under a defined protocol. An ensemble on
  one scan does not measure scan–rescan repeatability [5].
- **Simulated referral:** flags under a hypothetical review budget estimate a
  ranking trade-off. They are not actual clinician review, intervention, or
  evidence of clinical utility.

## Data, budget, and failure conditions

Unknown at this stage: eligible independent-patient count; sites, scanners,
tracers and reconstructions; annotation provenance/adjudication and repeat
measurements; patient linkage; consent and governance; model/inference access;
hardware and GPU-hours; and clinically acceptable error and review capacity.
Estimate sample size and compute only after these are established; none is
assumed here.

Do not make a primary validation claim if patient isolation or provenance fails,
units or references are ambiguous, predictions or references are missing
without prespecified handling, or evaluation choices used outcomes. Retain and
report failures and denominators; do not silently remove cases. Without genuine
probabilities, entropy is unavailable; without independent patients, results
remain development analysis; without repeat acquisitions or references,
repeatability is not assessed. No numerical success threshold is set before
clinical capacity and acceptable error are supplied.

## Decision summary

| Decision | Disposition |
| --- | --- |
| ADOPT | Patient-grouped isolation, same-patient pipeline comparisons, patient-cluster resampling. |
| MODIFY | Separate fixed-prediction ranking from pipeline performance; state AURC outcome, unit, coverage grid, and tie policy. |
| DEFER | Real-patient reliability, external validation, calibrated uncertainty, and repeatability until data, governance, and resources are confirmed. |
| REJECT | GT-centred cropping at unlabelled inference; treating outcome-informed OOF as unexposed; equating simulated flags with clinical review; using net-volume MAE alone as segmentation utility. |

## Candidate research questions

1. Does ensemble disagreement rank absolute whole-body mask-volume error better
   than random ranking on an untouched, patient-isolated cohort?
2. Do candidate rankings persist across sites or acquisition conditions?
3. How do scan–rescan and reference-reader variation compare with
   between-pipeline variation in generic mask volume and spatial overlap?

## Checked references

1. Geifman Y, El-Yaniv R. “Selective Classification for Deep Neural Networks.”
   *NeurIPS 30*, 2017, proceedings version. [DOI
   `10.48550/arXiv.1705.08500`](https://doi.org/10.48550/arXiv.1705.08500);
   [official proceedings](https://proceedings.neurips.cc/paper/7073-selective-classification-for-deep-neural-networks.pdf).
   Checked §§2, 5 and Figure 2. Supports classification risk–coverage
   framing, not PET validation or this AURC.
2. Bland JM, Altman DG. “Statistical methods for assessing agreement between
   two methods of clinical measurement.” *The Lancet* 327 (1986): 307–310.
   [DOI `10.1016/S0140-6736(86)90837-8`](https://doi.org/10.1016/S0140-6736(86)90837-8).
   Checked the authors' reproduction of the original text, Summary and
   Introduction. Supports method-agreement analysis distinct from correlation;
   no project limits are supplied.
3. Field CA, Welsh AH. “Bootstrapping clustered data.” *JRSS B* 69 (2007):
   369–390. [DOI `10.1111/j.1467-9868.2007.00593.x`](https://doi.org/10.1111/j.1467-9868.2007.00593.x).
   Checked publisher record and abstract. Supports cluster resampling as a
   design choice and notes model dependence; the paired patient procedure here
   remains proposed.
4. Efron B, Tibshirani RJ. “Bootstrap methods for standard errors, confidence
   intervals, and other measures of statistical accuracy.” *Statistical
   Science* 1 (1986): 54–75. [DOI
   `10.1214/ss/1177013815`](https://doi.org/10.1214/ss/1177013815). Checked
   Project Euclid record and abstract. Supports bootstrap use for statistical
   accuracy and confidence intervals, not a specific patient-cluster design.
5. Pfaehler E, et al. “Repeatability of two semi-automatic artificial
   intelligence approaches for tumor segmentation in PET.” *EJNMMI Research*
   11 (2021): 4. Version of record, 6 January 2021. [DOI
   `10.1186/s13550-020-00744-9`](https://doi.org/10.1186/s13550-020-00744-9).
   Checked Methods—test–retest evaluation, Figure 6, and Discussion. Supports
   repeatability analysis in its NSCLC setting, not generality to this cohort.
6. Kendall A, Gal Y. “What Uncertainties Do We Need in Bayesian Deep Learning
   for Computer Vision?” *NeurIPS 30*, 2017, proceedings version. [DOI
   `10.48550/arXiv.1703.04977`](https://doi.org/10.48550/arXiv.1703.04977);
   [official proceedings](https://papers.neurips.cc/paper/7141-what-uncertainties-do-we-need-in-bayesian-deep-learning-for-computer-vision.pdf).
   Checked §1, Figure 1, and §5.2. Supports the paper's aleatoric/epistemic
   distinction, not calibrated or clinically predictive disagreement here.

These publisher/proceedings records and accessible source texts were checked
for the claims above. No broader novelty review was performed.
