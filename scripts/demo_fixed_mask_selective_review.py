"""SYNTHETIC mathematical benchmark; NO CLINICAL CLAIM."""

from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np

from pet_ai.evaluation.segmentation import evaluate_binary_segmentation
from pet_ai.reliability import (
    aurc,
    predictive_entropy,
    risk_coverage_curve,
    segmentation_disagreement,
)

VOXEL_VOLUME_MM3 = 8.0
REVIEW_FRACTION = 0.5


@dataclass(frozen=True)
class SyntheticPrediction:
    """Prediction-only input, deliberately without a reference field."""

    case_id: str
    final_mask: np.ndarray
    member_probabilities: tuple[np.ndarray, ...]
    member_masks: tuple[np.ndarray, ...]
    voxel_volume_mm3: float = VOXEL_VOLUME_MM3


def mask(start: int, stop: int) -> np.ndarray:
    result = np.zeros((4, 4, 4), dtype=np.uint8)
    result[start:stop, :2, :2] = 1
    return result


def synthetic_inputs() -> tuple[list[SyntheticPrediction], list[np.ndarray]]:
    """Artificial arrays only: not trained folds, seeds or official inference."""
    empty, small, large, shifted = mask(0, 0), mask(0, 1), mask(0, 2), mask(2, 4)
    specifications = [
        ("SYNTHETIC_CORRECT", small, small, [small] * 5),
        ("SYNTHETIC_STABLE_BUT_WRONG", empty, large, [empty] * 5),
        ("SYNTHETIC_CANCELLATION", shifted, large, [shifted] * 5),
        ("SYNTHETIC_MEMBER_DISAGREEMENT", large, small, [empty, small, large, shifted, large]),
    ]
    predictions, references = [], []
    for case_id, final, reference, members in specifications:
        probabilities = tuple(np.where(m != 0, 0.9, 0.1) for m in members)
        predictions.append(SyntheticPrediction(
            case_id, final.copy(), probabilities,
            tuple((p > 0.5).astype(np.uint8) for p in probabilities),
        ))
        references.append(reference.copy())
    return predictions, references


def reference_free_scores(prediction: SyntheticPrediction) -> dict[str, float]:
    """High-is-risk scores on the entire fixed evaluation grid."""
    return {
        "entropy": float(np.mean(predictive_entropy(prediction.member_probabilities))),
        "member_probability_variance": float(np.mean(np.var(
            np.stack(prediction.member_probabilities), axis=0, ddof=0,
        ))),
        "predicted_mtv_ml": float(np.count_nonzero(prediction.final_mask)
                                  * prediction.voxel_volume_mm3 / 1000.0),
        "pairwise_disagreement": segmentation_disagreement(prediction.member_masks),
    }


def reference_based_errors(
    prediction: SyntheticPrediction, reference: np.ndarray,
) -> dict[str, float]:
    metrics = evaluate_binary_segmentation(
        prediction.final_mask, reference, voxel_volume_mm3=prediction.voxel_volume_mm3,
    )
    return {"fpv_ml": metrics.fpv_ml, "fnv_ml": metrics.fnv_ml,
            "r_spatial_ml": metrics.fpv_ml + metrics.fnv_ml,
            "e_mtv_ml": abs(metrics.fpv_ml - metrics.fnv_ml)}


def benchmark() -> dict:
    """Compute JSON-safe results, without writing analysis files."""
    predictions, references = synthetic_inputs()
    scores = [reference_free_scores(p) for p in predictions]
    errors = [reference_based_errors(p, r) for p, r in zip(predictions, references, strict=True)]
    risks = np.asarray([e["r_spatial_ml"] for e in errors])
    methods = {}
    for name in scores[0]:
        values = np.asarray([s[name] for s in scores])
        coverage, retained = risk_coverage_curve(risks, values)
        retained_count = int(len(predictions) * (1.0 - REVIEW_FRACTION))
        groups = [[p.case_id for p, value in zip(predictions, values, strict=True) if value == v]
                  for v in sorted(set(values), reverse=True)]
        methods[name] = {
            "synthetic_aurc_ml": aurc(risks, values),
            "coverage": coverage.tolist(), "retained_risk_ml": retained.tolist(),
            "risk_at_review_fraction_ml": float(retained[retained_count - 1]),
            "review_priority_tie_groups_high_first": groups,
        }
    return {
        "label": "SYNTHETIC MATHEMATICAL DEMONSTRATIONS / NO CLINICAL CLAIM",
        "contract": "Fixed artificial masks; five artificial probability arrays, not folds/seeds; no inference",
        "tie_policy": "expected over within-tie permutations, common to all methods",
        "review_fraction": REVIEW_FRACTION,
        "cases": [{"case_id": p.case_id, "voxel_volume_mm3": p.voxel_volume_mm3,
                   "scores": s, "errors": e}
                  for p, s, e in zip(predictions, scores, errors, strict=True)],
        "methods": methods,
        "reference_informed_oracle_aurc_ml": aurc(risks, risks),
        "analytic_random_expected_aurc_ml": float(np.mean(risks)),
        "analytic_random_expected_retained_risk_ml": float(np.mean(risks)),
    }


def main() -> None:
    print(json.dumps(benchmark(), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
