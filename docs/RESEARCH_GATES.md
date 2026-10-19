# Auditable research gates

**All studies: PROPOSED / NOT RUN.** This roadmap adds no approval, preregistration, data-access permission or completed experiment. It operationalizes the retained [design candidate](RESEARCH_DESIGN_CANDIDATE.md). SAP approval by the PI/statistician and nuclear-medicine reference-SOP approval are `PENDING`.

## Study 1 — Independent FDG reliability validation

Question: does UQ improve fixed-prediction error ordering beyond Predicted MTV, a size baseline rather than UQ?

| Gate | Required auditable artifact before progression | Current status |
|---|---|---|
| G1: Data rights and exposure | Access/use permissions, provenance and versioned patient/examination audit covering every contributing fold's training, validation, selection, calibration and preprocessing exposure; repeated examinations grouped by patient | `PENDING`; unknown exposure is not independence |
| G2: SAP and metric freeze | Approved primary comparison and paired ΔAURC estimand/sign; Entropy versus MTV remains a candidate. Freeze five-fold/TTA identity, official final masks, score/grid definitions, tie handling, invalid/failure handling, eligible denominator, review-budget integer rule, multiplicity and analysis code before independent outcome access | `PENDING`; no retrospective preregistration of FDG20 |
| G3: Independent patients | Versioned eligible cohort and non-exposure evidence for all members; independent sample size and precision justification | `NOT RUN`; no independent cohort available; search paused; size/centres/effect `TBD` |
| G4: Reference and lesion SOP | Expert-approved reference completeness, geometry, lesion inclusion/matching, split/merge handling, blinded review and adjudication; clinically major-FN definition and threshold | `PENDING`; clinical definitions `TBD` |
| G5: Paired evaluation | Same patients/predictions for all scores; prespecified patient-level paired confidence intervals (cluster repeated scans), interval level/interpretation and bootstrap details; ΔAURC, retained spatial risk, FNV, absolute net MTV error, failures and error analysis reported separately | `PROPOSED / NOT RUN`; intervals and effect targets `TBD` |

Use `FPV + FNV` for spatial error and `|FPV − FNV|` for absolute net-volume error. Report lesion-level errors only under an approved complete reference/matching protocol. A bootstrap cannot repair leakage. Null or adverse comparisons remain reportable; no superiority is assumed.

## Study 2 — Clinical missed-lesion and failure analysis

| Gate | Required auditable artifact before progression | Current status |
|---|---|---|
| G6: Confirm blind spots | Independent evidence plus nuclear-medicine adjudication separating voxel-level FNV, complete reference-lesion misses and clinically major misses; record uncertainty and reference incompleteness | `PROPOSED / NOT RUN`; computational common-uncovered regions are candidates only |
| G7: Conditional complementary evidence | Only after G6, separately approved comparison of low-cost cues; consider a supplemental model only if simpler evidence is inadequate and an incremental question remains. Preserve the primary mask initially; freeze prompts and report false prompts, candidate counts, residual FNV/lesion misses and compute cost | `PROPOSED / NOT RUN`; no presumed benefit |
| G8: Actual review cost | Separately approved reader protocol, measured interaction time, review yield, false-prompt burden and clinically acceptable residual error; reader recruitment/design and thresholds specified before execution | `PROPOSED / NOT RUN`; readers, cost, effect and thresholds `TBD` |

The FDG20 simulated case budget measures allocation, not physician time or corrected disease. Positive, null and increased-burden outcomes must all remain possible. G8 is a later reader study; it is not completed by retrospective scoring or a faster model.

## Study 3 — PSMA / cross-centre generalization

| Gate | Required auditable artifact before progression | Current status |
|---|---|---|
| G9: Transfer governance and design | Separate rights/exposure audit, versioned tracer/ligand, centre, equipment, reconstruction and patient-spectrum metadata; approved reference and paired validation protocol | `PROPOSED / NOT RUN`; patients/centres/sample size `TBD`; approval `PENDING` |
| G10: Independent transfer and review benefit | Evaluate fixed direct transfer separately from recalibration; prespecify site/tracer analyses, uncertainty and failure reporting. Measure actual review benefit under a separately approved reader protocol | `PROPOSED / NOT RUN`; no PSMA or external-centre result |

The next minimum research gate is **G1**, followed by SAP/reference approval and independent cohort availability; new patient inference or auxiliary-model training is not authorized by this document. Public [FDG20](FDG20_PILOT_METHODS.md) and [five-case](DEVELOPMENT_BASELINE_40E_CASE.md) aggregates remain development evidence throughout.
