# Synthetic fixed-mask selective review

**SYNTHETIC MATHEMATICAL DEMONSTRATIONS / NO CLINICAL CLAIM.**
All cases, references, final masks and five member probability arrays are
constructed in memory: not patients, trained folds/seeds, real inference,
nnU-Net/LesionTracer checkpoints, or a reproduction of FDG20.

From an installed checkout:

```powershell
python scripts/demo_fixed_mask_selective_review.py
```

The existing quantitative demo uses mean-member-volume error and a composite
score. This separate example uses a directly fixed final mask, four separate
rankings and spatial risk; historical calculations remain unchanged.

## Computation contract

Prediction inputs are separate from references. Scores use the entire common
4×4×4 grid without a reference ROI. Higher means candidate higher risk:
binary entropy of mean member probability (natural log, existing entropy log
clipping); mean population probability variance (`ddof=0`); Predicted MTV of
the **fixed final mask**, a size baseline, not UQ; and `1 - mean(pairwise Dice)`
of member masks (`p > 0.5`). Double-empty pairs have Dice 1, single-empty pairs
Dice 0. No extra epsilon or exclusions are introduced. The final mask is not
claimed to result from official mean-logits integration. Voxel volume is 8 mm³:
volume in mL equals voxel count × 8 / 1000.

Only evaluation uses references via existing binary segmentation evaluation:
`R_spatial = FPV + FNV`, `E_MTV = |FPV - FNV|`, all mL. Predicted MTV is never
reference MTV. All four methods use identical cases, final predictions, risk
values and coverage `k/n`, k=1…n. Existing expected-within-tie permutations
make Risk–Coverage independent of input order. High-first score tie groups are
printed without inventing a unique ordering. AURC is mean retained risk on
that grid, a right-endpoint discrete integral; lower is better. The 50% simulated
review budget retains two of four artificial cases. At a boundary tie, risk is
an expectation, not proof that tied cases can be distinguished.

The oracle ranks by reference-derived risk and is not deployable. Uniform-random
ordering has expected retained risk and AURC equal to full-cohort mean risk.
All scores, errors, AURCs, retained risks and rankings are computed at runtime;
no FDG20 numbers are copied. Review does not imply correction or clinical gain.

## Two deliberate failures

- Stable but wrong: all members/final mask empty, reference nonempty;
  disagreement is zero while spatial error is positive.
- FPV/FNV cancellation: equal disjoint foreground volumes yield zero net
  volume error but positive spatial error.

Tests check reference separation/invariance, error identities, fixed-final MTV,
expected ties, common evaluation sets, reproducibility, labels and unchanged
historical JSON. No clinical confidence interval, p-value or superiority claim
is estimated. Artificial examples cannot establish clinical benefit.

FDG20 remains **DEVELOPMENT / TRAINING_EXPOSURE_NOT_EXCLUDED**; G1 remains
**BLOCKED_PROVENANCE**, Phase C **NOT_RUN**, historical Route A
**PENDING_CUSTODIAN_EVIDENCE**, new Route B **DESIGN CANDIDATE / NOT RUN**.
The demo reads no private evidence and changes none of these gates.
