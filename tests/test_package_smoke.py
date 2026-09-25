from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

def test_core_modules_import_and_model_available():
    import audiencenet, vision_engine, physical_baseline
    model=audiencenet.get_model()
    assert model.available
    assert model.version=='AudienceNet-2.0.0'
    assert callable(vision_engine.analyze)
    assert physical_baseline.BDM_TABLE

def test_v11_runtime_assets_exist():
    required=['observer.html','observer.js','index.html','app.js','server.py','models/audiencenet_v2.json','VERSION.txt','present.html','present.js','present.css']
    assert all((ROOT/p).exists() for p in required)
    assert (ROOT/'VERSION.txt').read_text().strip()=='11.0.0'
