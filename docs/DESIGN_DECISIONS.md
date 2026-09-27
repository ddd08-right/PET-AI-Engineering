# v0.3 Design Decisions

1. Voxel Dice and PET quantitative error are different endpoints. Similar overlap can still yield different physical volumes or masked image summaries.
2. Voxel spacing is required because voxel count alone cannot determine a physical volume in mL.
3. Reliability is evaluated at case level because review decisions and quantitative errors concern complete cases, not isolated voxels.
4. Multiple simple candidates expose whether agreement, physical-volume stability, or probability uncertainty carries useful ranking information.
5. Fixed-seed random ranking is a neutral control; reverse ranking is a deliberate negative control that checks evaluation direction.
6. Best-case reference ranking uses unavailable true error and is only a methodological reference, never a deployable reliability method.
7. Risk--coverage models fixed-budget selective review: highest predicted-risk cases leave automatic handling first.
8. Synthetic arrays test mathematics and engineering behavior. They do not establish clinical validation, clinical utility, or external generalization.
9. No additional network architecture was added because v0.3 isolates the quantification and evaluation layer downstream of existing segmentation outputs.
10. The spacing-only volume API remains for compatibility and assumes orthogonal voxel axes. NIfTI-facing volume uses `abs(det(affine[:3, :3])) / 1000` after unit and coded-transform validation, so shear and reflection are handled without presentation rounding.
11. Physical NIfTI evaluation requires at least one coded qform/sform. This is a conservative project policy, not a statement that every otherwise legal NIfTI must contain matching coded transforms.
12. Training-wrapper seeds are declarations unless runtime evidence establishes the effective trainer state. A manifest failure after a successful trainer run is an overall wrapper failure; a trainer failure retains its original exit code.
