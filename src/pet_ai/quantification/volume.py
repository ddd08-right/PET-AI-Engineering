"""Physical volume calculations for three-dimensional masks."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def _validated_spacing(spacing_mm: Sequence[float]) -> np.ndarray:
    spacing = np.asarray(spacing_mm, dtype=float)
    if spacing.shape != (3,):
        raise ValueError("spacing_mm must contain exactly three values in D, H, W order")
    if not np.all(np.isfinite(spacing)):
        raise ValueError("spacing_mm values must be finite")
    if np.any(spacing <= 0):
        raise ValueError("spacing_mm values must be strictly positive")
    return spacing


def _validated_binary_mask(mask: np.ndarray) -> np.ndarray:
    """Return a 3D boolean mask after rejecting ambiguous non-binary values."""
    array = np.asarray(mask)
    if array.ndim != 3:
        raise ValueError("mask must be a 3D array")
    if not np.all((array == 0) | (array == 1)):
        raise ValueError("mask must be boolean or contain only binary values 0 and 1")
    return array.astype(bool, copy=False)


def voxel_volume_ml(spacing_mm: Sequence[float]) -> float:
    """Return voxel volume from orthogonal-axis spacing in millimetres.

    Spacing alone cannot represent shear. Use :func:`affine_voxel_volume_ml`
    when a full image affine is available.
    """
    spacing = _validated_spacing(spacing_mm)
    return float(np.prod(spacing) / 1000.0)


def affine_voxel_volume_ml(affine_mm: np.ndarray) -> float:
    """Return voxel volume from a 4x4 voxel-to-millimetre affine.

    Reflections are valid and produce a positive volume. Unit validation and
    anatomical alignment remain responsibilities of the image-level caller.
    """
    affine = np.asarray(affine_mm, dtype=float)
    if affine.shape != (4, 4):
        raise ValueError("affine_mm must be a 4x4 matrix")
    if not np.all(np.isfinite(affine)):
        raise ValueError("affine_mm must contain only finite values")
    if not np.allclose(affine[3], [0.0, 0.0, 0.0, 1.0], atol=1e-8, rtol=0):
        raise ValueError("affine_mm must have a valid homogeneous final row")
    determinant = float(np.linalg.det(affine[:3, :3]))
    if abs(determinant) <= np.finfo(float).eps:
        raise ValueError("affine_mm linear transform must be non-degenerate")
    return abs(determinant) / 1000.0


def mask_volume_ml(mask: np.ndarray, spacing_mm: Sequence[float]) -> float:
    """Return generic binary-mask volume in mL; an empty mask has volume 0.0 mL."""
    array = _validated_binary_mask(mask)
    return float(np.count_nonzero(array) * voxel_volume_ml(spacing_mm))


def mask_volume_from_affine_ml(mask: np.ndarray, affine_mm: np.ndarray) -> float:
    """Return binary-mask volume using a validated millimetre affine."""
    array = _validated_binary_mask(mask)
    return float(np.count_nonzero(array) * affine_voxel_volume_ml(affine_mm))
