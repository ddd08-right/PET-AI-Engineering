# PET Quantification Boundaries

The v0.3 utilities convert a three-dimensional binary mask into a generic
physical volume. For orthogonal voxel axes with spacing in `(D, H, W)` millimetres:

`voxel volume (mL) = spacing_D * spacing_H * spacing_W / 1000`

The division follows from `1000 mm^3 = 1 mL`. Spacing alone cannot represent a
sheared grid. When a validated voxel-to-millimetre affine is available, use
`abs(det(affine[:3, :3])) / 1000` mL instead. Mask volume is foreground voxel
count multiplied by voxel volume. Empty masks have volume `0.0 mL`. Spacing
must contain exactly three finite, strictly positive values. The array helper
validates numeric arguments only; it cannot validate NIfTI units, transform
provenance, or anatomical alignment. Those checks belong to the NIfTI geometry
and audit entry points.

Boolean masks are accepted. Integer and floating masks must contain only
explicit binary values `{0, 1}`. Probabilistic masks are rejected rather than
silently thresholded; threshold selection belongs upstream and must be explicit.

`masked_mean` and `masked_max` summarize finite image values inside a binary
mask. Both reject an empty mask because the statistic is undefined.
`uptake_volume_product` multiplies the generic masked mean by generic mask
volume and therefore has units of image-value times mL.

These names deliberately do not imply MTV, TLV, TMTV, or SUV. SUV terminology
is valid only when the PET image has already been correctly converted and
validated in SUV units. Study-specific biological or clinical interpretations
are NOT VERIFIED by these generic calculations.
