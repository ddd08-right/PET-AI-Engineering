from __future__ import annotations

import numpy as np
import pytest

from pet_ai.quantification import (
    affine_voxel_volume_ml,
    mask_volume_from_affine_ml,
    mask_volume_ml,
    masked_max,
    masked_mean,
    uptake_volume_product,
    voxel_volume_ml,
)


def test_affine_volume_handles_orthogonal_shear_and_reflection():
    orthogonal = np.diag([2.0, 3.0, 4.0, 1.0])
    shear = np.array([[2.0, 1.0, 0.0, 0.0], [0.0, 3.0, 0.0, 0.0], [0.0, 0.0, 4.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
    reflection = np.diag([-2.0, 3.0, 4.0, 1.0])

    assert affine_voxel_volume_ml(orthogonal) == pytest.approx(0.024)
    assert affine_voxel_volume_ml(shear) == pytest.approx(0.024)
    assert affine_voxel_volume_ml(reflection) == pytest.approx(0.024)
    assert mask_volume_from_affine_ml(np.ones((1, 1, 2)), shear) == pytest.approx(0.048)


def test_metre_conversion_upstream_matches_millimetre_affine_volume():
    affine_m = np.diag([0.002, 0.003, 0.004, 1.0])
    affine_mm = affine_m.copy()
    affine_mm[:3, :] *= 1000.0

    assert affine_voxel_volume_ml(affine_mm) == pytest.approx(0.024)


@pytest.mark.parametrize(
    "affine",
    (
        np.eye(3),
        np.full((4, 4), np.nan),
        np.diag([1.0, 1.0, 0.0, 1.0]),
        np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [1.0, 0.0, 0.0, 1.0]]),
    ),
)
def test_invalid_affine_volume_inputs_are_rejected(affine):
    with pytest.raises(ValueError):
        affine_voxel_volume_ml(affine)


def test_one_thousand_unit_voxels_equal_one_ml():
    mask = np.ones((10, 10, 10), dtype=np.uint8)

    assert mask_volume_ml(mask, [1, 1, 1]) == 1.0


def test_doubling_one_spacing_dimension_doubles_volume():
    mask = np.ones((2, 3, 4), dtype=np.uint8)

    baseline = mask_volume_ml(mask, [1, 1, 1])
    doubled = mask_volume_ml(mask, [2, 1, 1])

    assert doubled == 2 * baseline


def test_empty_mask_has_zero_volume():
    assert mask_volume_ml(np.zeros((2, 2, 2)), [1, 1, 1]) == 0.0


@pytest.mark.parametrize("value", [0.01, 0.5, -1, 2, np.nan])
def test_ambiguous_non_binary_mask_is_rejected(value):
    mask = np.zeros((2, 2, 2), dtype=float)
    mask[0, 0, 0] = value

    with pytest.raises(ValueError, match="binary values 0 and 1"):
        mask_volume_ml(mask, [1, 1, 1])
    with pytest.raises(ValueError, match="binary values 0 and 1"):
        masked_mean(np.ones_like(mask), mask)


def test_boolean_mask_is_accepted():
    mask = np.zeros((2, 2, 2), dtype=bool)
    mask[0, 0, 0] = True

    assert mask_volume_ml(mask, [1, 1, 1]) == 0.001
    assert masked_mean(np.ones_like(mask, dtype=float), mask) == 1.0


@pytest.mark.parametrize(
    "spacing",
    ([1, 1], [1, 1, 1, 1], [0, 1, 1], [-1, 1, 1], [np.nan, 1, 1], [np.inf, 1, 1]),
)
def test_invalid_spacing_is_rejected(spacing):
    with pytest.raises(ValueError):
        voxel_volume_ml(spacing)


def test_image_mask_shape_mismatch_is_rejected():
    with pytest.raises(ValueError, match="shapes differ"):
        masked_mean(np.zeros((2, 2, 2)), np.zeros((2, 2, 3)))


def test_masked_statistics_and_product_follow_generic_definitions():
    image = np.arange(8, dtype=float).reshape(2, 2, 2)
    mask = np.zeros_like(image, dtype=np.uint8)
    mask[0, 0, 1] = 1
    mask[1, 1, 1] = 1

    assert masked_mean(image, mask) == 4.0
    assert masked_max(image, mask) == 7.0
    assert uptake_volume_product(image, mask, [1, 1, 1]) == 0.008


@pytest.mark.parametrize("function", [masked_mean, masked_max])
def test_empty_masked_statistic_is_explicitly_undefined(function):
    with pytest.raises(ValueError, match="empty mask"):
        function(np.zeros((2, 2, 2)), np.zeros((2, 2, 2)))


def test_non_finite_foreground_image_value_is_rejected():
    image = np.ones((2, 2, 2))
    image[0, 0, 0] = np.nan
    mask = np.zeros_like(image)
    mask[0, 0, 0] = 1

    with pytest.raises(ValueError, match="finite"):
        masked_mean(image, mask)
