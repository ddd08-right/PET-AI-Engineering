from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

POWERSHELL = shutil.which("powershell.exe") or shutil.which("pwsh.exe")
REPO_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = REPO_ROOT / "scripts" / "train_nnunet.ps1"
VALIDATION_PYTHON = REPO_ROOT.parents[1] / (
    "_pet_ai_public_validation_20260924_01/venv/Scripts/python.exe"
)


def _fake_command(path: Path, exit_code: int) -> Path:
    path.write_text(f"@echo off\r\nexit /b {exit_code}\r\n", encoding="ascii")
    return path


def _run_wrapper(
    tmp_path: Path,
    trainer: Path,
    *,
    manifest: Path | None = None,
    manifest_python: Path = VALIDATION_PYTHON,
    seed_parameter: str | None = None,
) -> subprocess.CompletedProcess[str]:
    if POWERSHELL is None:
        pytest.skip("PowerShell is unavailable")
    command = [
        POWERSHELL,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(WRAPPER),
        "-Dataset",
        "901",
        "-Configuration",
        "3d_fullres",
        "-Fold",
        "0",
        "-Trainer",
        "MockTrainer",
        "-NnUNetTrainExe",
        str(trainer),
        "-ManifestPython",
        str(manifest_python),
    ]
    if manifest is not None:
        command += ["-RunManifestOut", str(manifest)]
    if seed_parameter is not None:
        command += [seed_parameter, "20260924"]
    environment = os.environ.copy()
    environment.update(
        {
            "nnUNet_raw": str(tmp_path / "raw"),
            "nnUNet_preprocessed": str(tmp_path / "preprocessed"),
            "nnUNet_results": str(tmp_path / "results"),
        }
    )
    return subprocess.run(
        command,
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def test_wrapper_success_and_caller_independent_manifest_path(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "run.json"
    result = _run_wrapper(
        tmp_path,
        _fake_command(tmp_path / "trainer.cmd", 0),
        manifest=output,
        seed_parameter="-DeclaredSeed",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["declared_seed"] == 20260924
    assert data["effective_seed"] is None
    assert data["seed_verification_status"] == "UNVERIFIED_DECLARATION_ONLY"
    assert data["exit_status"] == 0


def test_wrapper_preserves_nonzero_trainer_exit(tmp_path: Path) -> None:
    output = tmp_path / "run.json"
    result = _run_wrapper(tmp_path, _fake_command(tmp_path / "trainer.cmd", 23), manifest=output)

    assert result.returncode == 23
    assert json.loads(output.read_text(encoding="utf-8"))["exit_status"] == 23


def test_wrapper_uses_distinct_launch_failure_exit(tmp_path: Path) -> None:
    output = tmp_path / "run.json"
    result = _run_wrapper(tmp_path, tmp_path / "missing-trainer.exe", manifest=output)

    assert result.returncode == 127
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["exit_status"] == 127
    assert "trainer_launch_status=LAUNCH_FAILED" in data["notes"]


def test_manifest_failure_cannot_hide_successful_training(tmp_path: Path) -> None:
    result = _run_wrapper(
        tmp_path,
        _fake_command(tmp_path / "trainer.cmd", 0),
        manifest=tmp_path / "missing.json",
        manifest_python=_fake_command(tmp_path / "manifest-fails.cmd", 9),
    )

    assert result.returncode == 70


def test_deprecated_seed_alias_warns_and_records_declaration(tmp_path: Path) -> None:
    output = tmp_path / "run.json"
    result = _run_wrapper(
        tmp_path,
        _fake_command(tmp_path / "trainer.cmd", 0),
        manifest=output,
        seed_parameter="-Seed",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "deprecated" in (result.stdout + result.stderr).lower()
    assert json.loads(output.read_text(encoding="utf-8"))["declared_seed"] == 20260924
