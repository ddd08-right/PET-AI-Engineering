# 40-epoch development baseline — partial recipe

**Evidence status: `PARTIAL_RECIPE`.** This directory is a post-hoc, public-safe
extraction of the method used by the single-seed, fold-0 development case. It is
not a runnable reproduction of the five-case result from this public repository.

## Inputs and contract

![Two annotation-coordinate case pools are sampled uniformly into fixed slots: slot 0 uses force foreground false; slot 1 draws u uniformly from zero to one and forces foreground when u is below 0.82. Both delegate patch selection to upstream nnU-Net get_bbox.](../../docs/figures/midpoint_sampling.svg)

*Figure. Pool membership is defined by class-1 annotation coordinates; no
coordinates does not mean clinical absence. `0.82` is the slot-1
foreground-force probability, not the positive-case sampling proportion. Both
slots delegate patch selection to upstream nnU-Net `get_bbox`, whose behavior
can depend on ignore-label settings. [PNG
preview](../../docs/figures/midpoint_sampling.png).*

- Install the historical nnU-Net/PyTorch environment separately. These are not
  core package dependencies.
- This run used `nnUNet_n_proc_DA=0`. Set that variable explicitly because
  `scripts/train_nnunet.ps1` otherwise defaults it to `1`.
- Supply `nnUNet_raw`, `nnUNet_preprocessed`, and `nnUNet_results`; no local
  path is embedded here.
- Dataset channel 0 is CT, channel 1 is PET, and label 1 is lesion foreground.
  Supply an nnU-Net dataset JSON, locked plans, preprocessed arrays/properties,
  and a patient-grouped split matching the schema in `method.json`.
- The extracted trainer preserves batch size 2, patch size `[160, 112, 96]`,
  40 epochs, upstream loss/PolyLR behavior, and the recorded negative/positive
  midpoint sampling policy.

The word “negative” here means that the preprocessed properties contain no
class-1 annotation coordinates; it does not establish clinical absence. The
loader assigns that stratum to batch slot 0 and calls upstream
`get_do_oversample(0) = False`. Slot 1 is drawn uniformly from cases with
class-1 coordinates. `0.82` is the probability of calling
`get_do_oversample(1) = True`; it is not a probability for selecting a positive
case. Patch-box selection is delegated to upstream `get_bbox`: with no
ignore-label mode, false selects a random box and true centers the box on a
selected foreground coordinate. Upstream ignore-label handling can change the
false branch, so exact patch selection also depends on the dataset label
configuration.

Template only (not executed in this repository):

```powershell
$env:nnUNet_extTrainer = (Resolve-Path src/pet_ai/nnunet_extensions)
$env:nnUNet_n_proc_DA = "0"
.\scripts\train_nnunet.ps1 -Dataset <DATASET_ID> -Configuration 3d_fullres -Fold 0 `
  -Trainer nnUNetTrainer_DevelopmentBaseline40epochs -Plans nnUNetPlans_6G `
  -DeclaredSeed 20260924 -RunManifestOut <OUTPUT_JSON>
```

The wrapper records `DeclaredSeed`; it does not make that value the effective
trainer seed. A real launch must arrange and verify Python, NumPy, PyTorch,
CUDA, and augmentation-worker RNG state in its own environment. This public
copy does not seed RNGs. The private run launcher had separate seed setup; the
public wrapper's declared seed is manifest metadata only.

## Outputs and limits

nnU-Net owns checkpoints, logs, and validation predictions under
`nnUNet_results`. The wrapper additionally writes a JSON manifest and preserves
trainer exit status. The historical recovery used a checkpoint-specific
fail-closed guard, but its resume did not save prior RNG history. That guard is
not part of the public trainer. The public trainer retains an epoch checkpoint
hook, not the checkpoint-specific recovery guard. Its recipe also omits the
historical launcher's wall-clock budget/stop policy, recovery validation, RNG
seeding, output isolation, and result-evaluation orchestration. The historical
resume is not claimed bitwise reproducible.

No patient data, weights, private split membership, or local paths are included.
The public CPU validation environment can compile and statically inspect this
module. An import-only smoke in the available historical environment resolved
the class with Torch `2.13.0+cu126` and nnU-Net `2.8.1`; the protected start
manifest records the nnU-Net version as `UNKNOWN`, so this smoke does not
establish the exact runtime version used by the historical run. No trainer was
instantiated and no training or inference was run.

## Dependency status

- `PUBLIC_IMPLEMENTATION`: the balanced case-slot loader, 0.82 foreground-force
  branch, and 40-epoch trainer in
  `src/pet_ai/nnunet_extensions/development_baseline_40e.py`.
- `UPSTREAM_DEPENDENCY`: nnU-Net's `nnUNetDataLoader`, `nnUNetTrainer_20epochs`,
  trainer transforms, augmenters, `get_allowed_n_proc_DA`, patch bounding-box
  selection, loss, and PolyLR; NumPy; and batchgenerators pickle/path helpers.
- `MISSING`: the private `recovery_guard.py`, private `run_baseline.py`
  orchestration and data staging / budget controls, and the original protected
  cohort and preprocessed artifacts. This method folder cannot reproduce the
  historical five-case result by itself.

## Provenance

The protected start manifest bound the midpoint implementation to SHA-256
`7ab8e12c35dd3c24cf50040b1388396a74679870fdbe3b2ba5c6e30d068856d4`.
The launch-time baseline trainer hash recorded there was
`cf3563022f7934bd239f9d6057a8b86b14a907b1d262cbffe2928368832739c6`;
the later recovery source is not represented as the original launch file.
This public copy renames classes, removes experiment stop switches and private
recovery bindings, parameterizes paths, and keeps the sampler/trainer settings.
