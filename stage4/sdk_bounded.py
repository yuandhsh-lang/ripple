"""At most three fresh whole-suite runs; record failures without retry inflation."""
import datetime,json,os,subprocess
from pathlib import Path
W=Path(__file__).resolve().parent.parent;E=W/'stage4/evidence'
summary=[]
for i in range(1,4):
    evidence=E/f'sdk-bounded-{i}';evidence.mkdir()
    env=os.environ.copy();env.update(MAKEPAD='headless',RIPPLE_TEST_ROOT=str(W),RIPPLE_TEST_EVIDENCE=str(evidence),CARGO_TARGET_DIR=str(W/'stage4/runtime/cargo-target'),RUST_BACKTRACE='full')
    cmd=['cargo','+1.97.1','test','--locked','--offline','--manifest-path','phase1/business-harness/Cargo.toml','--','--test-threads=1','--nocapture']
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (E/f'sdk-bounded-{i}.log').open('x',encoding='utf-8') as log:p=subprocess.run(cmd,cwd=W,env=env,stdout=log,stderr=subprocess.STDOUT)
    r={'command':cmd,'exit_code':p.returncode,'start_utc':start,'end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'evidence':str(evidence),'fixture_model':True,'fixture_weather':True,'RUST_BACKTRACE':'full'}
    with (E/f'sdk-bounded-{i}-command.json').open('x',encoding='utf-8') as f:json.dump(r,f,indent=2)
    summary.append(r);print('SDK bounded run',i,'exit',p.returncode,flush=True)
    # A compilation failure is not a runtime repeat; stop and diagnose it.
    if p.returncode and 'Running unittests' not in (E/f'sdk-bounded-{i}.log').read_text(encoding='utf-8',errors='replace'):break
with (E/'sdk-bounded-summary.json').open('x',encoding='utf-8') as f:json.dump(summary,f,indent=2)
raise SystemExit(0 if len(summary)==3 and all(r['exit_code']==0 for r in summary) else 1)
