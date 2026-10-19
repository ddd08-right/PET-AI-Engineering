
# Metrics

## Voxel-level metrics

`pet_ai.evaluation.segmentation` reports:

- TP: predicted foreground voxels that overlap ground truth foreground.
- FP: predicted foreground voxels outside ground truth.
- FN: ground truth foreground voxels missed by prediction.
- Dice: `2 * TP / (2 * TP + FP + FN)` when ground truth is non-empty.
- FPV_mL: false-positive voxels multiplied by voxel volume.
- FNV_mL: false-negative voxels multiplied by voxel volume.

The standard formula gives Dice 0 when the reference is empty and prediction is
non-empty; only the both-empty case has a 0/0 denominator. For compatibility,
this project excludes every empty-reference case from its strict Dice aggregate
and represents it internally as `NaN`; JSON-style output converts that to
`null` with the historical status `UNDEFINED_EMPTY_GT`. Read this as
“not applicable under the project aggregation policy,” not a universal claim
of mathematical undefinedness. Use FPV_mL to evaluate negative cases.

Array entry points require same-shaped, finite, strictly binary 3D arrays; they
cannot establish physical alignment. NIfTI evaluation additionally requires a
recognized spatial unit and the same validated physical grid. Units are
converted to millimetres, comparisons use absolute tolerances with `rtol=0`,
and voxel volume is `abs(det(affine[:3, :3]))`. Inputs are not resampled,
thresholded, or repaired. A same-grid result does not prove anatomical
registration. Different native PET/CT grids are not automatically corrupt, but
cannot be fused by matching array indices without justified alignment.

## Lesion-level metrics

`pet_ai.evaluation.lesion_metrics` identifies connected components in 3D binary masks using configurable 6, 18, or 26 connectivity. It reports GT lesion count, prediction lesion count, true-positive lesions, false-positive lesions, false-negative lesions, lesion sensitivity, lesion volumes in mL, and small-lesion failures.

The legacy matching policy is deterministic greedy one-to-one overlap matching.
Candidate pairs require at least one overlapping voxel and are sorted by
descending overlap, then ascending IDs. This is a detection rule, not contour
accuracy and not a claim of equivalence to an AutoPET official implementation.
The overlap matrix `[[9, 8], [8, 0]]` is a counterexample: greedy returns one
match although a two-match assignment exists. Maximum-cardinality matching is
not implemented. Split/merge ambiguity remains explicitly reported.

## FDG20 fixed-prediction development analysis

The FDG20 pilot uses a different, protected fixed-prediction pipeline and
should not be conflated with the generic public functions above. The official
five-fold, TTA-enabled path and official logits integration form the final
binary mask. Member foreground-probability maps are used for reference-free
scores; the reference does not enter prediction or scoring.

- `R_spatial = FPV + FNV` (mL) is total spatial error volume. It is not the
  absolute net MTV error.
- `E_MTV = |FPV - FNV|` (mL) is the absolute net-volume difference on a common
  binary physical grid. When the same mask, reference, and voxel volume are
  used, it is algebraically equal to `abs(FPV - FNV)`.
- FNV alone is the false-negative volume. It is not a lesion count, a complete
  lesion-miss rate, or a clinical-severity measure.
- Frozen entropy is calculated from the mean foreground probability and
  aggregated over the full PET evaluation grid. Fold probability variance uses
  the frozen population-variance implementation. Pairwise disagreement and
  Predicted MTV are post-hoc comparisons; Predicted MTV is a size baseline, not
  an uncertainty measure.

Reported risk–coverage and AURC values are descriptive for a 20-case
availability-sampled development cohort (10 reference-foreground and 10
empty-reference annotations); training exposure was not excluded. Full-grid
averages may be affected by background and field of view. A simulated referral
share does not measure correction, clinical utility, or reader time. See
[`FDG20_PILOT_METHODS.md`](FDG20_PILOT_METHODS.md) for the aggregate values,
method status, and limits. No independent validation or lesion-level clinical
adjudication is established by these quantities.
