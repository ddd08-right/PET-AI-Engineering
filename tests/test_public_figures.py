from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import render_public_figures

ROOT = Path(__file__).resolve().parents[1]


def test_metric_figure_uses_frozen_values_counts_and_semantic_order() -> None:
    data = json.loads(
        (ROOT / "docs/development_baseline_40e_summary.json").read_text(
            encoding="utf-8"
        )
    )
    svg = render_public_figures.metric_svg(data)
    labels = (
        "Final",
        "EMA-selected",
        "Analytic empty control",
    )
    positions = [svg.index(f">{label}</text>") for label in labels]
    assert positions == sorted(positions)
    assert "0.0991" in svg and "0.2187" in svg and "0.0000" in svg
    assert "59.43 mL" in svg and "63.21 mL" in svg and "33.30 mL" in svg
    assert svg.count("n=3 of 5") == 3
    assert svg.count("n=5 of 5") == 3
    assert "not model inference" in svg
    assert "0.0" in svg and "1.0" in svg and "70" in svg


@pytest.mark.parametrize("failure", ("missing", "nonfinite"))
def test_figure_input_validation_fails_closed(tmp_path: Path, monkeypatch, failure: str) -> None:
    summary_path = ROOT / "docs/development_baseline_40e_summary.json"
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    if failure == "missing":
        del data["aggregates"]["final"]["strict_dice"]["mean"]
    else:
        data["aggregates"]["final"]["strict_dice"]["mean"] = float("nan")
    altered_summary = tmp_path / "summary.json"
    altered_summary.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(render_public_figures, "SUMMARY", altered_summary)

    with pytest.raises(ValueError):
        render_public_figures.load_and_validate_inputs()


def test_optional_png_render_reports_missing_browser(tmp_path: Path) -> None:
    svg = tmp_path / "synthetic.svg"
    svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")

    with pytest.raises(RuntimeError, match="SVG preview render failed"):
        render_public_figures.render_png(
            tmp_path / "missing-browser",
            svg,
            tmp_path / "synthetic.png",
            10,
            10,
        )
