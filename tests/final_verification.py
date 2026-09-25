from __future__ import annotations
import hashlib, json, subprocess, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docs'


def load(name: str):
    return json.load(open(DOC / name, encoding='utf-8'))


def sha(path: Path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


# Parse/syntax closure for production + training modules used by the current release.
pyfiles = [
    'server.py','vision_engine.py','audiencenet.py','physical_baseline.py','field_calibrator.py',
    'generate_demo_assets.py','training/train_audiencenet.py','training/train_field_calibrator.py',
    'training/evaluate_locked_field_studies.py'
]
subprocess.run([sys.executable, '-m', 'py_compile', *pyfiles], cwd=ROOT, check=True, timeout=45)
for js in ['app.js','observer.js','study.js','study_admin.js','validate.js','present.js']:
    subprocess.run(['node', '--check', js], cwd=ROOT, check=True, timeout=30)

train = load('AUDIENCENET_TRAINING_REPORT.json')
ai = load('audiencenet_runtime_verification.json')
eng = load('engineering_runtime_verification.json')
http = load('http_smoke_verification.json')
deck = load('deck_api_verification.json')
avixa = load('avixa_baseline_verification.json')
adv = load('adversarial_projection_benchmark.json')
abl = load('ablation_benchmark.json')
fix = load('fix_rescan_verification.json')
field = load('field_study_api_verification.json')
bf = load('browser_field_study_verification.json')
lev = load('locked_evaluator_logic_verification.json')
bv5 = load('browser_main_e2e_verification.json')
bid = load('browser_id_e2e_verification.json')
bval = load('browser_validation_verification.json')
ui = load('ui_design_verification.json')
pres = load('PRESENTATION_VERIFICATION.json')
obs = load('observer_api_verification.json')
bobs = load('browser_observer_verification.json')
presenter = load('presenter_mode_verification.json')

critical = [
    'index.html','styles.css','app.js','locale.js','observer.html','observer.js','present.html','present.js','present.css','validate.html','validate.js',
    'study.html','study.js','study_admin.html','study_admin.js',
    'server.py','vision_engine.py','audiencenet.py','physical_baseline.py','field_calibrator.py',
    'README.md','requirements.txt','requirements-dev.txt','SETUP_WINDOWS.bat','RUN_WINDOWS.bat',
    'RUN_FIELD_STUDY_WINDOWS.bat','RUN_FIELD_STUDY_LINUX_MAC.sh','VERSION.txt','Dockerfile','.dockerignore',
    'models/audiencenet_v2.json','training/train_audiencenet.py','training/train_field_calibrator.py',
    'training/evaluate_locked_field_studies.py','assets/demo_deck.pdf','assets/hero_source_detail.png',
    'assets/hero_audience_detail.png','docs/MODEL_CARD.md','docs/DATASET_CARD.md','docs/BENCHMARK_REPORT.md',
    'docs/FIELD_TEST_PROTOCOL.md','docs/FIELD_STUDY_QUICKSTART.md','docs/FIELD_VALIDATION_QUICKSTART.md',
    'docs/FRONTIER_AI_BASELINE_PROTOCOL.md','docs/BASELINE_SUPREMACY.md','docs/COMPETITOR_BASELINES.md',
    'docs/Q_AND_A_DEFENSE.md','docs/FINAL_SCORECARD.md','docs/SOURCES_2026_09_10.md','docs/LICENSES.md',
    'docs/DEPLOYMENT.md','docs/ARCHITECTURE_ONE_PAGE.md','docs/EXPERIMENT_ONE_PAGE.md','docs/DEMO_SCRIPT.md',
    'docs/PRESENTATION_SCRIPT.md','docs/PRESENTATION_SCRIPT_ID.md','docs/V11_DELTA.md','docs/RULE_ALIGNMENT_2026.md','docs/LIVE_PRESENTATION_CUE_SHEET.md','docs/Q_AND_A_DEFENSE_ID.md','docs/FIELD_VALIDATION_QUICKSTART_ID.md','docs/SUBMISSION_CHECKLIST.md','docs/SUBMISSION_CHECKLIST_ID.md','docs/PRESENTATION_DEMO.md','docs/CONTROLLED_CLOSURE_MATRIX.md',
    'BACKROW_YCWC_2026_PRESENTATION.pptx','BACKROW_YCWC_2026_PRESENTATION_ID.pptx','build_presentation.js','docs/PRESENTATION_VERIFICATION.json'
]
for p in critical:
    assert (ROOT / p).exists(), p

procedural_adv_ok = all(x.get('ok') for x in adv['cases']) and all(adv['verified_properties'].values())
field_security_keys = [
    'participant_cannot_read_admin_api','raw_study_static_file_blocked','admin_token_required',
    'admin_token_not_exported','participant_submission_immutable','frozen_randomized_order',
    'timed_exposure_protocol','presenter_events_authorized_and_logged','response_roundtrip',
    'tiny_study_training_refused'
]
field_security_ok = all(field.get(k) for k in field_security_keys) and field.get('early_response_server_blocked') and field.get('public_exposure_completion_only')
match_pairs = [(x['expected'], x['matched']) for x in deck['auto_match']]

# Release tree may contain the empty data directory; it must not contain participant records.
field_dir = ROOT / 'data' / 'field_studies'
field_json_count = len(list(field_dir.glob('*.json'))) if field_dir.exists() else 0

# Stale model must be absent from a competition release tree.
stale_model_absent = not (ROOT / 'models' / 'audiencenet_v1.json').exists()

# Claim-discipline lint on current public copy/docs.
public_text = '\n'.join((ROOT / p).read_text(encoding='utf-8', errors='ignore') for p in [
    'README.md','index.html','app.js','docs/FINAL_SCORECARD.md','docs/MODEL_CARD.md','docs/Q_AND_A_DEFENSE.md'
])
forbidden_claims = ['world\'s first', '100% human accuracy', 'camera sees exactly what the human sees']
claim_lint = not any(x.lower() in public_text.lower() for x in forbidden_claims)

checks = {
    'syntax': True,
    'audiencenet_training': (
        train['version'] == 'AudienceNet-2.0.0'
        and train['samples'] == 1440
        and train['test_macro_f1'] > max(train['signal_baseline_macro_f1'], train['geometry_baseline_macro_f1'])
        and train['human_readability_claim'] is False
    ),
    'audiencenet_runtime': bool(ai['ok']) and ai['model'] == 'AudienceNet-2.0.0',
    'engineering_projection': eng['alignment_pass'] == eng['cases'] == 6 and eng['wrong_pair_reject'] == 2 and eng['numeric_demo'],
    'avixa_source_baseline': bool(avixa['ok']),
    'adversarial_projection': procedural_adv_ok,
    'learned_ablation': bool(abl['ok']) and abl['learned_channel_non_cosmetic']['pass'] and abl['direct_evidence_safety_override']['pass'] and abl['numeric_hard_guard']['pass'],
    'fix_rescan': fix['before']['at_risk'] >= 1 and fix['after']['at_risk'] == 0 and fix['after']['watch'] == 0 and fix['critical_threshold_recovered'],
    'http_security': bool(http['ok']) and http['invalid_input_rejected'] and http['path_traversal_rejected'] and http['csp'],
    'deck_auto_match': bool(deck['ok']) and match_pairs == [(0,0),(1,1),(2,2)],
    'field_study_protocol_security': bool(field['ok']) and field_security_ok and not field['participant_truth_leak'],
    'locked_evaluator_logic': bool(lev['ok']) and lev['perfect_gate_fixture_passed'] and lev['calibration_leakage_refused'] and lev['timed_exposure_enforced'],
    'browser_field_study': bool(bf['ok']) and bf['participant_truth_hidden'] and bf['admin_truth_available'] and bf['browser_response_flow'] and bf.get('reader_locked_until_exposure') and bf.get('pre_exposure_cue_without_live_overlay'),
    'browser_main': bool(bv5['ok']) and bv5['engine_ready'] and not bv5['desktop_horizontal_overflow'] and not bv5['mobile_horizontal_overflow'] and not bv5['pageerrors'] and 'AFTER 0 risk' in bv5['fix_rescan_delta'],
    'browser_indonesian': bool(bid['ok']) and bid['indonesian_main'] and bid['indonesian_validation'] and bid['indonesian_reader_truth_hidden'] and bid['indonesian_admin'] and not bid['pageerrors'],
    'browser_validation': bool(bval['ok']) and not bval['desktop_horizontal_overflow'] and not bval['mobile_horizontal_overflow'] and not bval['pageerrors'],
    'remote_observer_api': bool(obs['ok']) and obs['session_pairing'] and obs['six_digit_join'] and obs.get('pairing_code_single_use') and not obs['public_secret_leak'] and obs['admin_status_protected'] and obs['remote_slide_match'] == 2,
    'remote_observer_browser': bool(bobs['ok']) and bobs['pairing_ui'] and bobs['capture_ui'] and not bobs['mobile_overflow'] and bobs['bilingual'] and not bobs['pageerrors'],
    'ui_design': bool(ui['ok']) and not ui['desktop_horizontal_overflow'] and not ui['mobile_horizontal_overflow'] and not ui['decorative_gradients'] and ui['real_evidence_hero'],
    'release_data_clean': field_json_count == 0,
    'stale_model_absent': stale_model_absent,
    'claim_lint': claim_lint,
    'presentation_artifact': (bool(pres['ok']) and pres['slides'] == 10 and str(pres.get('english_overflow_test','')).startswith('PASS') and str(pres.get('indonesian_overflow_test','')).startswith('PASS') and str(pres.get('english_render_test','')).startswith('PASS') and str(pres.get('indonesian_render_test','')).startswith('PASS') and pres.get('version') == '11.0.0'),
    'presenter_mode': bool(presenter['ok']) and presenter['scenes']==7 and presenter['bilingual'] and presenter.get('external_voice_segments')==0 and presenter.get('local_voice_rehearsal') and presenter.get('paid_plugin_dependency') is False and not presenter['desktop_overflow'] and not presenter['mobile_overflow'] and not presenter['pageerrors'],
    'observer_stable_scan': bool(bobs.get('stable_scan_logic')) and bool(bobs.get('framing_guide')),
    'ocr_timeout_hardening': 'OCR_TIMEOUT_S=3.0' in (ROOT/'vision_engine.py').read_text(encoding='utf-8').replace(' ',''),
}
assert all(checks.values()), [k for k,v in checks.items() if not v]

out = {
    'generated_at': datetime.now(timezone(timedelta(hours=7))).isoformat(timespec='seconds'),
    'version': (ROOT / 'VERSION.txt').read_text().strip(),
    'all_internal_checks_pass': True,
    'checks': checks,
    'measured': {
        'audiencenet_scope': train['training_scope'],
        'audiencenet_samples': train['samples'],
        'audiencenet_test_macro_f1': train['test_macro_f1'],
        'signal_baseline_macro_f1': train['signal_baseline_macro_f1'],
        'geometry_baseline_macro_f1': train['geometry_baseline_macro_f1'],
        'human_readability_claim': False,
        'engineering_alignment': f"{eng['alignment_pass']}/{eng['cases']}",
        'wrong_pair_rejected': eng['wrong_pair_reject'],
        'engineering_median_analysis_s': eng['median_latency_s'],
        'judge_counts': ai['judge_counts'],
        'fix_rescan_before': fix['before'],
        'fix_rescan_after': fix['after'],
        'deck_matches_zero_based': match_pairs,
        'deck_match_only_ms': [x.get('match_only_ms') for x in deck['auto_match']],
        'field_study_protocol': {
            'truth_blinded': not field['participant_truth_leak'],
            'frozen_randomized_order': field['frozen_randomized_order'],
            'timed_exposure': field['timed_exposure_protocol'],
            'presenter_events_logged': field['presenter_events_authorized_and_logged'],
            'immutable_submission': field['participant_submission_immutable'],
        },
        'browser_main_screenshots': bv5['screenshots'],
        'browser_indonesian_screenshots': bid['screenshots'],
        'validation_screenshots': bval['screenshots'],
        'observer_screenshots': bobs['screenshots'],
        'presenter_scenes': presenter['scenes'],
    },
    'claim_boundary': (
        'BACKROW 11.0 is verified as a working AI-integrated audience-camera recoverability system with '
        'custom AudienceNet 2.0 procedural learned evidence, exact OCR/numeric evidence, page-index-free '
        'deck retrieval, physical-view rectification, conservative evidence fusion, remote audience-device pairing, repair/rescan, and '
        'blinded timed field-validation tooling. Procedural/model metrics are not human-readability accuracy.'
    ),
    'unresolved_external_empirical_gate': {
        'real_projector_naive_human_locked_field_test_complete': False,
        'manual_workflow_baseline_complete': False,
        'real_stable_frame_deck_match_target_complete': False,
        'locked_frontier_vlm_baseline_complete': False,
        'reason': (
            'These require a real projector/display, multiple physical rooms/positions, naïve readers, and '
            'external frontier-model runs on the frozen physical evidence. They are intentionally not fabricated.'
        ),
        'collector': 'study.html + study_admin.html + /api/study/*',
        'validation_console': 'validate.html',
        'protocol': 'docs/FIELD_TEST_PROTOCOL.md',
        'locked_evaluator': 'training/evaluate_locked_field_studies.py'
    },
    'critical_sha256': {p: sha(ROOT / p) for p in critical},
}
json.dump(out, open(DOC / 'FINAL_VERIFICATION.json','w'), indent=2)
print(json.dumps({
    'ok': True,
    'version': out['version'],
    'audiencenet_macro_f1_procedural': train['test_macro_f1'],
    'strongest_simple_baseline_macro_f1': max(train['signal_baseline_macro_f1'],train['geometry_baseline_macro_f1']),
    'judge_counts': ai['judge_counts'],
    'fix_after': fix['after'],
    'deck_matches': match_pairs,
    'field_protocol_v2': field_security_ok,
    'external_physical_gate_complete': False,
}, indent=2))
