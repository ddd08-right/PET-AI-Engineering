# Programming Evidence

The strongest public programming evidence is the direct correspondence between
small implementations and behavioral tests. Unless noted otherwise, tests use
synthetic fixtures or analytic arrays and do not establish clinical validity.

## Representative implementation–test pairs

| Engineering behavior | Implementation | Behavioral evidence | Boundary |
| --- | --- | --- | --- |
| Native PyTorch forward, loss, gradients, and parameter updates | [`models/unet3d.py`](../src/pet_ai/models/unet3d.py), [`losses/segmentation.py`](../src/pet_ai/losses/segmentation.py), [`training/engine.py`](../src/pet_ai/training/engine.py) | [`test_unet3d.py`](../tests/test_unet3d.py), [`test_pytorch_loss.py`](../tests/test_pytorch_loss.py), [`test_pytorch_training.py`](../tests/test_pytorch_training.py) | Synthetic two-channel tensors; compact teaching implementation, not a novel architecture claim. |
| Geometry, units, and coded-transform policy | [`qc/geometry.py`](../src/pet_ai/qc/geometry.py) | [`test_geometry.py`](../tests/test_geometry.py) | Compares shape, millimetre-normalized spacing, orientation, affine, and qform/sform policy on synthetic NIfTI files. |
| Affine-aware physical volume | [`quantification/volume.py`](../src/pet_ai/quantification/volume.py) | [`test_quantification.py`](../tests/test_quantification.py), [`test_real_data_audit.py`](../tests/test_real_data_audit.py) | Uses the absolute determinant of a validated millimetre affine; covers orthogonal, sheared, and reflected synthetic grids. |
| Segmentation counts and physical error volumes | [`evaluation/segmentation.py`](../src/pet_ai/evaluation/segmentation.py) | [`test_segmentation_metrics.py`](../tests/test_segmentation_metrics.py) | Validates binary 3D inputs and common geometry; reports TP/FP/FN, Dice, FPV, and FNV. |
| Lesion matching and ambiguity reporting | [`evaluation/lesion_metrics.py`](../src/pet_ai/evaluation/lesion_metrics.py) | [`test_lesion_metrics.py`](../tests/test_lesion_metrics.py) | Deterministic connected-component overlap matching; split/merge ambiguity is surfaced rather than interpreted biologically. |
| Risk–coverage and score ties | [`reliability/risk_coverage.py`](../src/pet_ai/reliability/risk_coverage.py) | [`test_risk_coverage.py`](../tests/test_risk_coverage.py) | Default tie handling computes the expected risk across within-tie permutations; input-order-dependent `stable` behavior is an explicit legacy option. |
| Run provenance and seed semantics | [`reproducibility/run_manifest.py`](../src/pet_ai/reproducibility/run_manifest.py), [`train_nnunet.ps1`](../scripts/train_nnunet.ps1) | [`test_run_manifest.py`](../tests/test_run_manifest.py), [`test_train_nnunet_wrapper.py`](../tests/test_train_nnunet_wrapper.py) | Records declared seed metadata separately from evidence of effective runtime control; wrapper tests use mocks, not training. |
| Public development sampler/trainer adaptation | [`development_baseline_40e.py`](../src/pet_ai/nnunet_extensions/development_baseline_40e.py) | [`test_public_method_recipe.py`](../tests/test_public_method_recipe.py) | Static checks cover a post-hoc `PARTIAL_RECIPE`; the protected run is not reproduced. |

## Empty-reference Dice policy

The standard Dice formula gives `0` when the reference is empty and the
prediction is non-empty; it becomes `0/0` only when both masks are empty. The
project's public `dice_from_counts` API intentionally preserves the historical
policy of returning `NaN` whenever the reference is empty, serialized as
`null` with status `UNDEFINED_EMPTY_GT`. The strict development-case aggregate
therefore excludes all empty-reference cases from Dice and averages the three
non-empty references. This API policy is not presented as a universal
mathematical definition. FPV, FNV, and absolute volume error retain all five
development cases.

## Contribution and dependency boundary

- **Implemented in this repository:** validation and QC utilities, metric and
  reliability functions, provenance helpers, the compact synthetic PyTorch
  teaching path, wrappers, tests, and the parameterized public development
  adaptation.
- **Upstream dependencies:** PyTorch supplies the tensor framework and
  optimizer primitives. nnU-Net supplies its architecture, data-loader base,
  transforms, loss, PolyLR, checkpointing, and online EMA pseudo-Dice
  selection. AutoPET data and labels are not repository-authored.
- **Public adaptation:**
  [`development_baseline_40e.py`](../src/pet_ai/nnunet_extensions/development_baseline_40e.py)
  is a renamed, path-parameterized, public-safe extraction of the sampler and
  40-epoch trainer settings. It is not asserted to be the complete historical
  launcher.
- **Private historical orchestration:** protected data staging, split
  membership, recovery guard, budget controls, original launcher, weights, and
  per-case evaluation inputs are absent. Their omission prevents independent
  reproduction of the frozen five-case aggregates.

Additional modules and entry points remain documented in the
[architecture overview](ARCHITECTURE.md); this page intentionally emphasizes a
small set of inspectable implementation–test relationships rather than a claim
of sole authorship or contribution percentage.
