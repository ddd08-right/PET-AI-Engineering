# A Traceable 40-Epoch Development Baseline Case

**Evidence status: `DEVELOPMENT_EXPOSED`.** This is a single-seed, fold-0 development-set case study over five validation cases. It is not an independent test, an official AutoPET benchmark reproduction, an algorithmic innovation claim, or clinical validation.

## Research question

This question was formulated for the post-hoc case analysis; it was not a
preregistered hypothesis: can checkpoint ranking differ when evaluation
emphasizes segmentation overlap versus net volume error? We compare the final
checkpoint with the checkpoint selected during training by the upstream nnU-Net
online validation exponential-moving-average (EMA) pseudo Dice rule. Here,
“best” means best by that one online rule; it does not mean best for every
reported endpoint.

## Scope and method

The run used CT and PET inputs, seed `20260924`, fold `0`, nnU-Net `3d_fullres`, a 40-epoch PolyLR horizon, patch size `[160, 112, 96]`, batch size `2`, a verified midpoint-sampling loader, and single-process data augmentation (`nnUNet_n_proc_DA=0`). cuDNN deterministic mode was enabled and benchmark mode disabled. The loss remained the upstream nnU-Net loss inherited by the trainer.

The initial background process was interrupted after epoch index 21. Recovery was fail-closed from a checkpoint with `current_epoch=22`: the checkpoint hash, optimizer state, AMP scaler, logger history, network tensors, learning rate, trainer, fold, and configuration were checked before continuation. Historical random-number-generator state was not saved, so the resumed trajectory is not claimed to be bitwise equivalent to an uninterrupted run.

The final checkpoint has `current_epoch=40` and 40 logged epochs, corresponding to completed epoch indices 0–39. The EMA-selected checkpoint has `current_epoch=36` and 36 logged epochs, corresponding to completed epoch indices 0–35. This avoids the common one-epoch numbering error caused by the checkpoint field storing the next epoch counter.

The recorded `7345.4399993` seconds is only the independent PowerShell recovery-wrapper segment, from the epoch-22 resume through training completion and automatic final validation. It is not the cumulative GPU training time for all 40 epochs. Unrecoverable timing intervals are `UNKNOWN`. The recovery wrapper and the separate five-case EMA-selected-checkpoint evaluation both exited with code `0`.

## Aggregate results

![Horizontal comparison of final, EMA-selected, and analytic empty-prediction control on non-empty-reference Dice (n=3) and mean absolute volume error (n=5, mL). The analytic control is not model inference; aggregates cannot independently reproduce protected per-case metrics.](figures/development_metric_tradeoff.svg)

*Figure. Checkpoint ranking depends on the evaluation endpoint. Development-exposed, single seed/fold; lower net-volume error alone does not establish usable foreground segmentation. [PNG preview](figures/development_metric_tradeoff.png).*

All volume quantities are unweighted means in mL. `n` is the number of applicable cases out of five.

| Source | Strict Dice | FPV | FNV | Absolute volume error | Precision | Recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Final (`current_epoch=40`) | 0.09907 (n=3) | 48.07 mL (n=5) | 29.95 mL (n=5) | 59.43 mL (n=5) | 0.1036 (n=5) | 0.3256 (n=3) |
| EMA-selected (`current_epoch=36`) | 0.2187 (n=3) | 65.64 mL (n=5) | 23.88 mL (n=5) | 63.21 mL (n=5) | 0.1537 (n=5) | 0.4568 (n=3) |
| `ANALYTIC_EMPTY_PREDICTION_CONTROL` | 0.000 (n=3) | 0.000 mL (n=5) | 33.30 mL (n=5) | 33.30 mL (n=5) | undefined (n=0) | 0.000 (n=3) |

The standard Dice formula is 0 for empty reference/non-empty prediction and is
0/0 only when both masks are empty. The project's strict policy nevertheless
excludes every empty-reference case from Dice, recall, and relative-volume-error
aggregation. Dice and recall therefore average the three non-empty-reference
cases. The frozen `NaN`/`null` values and `UNDEFINED_EMPTY_GT` status are retained
as a historical project-policy API label, not a universal mathematical claim.
FPV, FNV, prediction/reference volume, and absolute volume error retain all five
cases. Precision is defined for all five real-model predictions because every
prediction was non-empty; it is undefined for the analytic all-empty control.

