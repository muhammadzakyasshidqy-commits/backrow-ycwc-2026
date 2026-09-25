#!/usr/bin/env python3
import numpy as np,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import vision_engine as ve

im=np.full((120,480,3),255,np.uint8)
old=ve.pytesseract.image_to_data
calls=[]
def boom(*args,**kwargs):
    calls.append(kwargs)
    raise RuntimeError('Tesseract process timeout')
ve.pytesseract.image_to_data=boom
try:
    try:
        ve.ocr_lines(im)
        raise AssertionError('source OCR timeout must fail closed')
    except ValueError as e:
        assert 'timed out' in str(e).lower()
    r=ve.recognize_expected_region(im,'2.5%')
    assert r['text']=='' and r['confidence']==0 and r['similarity']==0
    assert calls and all(abs(float(x.get('timeout',0))-ve.OCR_TIMEOUT_S)<1e-9 for x in calls)
finally:
    ve.pytesseract.image_to_data=old
print({'ok':True,'timeout_s':ve.OCR_TIMEOUT_S,'source_fail_closed':True,'region_fail_closed':True})
