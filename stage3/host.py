"""Use the existing guarded native driver with explicit stage-3 host/bundle pins."""
import os
import json
import sys
from pathlib import Path
WORK = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(WORK/'stage2'))
import run
v=run.v
if not os.environ['RIPPLE_TEST_RUN'].startswith('p3-'):
    raise RuntimeError('Only fresh stage-3 runs are allowed.')
host=os.environ.get('RIPPLE_STAGE3_HOST','rc2')
if host not in {'rc2','rc6'}: raise RuntimeError('Unknown pinned host')
v.RC2=WORK/('phase1/runtime/rc2' if host=='rc2' else 'stage3/runtime/rc6-extracted')
v.PORT=int(os.environ.get('RIPPLE_STAGE3_PORT','8173'))
if os.environ.get('RIPPLE_STAGE3_BASELINE')=='1': v.ROOT=WORK/'stage3/runtime/baseline'
original_save=v.save
def save(name,data):
    if isinstance(data,dict):
        data=dict(data,stage3_host=host)
        if host=='rc6' and data.get('classification')=='REAL_DEEPSEEK_MODEL_OFFICIAL_RC2_WITH_LIVE_WEATHER':
            data['classification']='REAL_DEEPSEEK_MODEL_OFFICIAL_RC6_WITH_LIVE_WEATHER'
        if data.get('classification','').endswith('_WITH_LIVE_WEATHER'):
            forecast=v.R/'soak-business-apps/ripple/weather.json'
            if forecast.exists() and json.loads(forecast.read_text())['source']=='FIXTURE':
                data['classification']=data['classification'].replace('_WITH_LIVE_WEATHER','_WITH_EXPLICIT_FIXTURE_WEATHER')
    return original_save(name,data)
v.save=save
if __name__=='__main__':
    mode=sys.argv[1]
    v.check_test_isolation()
    if mode=='prepare':v.prepare('soak-')
    elif mode=='start':v.start(sys.argv[2],reuse='--reuse' in sys.argv,no_provider='--no-provider' in sys.argv,revision='soak-')
    elif mode=='snap':v.snap(sys.argv[2])
    elif mode=='click':v.click(sys.argv[2])
    elif mode=='request':print(v.request(sys.argv[2]).decode())
