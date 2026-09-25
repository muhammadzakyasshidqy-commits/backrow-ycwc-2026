from __future__ import annotations
import json, math, os, re
import numpy as np

ROOT = os.path.abspath(os.path.dirname(__file__))
DEFAULT_MODEL = os.path.join(ROOT, 'models', 'audiencenet_v2.json')

# AudienceNet predicts projection/camera region signal survivability. It is deliberately
# separate from exact OCR recovery and from any future human-grounded field calibrator.
# Room features are physical geometry, not a claim that a camera equals human vision.
FEATURE_NAMES = [
    'structure_corr', 'contrast_ratio', 'sharpness_ratio', 'glare_fraction',
    'dark_fraction', 'edge_ratio', 'relative_text_height', 'source_confidence',
    'token_count', 'numeric_present', 'source_length_norm',
    'room_available', 'viewing_ratio_norm', 'bdm_ratio_to_minimum',
    'projected_region_height_mm_norm', 'visual_angle_arcmin_norm'
]

# Public AVIXA BDM source-geometry table mirrored here only to construct a learned
# feature. The final decision still keeps the transparent physical_baseline.py result
# separately visible to the user.
_BDM_TABLE = (
    (0.8, 1.0, 0.50), (1.0, 1.5, 0.75), (1.5, 2.0, 1.00),
    (2.0, 3.0, 1.50), (3.0, 4.0, 2.00), (4.0, 5.0, 2.50),
    (5.0, 6.0, 3.00), (6.0, 7.0, 3.50), (7.0, 8.0, 4.00),
    (8.0, 9.0, 4.50), (9.0, 10.000000001, 5.00),
)


def _softmax(z):
    z = np.asarray(z, dtype=np.float64)
    z = z - np.max(z)
    e = np.exp(z)
    return e / max(1e-12, float(np.sum(e)))


def _numbers(s: str):
    return re.findall(r'(?<![a-z])\d+(?:[.,]\d+)?%?(?![a-z])', (s or '').lower())


def _positive(v):
    try:
        x = float(v)
        return x if x > 0 else None
    except (TypeError, ValueError):
        return None


def _bdm_required_percent(viewing_ratio):
    r = _positive(viewing_ratio)
    if r is None:
        return None
    for lo, hi, pct in _BDM_TABLE:
        if lo <= r < hi:
            return pct
    return None


def room_geometry_features(box, source_shape, room_config=None):
    """Return bounded physical-geometry features.

    These are ordinary geometry, not human ground truth. `visual_angle_arcmin` is the
    angular height subtended by the source region using the supplied screen height and
    distance. It is useful input to a projection-survival model but is not interpreted as
    a medical eyesight threshold.
    """
    room_config = room_config or {}
    distance = _positive(room_config.get('farthest_seat_m'))
    image_height_m = _positive(room_config.get('image_height_m'))
    try:
        hsrc = max(1.0, float(source_shape[0]))
        region_h = max(0.0, float(box[3]))
    except Exception:
        hsrc, region_h = 1.0, 0.0
    element_frac = region_h / hsrc
    out = {
        'room_available': 0.0,
        'viewing_ratio_norm': 0.0,
        'bdm_ratio_to_minimum': 0.0,
        'projected_region_height_mm_norm': 0.0,
        'visual_angle_arcmin_norm': 0.0,
        'visual_angle_arcmin': None,
        'projected_region_height_mm': None,
    }
    if distance is None or image_height_m is None:
        return out
    ratio = distance / image_height_m
    required_pct = _bdm_required_percent(ratio)
    projected_h_m = image_height_m * element_frac
    angle_rad = 2.0 * math.atan2(projected_h_m, 2.0 * distance)
    arcmin = math.degrees(angle_rad) * 60.0
    actual_pct = element_frac * 100.0
    ratio_to_min = (actual_pct / required_pct) if required_pct else 0.0
    out.update({
        'room_available': 1.0,
        'viewing_ratio_norm': min(1.5, max(0.0, ratio / 10.0)),
        'bdm_ratio_to_minimum': min(2.5, max(0.0, ratio_to_min)) / 2.5,
        'projected_region_height_mm_norm': min(1.0, max(0.0, (projected_h_m * 1000.0) / 80.0)),
        'visual_angle_arcmin_norm': min(1.0, max(0.0, arcmin / 30.0)),
        'visual_angle_arcmin': arcmin,
        'projected_region_height_mm': projected_h_m * 1000.0,
    })
    return out


