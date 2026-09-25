"""Optional human-grounded calibration layer for BACKROW.

No field-calibrator model is bundled until a locked real-projector / naïve-reader
study contains enough independent observations. The runtime therefore fails
closed to `available=False` rather than inventing human-readability numbers.
"""
from __future__ import annotations
import json, math, os
import numpy as np

ROOT = os.path.abspath(os.path.dirname(__file__))
DEFAULT_PATH = os.path.join(ROOT, 'models', 'field_calibrator.json')
FEATURE_NAMES = [
    'camera_confidence', 'text_similarity', 'sharpness_ratio', 'contrast_ratio',
    'glare_fraction', 'dark_fraction', 'structure_corr', 'edge_ratio',
    'audiencenet_supported', 'audiencenet_watch', 'audiencenet_at_risk',
    'bdm_ratio_to_minimum', 'numeric_critical'
]


def make_features(recog, metrics, audiencenet, physical_baseline, expected=''):
    p=(audiencenet or {}).get('probabilities') or {}
    bdm=(physical_baseline or {}).get('ratio_to_minimum')
    try: bdm=float(bdm)
    except (TypeError, ValueError): bdm=1.0
    import re
    numeric_critical=1.0 if re.search(r'\d', expected or '') else 0.0
    vals={
        'camera_confidence':float((recog or {}).get('confidence',0))/100.0,
        'text_similarity':float((recog or {}).get('similarity',0)),
        'sharpness_ratio':float((metrics or {}).get('sharpness_ratio',0)),
        'contrast_ratio':float((metrics or {}).get('contrast_ratio',0)),
        'glare_fraction':float((metrics or {}).get('glare_fraction',0)),
        'dark_fraction':float((metrics or {}).get('dark_fraction',0)),
        'structure_corr':float((metrics or {}).get('structure_corr',0)),
        'edge_ratio':float((metrics or {}).get('edge_ratio',0)),
        'audiencenet_supported':float(p.get('supported',0)),
        'audiencenet_watch':float(p.get('watch',0)),
        'audiencenet_at_risk':float(p.get('at_risk',0)),
        'bdm_ratio_to_minimum':float(max(0,min(4,bdm))),
        'numeric_critical':numeric_critical,
    }
    return np.array([vals[n] for n in FEATURE_NAMES],dtype=np.float64), vals


class FieldCalibrator:
    def __init__(self,path=DEFAULT_PATH):
        self.path=path; self.available=False; self.version='not-trained'; self.metadata={}
        self.mean=None; self.scale=None; self.coef=None; self.intercept=0.0
        if not os.path.exists(path):
            self.metadata={'reason':'No human-grounded field calibrator has been trained yet.'}
            return
        try:
            with open(path,'r',encoding='utf-8') as f: d=json.load(f)
            if d.get('feature_names') != FEATURE_NAMES: raise ValueError('feature schema mismatch')
            self.mean=np.asarray(d['scaler']['mean'],dtype=float)
            self.scale=np.asarray(d['scaler']['scale'],dtype=float)
            self.coef=np.asarray(d['coef'],dtype=float)
            self.intercept=float(d['intercept'])
            if len(self.coef)!=len(FEATURE_NAMES): raise ValueError('weight count mismatch')
            self.version=d.get('version','field-calibrator')
            self.metadata=d.get('metadata',{})
            self.available=True
        except Exception as e:
            self.available=False; self.metadata={'reason':f'Field calibrator could not be loaded: {e}'}
    def predict_recovery(self,x):
        if not self.available: return None
        x=np.asarray(x,dtype=float)
        z=(x-self.mean)/np.where(self.scale==0,1,self.scale)
        logit=float(np.dot(self.coef,z)+self.intercept)
        p=1.0/(1.0+math.exp(-max(-30,min(30,logit))))
        return {'human_recovery_probability':p,'human_risk_probability':1-p,'version':self.version,'scope':'trained only from locked real-projector naïve-reader labels'}

_MODEL=None
def get_field_calibrator():
    global _MODEL
    if _MODEL is None: _MODEL=FieldCalibrator()
    return _MODEL
