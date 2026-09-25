#!/usr/bin/env python3
from __future__ import annotations
import os,sys,time,subprocess,socket
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PY=sys.executable
CORE=[
 'audiencenet_runtime_test.py','ocr_timeout_test.py','engineering_benchmark.py','avixa_baseline_test.py',
 'adversarial_projection_benchmark.py','ablation_benchmark.py','fix_rescan_benchmark.py',
 'field_study_api_test.py','locked_evaluator_logic_test.py','final_verification.py'
]
SERVER_TESTS=['http_smoke_test.py','deck_api_test.py','observer_api_test.py']
BROWSER=['browser_main_e2e_test.py','browser_id_e2e_test.py','browser_validation_test.py','browser_field_study_test.py','browser_observer_test.py','presenter_mode_test.py']

def run(name,timeout=180):
    print(f'\n=== {name} ===',flush=True)
    subprocess.run([PY,str(ROOT/'tests'/name)],cwd=ROOT,check=True,timeout=timeout)

def wait_port(port,timeout=15):
    end=time.time()+timeout
    while time.time()<end:
        try:
            with socket.create_connection(('127.0.0.1',port),timeout=.5): return True
        except OSError: time.sleep(.15)
    return False

def main():
    for n in CORE: run(n,600)
    env=os.environ.copy();env['PORT']='8098';env['BACKROW_HOST']='127.0.0.1'
    server=subprocess.Popen([PY,str(ROOT/'server.py')],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    try:
        if not wait_port(8098): raise RuntimeError('BACKROW test server did not start')
        for n in SERVER_TESTS: run(n,180)
    finally:
        server.terminate()
        try: server.wait(5)
        except subprocess.TimeoutExpired: server.kill()
    if '--with-browser' in sys.argv:
        for n in BROWSER: run(n,240)
    print('\nBACKROW V11 verification PASS',flush=True)
if __name__=='__main__': main()
