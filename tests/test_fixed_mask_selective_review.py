"""Mathematical contracts, not patient performance tests."""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import fields
from pathlib import Path

import numpy as np
import pytest

from pet_ai.reliability import aurc, risk_coverage_curve

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fixed_review_demo", ROOT / "scripts/demo_fixed_mask_selective_review.py",
)
demo = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = demo
SPEC.loader.exec_module(demo)


def test_reference_blindness_and_changed_reference_changes_error():
    assert "reference" not in {f.name for f in fields(demo.SyntheticPrediction)}
    predictions, references = demo.synthetic_inputs()
    for prediction, reference in zip(predictions, references, strict=True):
        before = demo.reference_free_scores(prediction)
        original = prediction.final_mask.copy()
        first = demo.reference_based_errors(prediction, reference)
        second = demo.reference_based_errors(prediction, 1 - reference)
        assert demo.reference_free_scores(prediction) == before
        assert first != second
        np.testing.assert_array_equal(prediction.final_mask, original)


def test_scores_follow_fixed_mask_and_probability_contract():
    predictions, _ = demo.synthetic_inputs()
    for prediction in predictions:
        score = demo.reference_free_scores(prediction)
        mean = np.mean(prediction.member_probabilities, axis=0)
        expected_entropy = np.mean(-mean * np.log(mean) - (1 - mean) * np.log(1 - mean))
        assert score["entropy"] == pytest.approx(expected_entropy)
        assert score["member_probability_variance"] == pytest.approx(
            np.var(prediction.member_probabilities, axis=0, ddof=0).mean())
        assert score["predicted_mtv_ml"] == pytest.approx(prediction.final_mask.sum() * 8 / 1000)
    prediction = predictions[-1]
    assert demo.reference_free_scores(prediction)["predicted_mtv_ml"] != pytest.approx(
        np.mean([m.sum() for m in prediction.member_masks]) * 8 / 1000)


def test_cancellation_and_stable_but_wrong():
    predictions, references = demo.synthetic_inputs()
    stable = demo.reference_based_errors(predictions[1], references[1])
    assert demo.reference_free_scores(predictions[1])["pairwise_disagreement"] == 0
    assert stable["fpv_ml"] == 0
    assert stable["fnv_ml"] == pytest.approx(8 * 8 / 1000)
    assert stable["r_spatial_ml"] > 0
    cancel = demo.reference_based_errors(predictions[2], references[2])
    assert cancel["fpv_ml"] == cancel["fnv_ml"] == pytest.approx(8 * 8 / 1000)
    assert cancel["e_mtv_ml"] == 0
    assert cancel["r_spatial_ml"] == pytest.approx(2 * 8 * 8 / 1000)


def test_expected_ties_and_common_risks_are_order_invariant():
    predictions, references = demo.synthetic_inputs()
    errors = np.array([demo.reference_based_errors(p, r)["r_spatial_ml"]
                       for p, r in zip(predictions, references, strict=True)])
    permutation = [3, 1, 0, 2]
    for name in demo.reference_free_scores(predictions[0]):
        scores = np.array([demo.reference_free_scores(p)[name] for p in predictions])
        c, risk = risk_coverage_curve(errors, scores)
        cp, rp = risk_coverage_curve(errors[permutation], scores[permutation])
        np.testing.assert_allclose(c, [0.25, 0.5, 0.75, 1])
        np.testing.assert_allclose(cp, c)
        np.testing.assert_allclose(rp, risk)
        assert aurc(errors, scores) == pytest.approx(np.mean(risk))
        assert risk[-1] == pytest.approx(errors.mean())


def test_demo_repeatable_labeled_and_historical_json_unchanged(capsys):
    paths = [ROOT / "docs/fdg20_pilot_aggregate_summary.json",
             ROOT / "docs/development_baseline_40e_summary.json"]
    before = [p.read_bytes() for p in paths]
    first = demo.benchmark()
    assert first == demo.benchmark()
    demo.main()
    output = capsys.readouterr().out
    assert "SYNTHETIC" in output and "NO CLINICAL CLAIM" in output
    assert json.loads(output) == first
    assert len(first["cases"]) == 4
    assert all(len(m["coverage"]) == 4 for m in first["methods"].values())
    assert before == [p.read_bytes() for p in paths]
