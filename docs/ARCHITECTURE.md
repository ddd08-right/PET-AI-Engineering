# Architecture

The repository contains three evidence tracks that share validation,
evaluation, and provenance utilities. They should not be read as one completed
real-patient pipeline.

## Evidence tracks

| Track | Main path | Status and boundary |
| --- | --- | --- |
| Native PyTorch teaching baseline | Synthetic `torch.utils.data.Dataset` → compact 3D U-Net → loss → backward → optimizer update | `ENGINEERING_SMOKE`; synthetic tensors and CPU checks, with no patient-performance claim. |
| nnU-Net development case | Protected CT/PET inputs → upstream nnU-Net plus public sampler adaptation → five-case aggregate evaluation | `DEVELOPMENT_EXPOSED`; one seed, fold 0, and no independent or external test. The published method is a post-hoc `PARTIAL_RECIPE`. |
| Reliability toolkit | Errors and risk scores → ranking → risk–coverage/AURC | Synthetic mathematical validation; a real-patient reliability study is incomplete. |

All three tracks can use the same foundations: public-safe manifest and split
validation, NIfTI geometry and label QC, segmentation and quantification
metrics, SHA256 hashing, run manifests, and failure records. Sharing utilities
does not raise one track's evidence status to that of another.

## Data validation is not a PyTorch Dataset

[`pet_ai.data.manifest`](../src/pet_ai/data/manifest.py) validates tabular
metadata, while [`pet_ai.data.split_validation`](../src/pet_ai/data/split_validation.py)
checks patient keys across train, validation, and test partitions. These
modules do not load tensors or define model batches.

[`SyntheticPETCTDataset`](../src/pet_ai/datasets/synthetic_petct.py) is a
PyTorch `Dataset` that deterministically creates two-channel PET/CT-like tensors
and binary labels for software tests. Its samples are synthetic fixtures, not a
clinical dataset or a bridge to the protected development cohort.

## Shared module responsibilities

| Concern | Implementation | Contract |
| --- | --- | --- |
| Geometry and labels | [`pet_ai.qc`](../src/pet_ai/qc) | Validate explicit spatial units, coded transforms, common grids, finite binary labels, and configured empty-mask policy; do not silently repair data. |
| Evaluation and quantification | [`pet_ai.evaluation`](../src/pet_ai/evaluation), [`pet_ai.quantification`](../src/pet_ai/quantification) | Report voxel/lesion behavior and physical quantities under explicit unit and empty-reference rules. |
| Reliability | [`pet_ai.reliability`](../src/pet_ai/reliability) | Compute synthetic disagreement and risk–coverage quantities without claiming patient-level validation. |
| Provenance | [`pet_ai.reproducibility`](../src/pet_ai/reproducibility) | Record hashes and run metadata; distinguish a declared seed from verified effective runtime control. |

## Repository layers

- [`scripts/`](../scripts) contains command-line and PowerShell entry points.
  They coordinate modules or upstream commands; they are not the primary home
  of reusable implementation logic.
- [`src/pet_ai/`](../src/pet_ai) contains the reusable Python implementation,
  including the synthetic PyTorch path and the public nnU-Net adaptation.
- [`tests/`](../tests) checks observable behavior with synthetic fixtures,
  analytic arrays, static recipe checks, and mocked wrapper executables. Tests
  do not reproduce the protected five-case run.
- [`docs/DEVELOPMENT_BASELINE_40E_CASE.md`](DEVELOPMENT_BASELINE_40E_CASE.md)
  records the development case; the public method boundary is documented in
  the [`PARTIAL_RECIPE`](../configs/development_baseline_40e/README.md).

This separation keeps data checks, tensor loading, model execution, evaluation,
and provenance independently inspectable without moving or duplicating code.
