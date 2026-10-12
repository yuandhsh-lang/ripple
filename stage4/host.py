"""Original host/guard driver with Stage 4 paths; no Provider profile copied."""
import os,sys,json
from pathlib import Path
WORK=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(WORK/'stage2'))
import run
v=run.v
assert os.environ['RIPPLE_TEST_RUN'].startswith('p4-')
host=os.environ['RIPPLE_STAGE4_HOST'];assert host in {'rc2','rc6'}
v.RC2=WORK/'stage4/runtime'/host;v.PORT=8183 if host=='rc2' else 8184
v.HUB=WORK/'stage4/runtime/hub.exe'
old_save=v.save
def save(name,data):
    if isinstance(data,dict):data=dict(data,stage4_host=host,stage4_real_model_called=False)
    old_save(name,data)
v.save=save
if __name__=='__main__':
    mode=sys.argv[1];v.check_test_isolation()
    if mode=='prepare':v.prepare('soak-')
    elif mode=='start':v.start(sys.argv[2],reuse='--reuse' in sys.argv,revision='soak-')
    elif mode=='snap':v.snap(sys.argv[2])
    elif mode=='click':v.click(sys.argv[2])
    elif mode=='request':print(v.request(sys.argv[2]).decode())