def make_feature_vector(expected, metrics, box, source_shape, source_confidence=100.0, room_config=None):
    hsrc, _ = source_shape[:2]
    _, _, _, h = box
    expected = expected or ''
    toks = re.findall(r'[A-Za-z0-9%]+', expected)
    room = room_geometry_features(box, source_shape, room_config)
    vals = {
        'structure_corr': max(0.0, float((metrics or {}).get('structure_corr', 0.0))),
        'contrast_ratio': min(2.0, max(0.0, float((metrics or {}).get('contrast_ratio', 0.0)))),
        'sharpness_ratio': min(2.0, max(0.0, float((metrics or {}).get('sharpness_ratio', 0.0)))),
        'glare_fraction': min(1.0, max(0.0, float((metrics or {}).get('glare_fraction', 0.0)))),
        'dark_fraction': min(1.0, max(0.0, float((metrics or {}).get('dark_fraction', 0.0)))),
        'edge_ratio': min(2.0, max(0.0, float((metrics or {}).get('edge_ratio', 0.0)))),
        'relative_text_height': min(0.20, max(0.0, h / max(1.0, float(hsrc)))) / 0.20,
        'source_confidence': min(1.0, max(0.0, float(source_confidence) / 100.0)),
        'token_count': min(20.0, float(len(toks))) / 20.0,
        'numeric_present': 1.0 if _numbers(expected) else 0.0,
        'source_length_norm': min(120.0, float(len(expected))) / 120.0,
        'room_available': room['room_available'],
        'viewing_ratio_norm': room['viewing_ratio_norm'],
        'bdm_ratio_to_minimum': room['bdm_ratio_to_minimum'],
        'projected_region_height_mm_norm': room['projected_region_height_mm_norm'],
        'visual_angle_arcmin_norm': room['visual_angle_arcmin_norm'],
    }
    return np.array([vals[n] for n in FEATURE_NAMES], dtype=np.float64), vals


class AudienceNet:
    """Compact custom MLP used as one learned evidence channel inside BACKROW.

    The bundled model is trained on a physics-aware procedural projection/camera
    survivability curriculum. It is *not* a human-readability model. Exact content loss
    is checked independently by OCR; a separate FieldCalibrator may only be enabled
    after real blinded projector/reader labels exist.
    """
    def __init__(self, path=DEFAULT_MODEL):
        self.path = path
        self.available = False
        self.error = None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                d = json.load(f)
            if d.get('feature_names') != FEATURE_NAMES:
                raise ValueError('AudienceNet feature schema mismatch')
            self.version = d['version']
            self.classes = d['classes']
            self.mean = np.array(d['scaler']['mean'], dtype=np.float64)
            self.scale = np.array(d['scaler']['scale'], dtype=np.float64)
            self.temperature = float(d.get('temperature', 1.0))
            self.layers = []
            for layer in d['layers']:
                self.layers.append((np.array(layer['weights'], dtype=np.float64),
                                    np.array(layer['bias'], dtype=np.float64),
                                    layer.get('activation', 'relu')))
            self.metadata = d.get('metadata', {})
            self.available = True
        except Exception as e:
            self.error = str(e)
            self.version = 'unavailable'
            self.classes = ['at_risk', 'supported', 'watch']
            self.metadata = {}

    def predict(self, feature_vector):
        if not self.available:
            return None
        x = np.asarray(feature_vector, dtype=np.float64)
        h = (x - self.mean) / np.where(np.abs(self.scale) < 1e-12, 1.0, self.scale)
        for i, (W, b, activation) in enumerate(self.layers):
            h = h @ W + b
            if i < len(self.layers) - 1:
                h = np.maximum(h, 0.0) if activation == 'relu' else np.tanh(h)
        probs = _softmax(h / max(1e-4, self.temperature))
        out = {c: float(p) for c, p in zip(self.classes, probs)}
        pred = max(out, key=out.get)
        return {'class': pred, 'confidence': float(out[pred]), 'probabilities': out,
                'version': self.version, 'temperature': self.temperature}

_MODEL = None


def get_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = AudienceNet()
    return _MODEL
