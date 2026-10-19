from __future__ import annotations

import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from scripts.render_fdg20_public_figure import render_svg, validate_payload


def synthetic_payload() -> dict:
    methods = [
        {
            "name": "Entropy",
            "analysis_status": "FROZEN_ANALYSIS",
            "discrete_AURC_mL": 1.0,
            "mean_retained_R_at_80pct_coverage_mL": 2.0,
            "cohort_FNV_share_in_4_referrals": 0.25,
        },
        {
            "name": "Fold variance",
            "analysis_status": "FROZEN_ANALYSIS",
            "discrete_AURC_mL": 2.0,
            "mean_retained_R_at_80pct_coverage_mL": 3.0,
            "cohort_FNV_share_in_4_referrals": 0.5,
        },
        {
            "name": "Predicted MTV (size baseline; not UQ)",
            "analysis_status": "POST_HOC",
            "discrete_AURC_mL": 3.0,
            "mean_retained_R_at_80pct_coverage_mL": 4.0,
            "cohort_FNV_share_in_4_referrals": 0.75,
        },
        {
            "name": "Pairwise disagreement",
            "analysis_status": "POST_HOC",
            "discrete_AURC_mL": 4.0,
            "mean_retained_R_at_80pct_coverage_mL": 5.0,
            "cohort_FNV_share_in_4_referrals": 0.0,
        },
    ]
    return {
        "schema": "fdg20-pilot-aggregate-summary-v2",
        "cohort": {
            "n": 20,
            "reference_foreground_annotations": 10,
            "empty_reference_annotations": 10,
            "training_exposure_excluded": False,
            "independent_validation": False,
        },
        "risk": {
            "definition": "R = FPV + FNV",
            "unit": "mL",
            "coverage_80": "16 retained / 4 referred",
            "lower_AURC_is_better": True,
        },
        "methods": methods,
        "references": {
            "random_analytic_expected_AURC_mL": 10.0,
            "oracle_AURC_mL": 0.5,
        },
    }


def test_synthetic_payload_renders_both_aggregate_panels():
    payload = synthetic_payload()

    validate_payload(payload)
    svg = render_svg(payload)

    assert "A. Discrete AURC" in svg
    assert "B. Cohort FNV assigned" in svg
    assert "Random analytic expectation" in svg
    assert "Reference-informed oracle" in svg
    assert "80% coverage = 16 retained / 4 referred" in svg
    assert "<script" not in svg.lower()
    assert "file:///" not in svg.lower()


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("schema", "unsupported aggregate schema"),
        ("case_id", "case-level fields are not permitted"),
        ("training", "cohort scope does not match"),
        ("share", "FNV share outside"),
    ],
)
def test_contract_rejects_invalid_or_case_level_data(mutation: str, message: str):
    payload = synthetic_payload()
    if mutation == "schema":
        payload["schema"] = "wrong"
    elif mutation == "case_id":
        payload["case_id"] = "not-permitted"
    elif mutation == "training":
        payload["cohort"]["training_exposure_excluded"] = True
    else:
        payload["methods"][0]["cohort_FNV_share_in_4_referrals"] = 1.1

    with pytest.raises(ValueError, match=message):
        validate_payload(payload)


def test_real_aggregate_json_and_png_are_public_aggregate_artifacts():
    root = Path(__file__).absolute().parents[1]
    payload = json.loads(
        (root / "docs" / "fdg20_pilot_aggregate_summary.json").read_text(encoding="utf-8")
    )
    validate_payload(payload)
    svg = render_svg(payload)
    assert "Pairwise disagreement" in svg
    assert "POST_HOC" not in svg

    png = (root / "docs" / "figures" / "fdg20_pilot_aggregate.png").read_bytes()
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", png[16:24]) == (1800, 1220)


def test_cli_writes_svg_to_requested_location():
    root = Path(__file__).absolute().parents[1]
    script = root / "scripts" / "render_fdg20_public_figure.py"
    source = root / "docs" / "fdg20_pilot_aggregate_summary.json"
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "nested" / "summary.svg"
        result = subprocess.run(
            [sys.executable, str(script), "--input", str(source), "--output", str(output)],
            capture_output=True,
            check=False,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert output.is_file()
        assert output.read_text(encoding="utf-8").lstrip().startswith("<svg ")
