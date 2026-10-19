# FDG20-informed research design candidate

**Status: `PROPOSED / NOT RUN`.** This version replaces the previous public
candidate's generic net-volume-error framing as the current roadmap. The
previous candidate is retained as
[`RESEARCH_DESIGN_CANDIDATE_PRE_FDG20.md`](RESEARCH_DESIGN_CANDIDATE_PRE_FDG20.md)
for history. This document is neither a preregistration nor an approved SAP,
clinical-reference SOP, or authorization to access data.

## Evidence that motivates the questions

FDG20 is a 20-case, availability-sampled development pilot with 10
reference-foreground and 10 empty-reference annotations. Training exposure was
not excluded. Entropy and fold-probability variance are frozen analyses;
Predicted MTV and Pairwise disagreement are post-hoc comparisons. Pairwise
disagreement's AURC above the analytic random expectation is retained as an
adverse observation. Predicted MTV is a simple fixed-mask size baseline, not a
UQ method. None of these results establishes independent validation, clinical
benefit, lesion sensitivity, or transportability.

## Q1 — Does UQ add value over a low-cost size baseline, and where are its blind spots?

First audit patient and examination overlap, repeated scans, training and
model-selection exposure, checkpoint and threshold selection, provenance,
permissions, and reference versions. Missing exposure evidence remains
`UNKNOWN`, not proof of independence. The independent FDG data search is
currently paused; no independent cohort is available for this plan.

Entropy versus Predicted MTV is a **future primary-comparison candidate**, not
an approved choice. The comparison must be approved by the PI and statistician
before independent outcomes are accessed. Pairwise disagreement, fold
variance, and other inexpensive baselines remain prespecified secondary
comparators only after the SAP defines multiplicity and failure handling.

Freeze the five-fold/TTA and official-logits prediction identity, final mask,
reference-blind scoring code, scoring grid, tie handling, invalid-case policy,
and review budget before testing. Use the same final predictions and eligible
patients for all scores. Report these separately: spatial error
`R_spatial = FPV + FNV`; FNV volume; absolute net-volume error
`E_MTV = |FPV − FNV|`; and lesion-level errors only when a clinically approved,
complete reference and matching protocol exist. Whole-grid scores may depend
on background and field of view; do not tune an ROI or denominator after
looking at results.

For an independent evaluation, confirm patient-level non-exposure for every
member contributing to that patient's score, including training, validation,
checkpoint/threshold choice, calibration, and preprocessing adaptation.
Repeated examinations are clustered by patient. Prespecify the primary
estimand, discrete AURC convention, review-budget integer rule, paired
patient-level bootstrap method and interval interpretation, confidence level,
and any multiplicity adjustment. Sample size and precision targets are
`TBD` until independent cohort structure, event rates, and clinically important
differences are known. A bootstrap does not repair training leakage.

## Q2 — After clinical confirmation, can complementary evidence improve review yield without unacceptable burden?

This question is conditional, not an instruction to build a model. Start only
if an independent evaluation identifies a reproducible blind spot and nuclear
medicine experts confirm the relevant reference is sufficiently complete.
Agree lesion inclusion, completeness status, geometry, matching and
split/merge rules, blind review, and adjudication before counting lesion
misses. Keep voxel FNV, a complete reference-lesion miss, and a clinically
major false negative as different outcomes. A major-FN definition and
threshold remain `TBD` pending expert approval.

If later approved, compare a low-cost candidate cue first, then consider an
ordinary second model only if the simpler evidence is inadequate and an
incremental question remains. A high-recall auxiliary model is a separate
proposal, not a presumed improvement. Keep the official primary mask fixed in
the initial prompt study. Count candidate prompts, false prompts, residual
FNV and adjudicated lesion misses, review workload, and compute cost. Measure
reader time from actual reader interactions; do not infer it from model runtime
or a simulated fixed case budget. Allow positive, null/no-incremental-benefit,
and increased-burden outcomes.

## Staged external validation

1. **Independence audit:** resolve patient exposure, repeated examinations,
   checkpoint/model selection, governance and release permissions.
2. **Fixed-score validation:** freeze scores and comparisons on independent
   FDG predictions and a complete, versioned reference before outcome access.
3. **Clinical blind-spot adjudication:** only after an approved lesion-reference
   protocol exists; distinguish computational candidates from confirmed
   lesion-level errors.
4. **Conditional complementary-evidence study:** obtain new approval, preserve
   the primary mask, and measure both review yield and added burden.
5. **Reader and transfer studies:** measure actual reader interaction time;
   separately record PSMA ligand, centre, disease spectrum, acquisition and
   reconstruction. Direct transfer and recalibration are distinct questions.

Independent patient count, centre count, major-FN rate, budget, and clinically
acceptable thresholds are all `TBD`. No independent FDG analysis, lesion-level
clinical adjudication, auxiliary-model intervention, reader-time study, PSMA
or external-centre validation has been performed under this plan.

## Governance and interpretation

The current FDG20 results are post-hoc development evidence and are not
retrospectively preregistered by this revision. The SAP requires PI and
statistician approval; the reference SOP requires nuclear-medicine review.
Data/IP release permission and model-weight redistribution rights are separate
from scientific protocol approval. See the [FDG20 methods and evidence limits](FDG20_PILOT_METHODS.md)
and the retained [pre-FDG20 candidate](RESEARCH_DESIGN_CANDIDATE_PRE_FDG20.md).