The automatic nnU-Net final-validation Dice was `0.05944427730135972`. It averages all five cases for foreground class 1: an empty-reference case with a non-empty prediction contributes Dice `0`, while only a both-empty pair becomes `NaN` and is omitted by `nanmean`. This five-case value is shown separately and is not mixed with the strict three-case Dice mean.

`ANALYTIC_EMPTY_PREDICTION_CONTROL` is an analytic calculation from reference-mask volumes, not a trained network and not an inference result. No fake prediction files were created. Its lower mean absolute volume error does not make it clinically useful: it misses all foreground in the three non-empty-reference cases. The result demonstrates why net volume error alone cannot establish segmentation value.

## Why the rankings conflict

Relative to final, the EMA-selected checkpoint had higher strict Dice, precision, and recall and lower FNV, but higher FPV and higher mean absolute volume error. This is a false-negative/false-positive trade-off, not evidence that one checkpoint is universally superior.

For binary masks, `|FPV - FNV|` is the absolute net volume error: false-positive and false-negative volumes can cancel. By contrast, exploratory `FPV + FNV` is the symmetric-difference error volume and does not permit that cancellation. It is useful for diagnosis but does not replace the locked primary endpoints. All five cases were retained; no influential case was removed after results were known.

## Foundations, repository work, observations, and open hypotheses

- **Upstream foundation:** nnU-Net supplies the training/inference framework, checkpointing behavior, online EMA pseudo-Dice selection, and baseline loss. The public dataset supplies the imaging and reference labels. These are not original contributions of this repository.
- **Engineering completed here:** a fixed single-seed/fold run scope; isolated output; fail-closed checkpoint recovery; budget-aware epoch-boundary stopping; checkpoint/source hashing; explicit wrapper exit records; final and EMA-selected five-case evaluation; strict empty-reference handling; and a public-safe aggregate audit.
- **Observations supported by this run:** overlap-based and net-volume-error rankings differed; the EMA-selected checkpoint reduced missed volume while increasing false-positive volume; and an analytic empty predictor obtained a lower net-volume MAE while being unusable for foreground detection.
- **Not yet verified:** generalization, clinical utility, reliability/calibration, causal effects of training duration, and whether the observed trade-off persists across seeds, folds, or external cohorts.

## Limitations and current conclusion

The sample contains only five development validation cases from one fold and one seed. The validation results were inspected repeatedly during engineering, so this is development-exposed evidence. Training was interrupted and resumed without complete historical RNG state. There is no independent external validation, and no reliability study has been completed. Differences from a historical 20-epoch run cannot be attributed to epoch count alone because seed, learning-rate trajectory, augmentation process, determinism settings, launcher, and checkpoint-selection policy also differed.

The experiment is traceable and useful as an engineering failure-analysis case, but model performance is insufficient for clinical conclusions or use.

One possible follow-up is a **result-aware exploratory case analysis whose method must be locked before further analysis**. It would examine the spatial source of false-positive volume in an influential retained case. This is not preregistered, was not part of the original study, and was not executed here.

## Provenance and public boundary

The companion aggregate file is [`development_baseline_40e_summary.json`](development_baseline_40e_summary.json). It contains only configuration, aggregate metrics, applicability counts, source digests, checkpoint counters/digests, and run-segment records. Patient images, case mappings, per-case rows, private paths, weights, credentials, and sensitive logs are excluded.

One source conflict is preserved: the original preparation-time configuration still says `PREPARATION_ONLY_NOT_RUN`. That stale field is not completion evidence. Completion is supported instead by the frozen result files, checkpoint metadata/logging counts, validation summary, and wrapper exit records listed by digest in the companion file.

The internal HTML report remains private and had only `structural_only` packaging verification because no Chromium renderer was available. No visual-QA-passed claim is made here.
