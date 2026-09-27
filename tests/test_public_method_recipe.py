from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/pet_ai/nnunet_extensions/development_baseline_40e.py"
CONFIG = ROOT / "configs/development_baseline_40e/method.json"


def test_optional_nnunet_extension_compiles_without_importing_gpu_dependencies() -> None:
    compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec")


def test_public_sampler_branches_with_mock_upstream_loader_and_rng(monkeypatch) -> None:
    """Exercise public sampler code directly under tiny synthetic strata."""
    module_names = (
        "batchgenerators",
        "batchgenerators.utilities",
        "batchgenerators.utilities.file_and_folder_operations",
        "nnunetv2",
        "nnunetv2.training",
        "nnunetv2.training.dataloading",
        "nnunetv2.training.dataloading.data_loader",
        "nnunetv2.training.nnUNetTrainer",
        "nnunetv2.training.nnUNetTrainer.variants",
        "nnunetv2.training.nnUNetTrainer.variants.training_length",
        "nnunetv2.training.nnUNetTrainer.variants.training_length.nnUNetTrainer_Xepochs",
    )
    for name in module_names:
        monkeypatch.setitem(sys.modules, name, ModuleType(name))

    class FakeDataLoader:
        def __init__(self, *_args, **_kwargs):
            self._data = SimpleNamespace(source_folder="synthetic")
            self.indices = ["negative-a", "negative-b", "positive-a"]

    class FakeTrainer:
        pass

    files_module = sys.modules[
        "batchgenerators.utilities.file_and_folder_operations"
    ]
    files_module.join = lambda folder, name: f"{folder}/{name}"
    files_module.load_pickle = lambda path: {
        "class_locations": {1: [] if "negative" in path else [(0, 0, 0)]}
    }
    sys.modules[
        "nnunetv2.training.dataloading.data_loader"
    ].nnUNetDataLoader = FakeDataLoader
    sys.modules[
        "nnunetv2.training.nnUNetTrainer.variants.training_length.nnUNetTrainer_Xepochs"
    ].nnUNetTrainer_20epochs = FakeTrainer

    spec = importlib.util.spec_from_file_location("public_recipe_test", SOURCE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    choices = iter(("negative-b", "positive-a"))

    def choose_next(_population):
        return next(choices)

    monkeypatch.setattr(module.np.random, "choice", choose_next)
    loader = module.DevelopmentMidpointDataLoader()
    assert loader.negative_identifiers == ["negative-a", "negative-b"]
    assert loader.positive_identifiers == ["positive-a"]
    assert loader.get_indices().tolist() == ["negative-b", "positive-a"]

    monkeypatch.setattr(module.np.random, "uniform", lambda: 0.81)
    assert loader.get_do_oversample(0) is False
    assert loader.get_do_oversample(1) is True
    monkeypatch.setattr(module.np.random, "uniform", lambda: 0.82)
    assert loader.get_do_oversample(1) is False


def test_public_recipe_is_parameterized_and_contains_no_private_payload() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    config = json.loads(CONFIG.read_text(encoding="utf-8"))

    assert ("D:" + "\\") not in source
    assert "AUTOPETL_" not in source
    assert config["evidence_status"] == "PARTIAL_RECIPE"
    assert config["dataset"]["required_argument"] is True
    assert config["dataset"]["private_split_membership_included"] is False
    assert config["sampling"]["slot_1"].endswith("0.82")
