"""Public-safe 40-epoch development-baseline trainer recipe.

This is a post-hoc extraction from source files bound in the protected run
manifest. It needs the historical nnU-Net environment and has not been trained
or imported in the public CPU environment.
"""

from __future__ import annotations

import numpy as np
from batchgenerators.utilities.file_and_folder_operations import join, load_pickle
from nnunetv2.training.dataloading.data_loader import nnUNetDataLoader
from nnunetv2.training.nnUNetTrainer.variants.training_length.nnUNetTrainer_Xepochs import (
    nnUNetTrainer_20epochs,
)


class DevelopmentBalancedDataLoader(nnUNetDataLoader):
    """Fill batch slot 0 from negative cases and slot 1 from positive cases."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        properties = {
            identifier: load_pickle(join(self._data.source_folder, identifier + ".pkl"))
            for identifier in self.indices
        }
        self.negative_identifiers = [
            identifier
            for identifier, props in properties.items()
            if len(props["class_locations"].get(1, [])) == 0
        ]
        self.positive_identifiers = [
            identifier
            for identifier, props in properties.items()
            if len(props["class_locations"].get(1, [])) > 0
        ]
        if not self.negative_identifiers or not self.positive_identifiers:
            raise RuntimeError(
                "training fold requires non-empty positive and negative strata; "
                f"observed {len(self.positive_identifiers)} positive and "
                f"{len(self.negative_identifiers)} negative cases"
            )

    def get_indices(self):
        """Select uniformly within each stratum using the active NumPy RNG."""
        return np.asarray(
            [
                np.random.choice(self.negative_identifiers),
                np.random.choice(self.positive_identifiers),
            ]
        )


class DevelopmentMidpointDataLoader(DevelopmentBalancedDataLoader):
    """Apply the recorded 0.82 foreground-force probability in the positive slot."""

    positive_force_fg_probability = 0.82

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_do_oversample = self._midpoint_get_do_oversample

    def _midpoint_get_do_oversample(self, sample_idx: int) -> bool:
        if sample_idx == 0:
            return False
        if sample_idx == 1:
            return bool(np.random.uniform() < self.positive_force_fg_probability)
        raise RuntimeError(f"expected batch size 2, got sample index {sample_idx}")


class nnUNetTrainer_DevelopmentBaseline40epochs(nnUNetTrainer_20epochs):
    """40-epoch nnU-Net trainer with the recorded two-stratum midpoint loader."""

    def __init__(self, plans, configuration, fold, dataset_json, device):
        super().__init__(plans, configuration, fold, dataset_json, device)
        self.num_epochs = 40

    def get_dataloaders(self):
        import nnunetv2.training.nnUNetTrainer.nnUNetTrainer as base

        if self.dataset_class is None:
            self.dataset_class = base.infer_dataset_class(self.preprocessed_dataset_folder)
        patch_size = self.configuration_manager.patch_size
        deep_supervision_scales = self._get_deep_supervision_scales()
        rotation, dummy2d, initial_patch_size, mirror_axes = (
            self.configure_rotation_dummyDA_mirroring_and_inital_patch_size()
        )
        train_transforms = self.get_training_transforms(
            patch_size,
            rotation,
            deep_supervision_scales,
            mirror_axes,
            dummy2d,
            use_mask_for_norm=self.configuration_manager.use_mask_for_norm,
            is_cascaded=self.is_cascaded,
            foreground_labels=self.label_manager.foreground_labels,
            regions=(
                self.label_manager.foreground_regions
                if self.label_manager.has_regions
                else None
            ),
            ignore_label=self.label_manager.ignore_label,
        )
        validation_transforms = self.get_validation_transforms(
            deep_supervision_scales,
            is_cascaded=self.is_cascaded,
            foreground_labels=self.label_manager.foreground_labels,
            regions=(
                self.label_manager.foreground_regions
                if self.label_manager.has_regions
                else None
            ),
            ignore_label=self.label_manager.ignore_label,
        )
        dataset_train, dataset_validation = self.get_tr_and_val_datasets()
        loader_train = DevelopmentMidpointDataLoader(
            dataset_train,
            self.batch_size,
            initial_patch_size,
            patch_size,
            self.label_manager,
            oversample_foreground_percent=self.oversample_foreground_percent,
            sampling_probabilities=None,
            pad_sides=None,
            transforms=train_transforms,
            probabilistic_oversampling=self.probabilistic_oversampling,
        )
        loader_validation = base.nnUNetDataLoader(
            dataset_validation,
            self.batch_size,
            patch_size,
            patch_size,
            self.label_manager,
            oversample_foreground_percent=self.oversample_foreground_percent,
            sampling_probabilities=None,
            pad_sides=None,
            transforms=validation_transforms,
            probabilistic_oversampling=self.probabilistic_oversampling,
        )
        allowed_processes = base.get_allowed_n_proc_DA()
        if allowed_processes == 0:
            augmenter_train = base.SingleThreadedAugmenter(loader_train, None)
            augmenter_validation = base.SingleThreadedAugmenter(loader_validation, None)
        else:
            augmenter_train = base.NonDetMultiThreadedAugmenter(
                data_loader=loader_train,
                transform=None,
                num_processes=allowed_processes,
                num_cached=max(6, allowed_processes // 2),
                seeds=None,
                pin_memory=self.device.type == "cuda",
                wait_time=0.002,
            )
            augmenter_validation = base.NonDetMultiThreadedAugmenter(
                data_loader=loader_validation,
                transform=None,
                num_processes=max(1, allowed_processes // 2),
                num_cached=max(3, allowed_processes // 4),
                seeds=None,
                pin_memory=self.device.type == "cuda",
                wait_time=0.002,
            )
        _ = next(augmenter_train)
        _ = next(augmenter_validation)
        self.print_to_log_file(
            "development midpoint sampler: slot0=negative/random, "
            "slot1=positive/force_fg_probability=0.82"
        )
        return augmenter_train, augmenter_validation

    def on_epoch_end(self):
        """Retain the source recipe's per-epoch continuation checkpoint."""
        super().on_epoch_end()
        if self.local_rank == 0 and self.current_epoch < self.num_epochs:
            completed_epoch = self.current_epoch
            self.current_epoch -= 1
            self.save_checkpoint(join(self.output_folder, "checkpoint_latest.pth"))
            self.current_epoch = completed_epoch
