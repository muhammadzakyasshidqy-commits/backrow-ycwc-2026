"""Source-only physical-geometry baseline for BACKROW.

This is NOT the AI. It encodes the public BDM minimum-element-height table
published with AVIXA's display-size guidance/calculator as a transparent
professional baseline. BACKROW compares this source-only baseline with what
the audience camera actually recovers.

Reference audited 2026-09-05:
https://store.avixa.org/CPBase__item?id=a13f200000C2iQeAAJ
Public BDM ratio table: https://new-warmup2.avixa.org/resources/display-image-size-calculators/learn-more-about-display-size
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

# (minimum viewing-distance / image-height ratio, exclusive upper ratio, minimum element height as % of image height)
BDM_TABLE = (
    (0.8, 1.0, 0.50),
    (1.0, 1.5, 0.75),
    (1.5, 2.0, 1.00),
    (2.0, 3.0, 1.50),
    (3.0, 4.0, 2.00),
    (4.0, 5.0, 2.50),
    (5.0, 6.0, 3.00),
    (6.0, 7.0, 3.50),
    (7.0, 8.0, 4.00),
    (8.0, 9.0, 4.50),
    (9.0, 10.0 + 1e-9, 5.00),
)


def _number(v) -> Optional[float]:
    try:
        x = float(v)
        return x if x > 0 else None
    except (TypeError, ValueError):
        return None


def bdm_required_percent(viewing_ratio: float) -> Optional[float]:
    """Return public BDM minimum element-height percentage for the table range.

    We intentionally do not extrapolate outside the published table. A caller
    receives None instead of a made-up requirement.
    """
    r = _number(viewing_ratio)
    if r is None:
        return None
    for lo, hi, pct in BDM_TABLE:
        if lo <= r < hi:
            return pct
    return None


def evaluate_region(box, source_shape, room_config=None):
    """Evaluate a source text region against optional physical room geometry.

    room_config: {farthest_seat_m, image_height_m}. The result is an auditable
    source-only baseline; it must not be interpreted as human ground truth.
    """
    room_config = room_config or {}
    distance = _number(room_config.get('farthest_seat_m'))
    image_height_m = _number(room_config.get('image_height_m'))
    hsrc = int(source_shape[0]) if source_shape is not None else 0
    try:
        region_h = max(0, int(box[3]))
    except Exception:
        region_h = 0
    element_pct = (region_h / hsrc * 100.0) if hsrc > 0 else 0.0
    out = {
        'available': False,
        'standard_baseline': 'AVIXA BDM public display-size geometry table',
        'scope': 'source geometry only; not AI; not human ground truth',
        'actual_element_height_pct': round(element_pct, 3),
    }
    if distance is None or image_height_m is None:
        out['reason'] = 'Room geometry not supplied.'
        return out
    ratio = distance / image_height_m
    required = bdm_required_percent(ratio)
    out.update({
        'farthest_seat_m': round(distance, 3),
        'image_height_m': round(image_height_m, 3),
        'viewing_ratio': round(ratio, 3),
        'minimum_element_height_pct': required,
    })
    if required is None:
        out['reason'] = 'Viewing ratio is outside the public BDM table range (0.8–10.0); BACKROW refuses to extrapolate.'
        return out
    out['available'] = True
    margin = element_pct - required
    ratio_to_min = element_pct / required if required > 0 else None
    out['margin_pct_points'] = round(margin, 3)
    out['ratio_to_minimum'] = round(ratio_to_min, 3) if ratio_to_min is not None else None
    # Borderline is deliberately conservative so source geometry does not look more certain than it is.
    if ratio_to_min is not None and ratio_to_min >= 1.15:
        status = 'meets'
    elif ratio_to_min is not None and ratio_to_min >= 1.0:
        status = 'borderline'
    else:
        status = 'below'
    out['status'] = status
    out['recommended_scale_factor'] = round(max(1.0, (required * 1.15) / max(element_pct, 1e-6)), 2)
    return out
