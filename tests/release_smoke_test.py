from __future__ import annotations
import argparse, hashlib, json, subprocess, sys, tempfile, zipfile
from pathlib import Path

def run(z:Path,out_path:Path):
    z=z.resolve();assert z.exists()
    sha=hashlib.sha256(z.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='backrow-release-') as td:
        td=Path(td)
        with zipfile.ZipFile(z) as f:
            bad=[x for x in f.namelist() if x.startswith('/') or '..' in Path(x).parts]
            assert not bad,bad;f.extractall(td)
        roots=[p for p in td.iterdir() if p.is_dir()];root=roots[0] if len(roots)==1 else td
        assert (root/'VERSION.txt').read_text().strip()=='11.0.0'
        assert not list(root.rglob('__pycache__'));assert not list(root.rglob('*.pyc'))
        assert not (root/'models/audiencenet_v1.json').exists()
        for req in ['locale.js','observer.html','observer.js','BACKROW_YCWC_2026_PRESENTATION_ID.pptx','docs/PRESENTATION_SCRIPT_ID.md','docs/Q_AND_A_DEFENSE_ID.md','docs/V11_DELTA.md','present.html','present.js','present.css','docs/AUTO_PRESENTATION.md','docs/NARRATION_EN.md','docs/NARRATION_ID.md','preview_v11/BACKROW_V11_VISUAL_REHEARSAL.mp4']:
            assert (root/req).exists(),req
        assert not list((root/'data/field_studies').glob('*.json')) if (root/'data/field_studies').exists() else True
        checks=[
            ('audiencenet_runtime','tests/audiencenet_runtime_test.py',60),
            ('fix_rescan','tests/fix_rescan_benchmark.py',90),
            ('field_study_api','tests/field_study_api_test.py',90),
            ('indonesian_browser','tests/browser_id_e2e_test.py',180),
            ('observer_browser','tests/browser_observer_test.py',120),
            ('locked_evaluator_logic','tests/locked_evaluator_logic_test.py',90),
            ('presenter_mode','tests/presenter_mode_test.py',120),
        ]
        passed={}
        for name,script,timeout in checks:
            subprocess.run([sys.executable,script],cwd=root,check=True,timeout=timeout,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);passed[name]=True
        result={'ok':True,'zip':z.name,'sha256':sha,'version':'11.0.0','clean_extract':True,'no_cache_files':True,'no_stale_model':True,'no_participant_data':True,**passed}
    out_path.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('zip');ap.add_argument('--out',required=True);args=ap.parse_args();run(Path(args.zip),Path(args.out))
if __name__=='__main__':main()
