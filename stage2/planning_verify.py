"""Official RC6 Stage 2 test driver; synthetic activities, real provider/tools.

RIPPLE_STAGE2_AUDIT: new sibling _audits/Ripple/Stage2-* folder.
RIPPLE_TEST_RUN: fresh p4-stage2-* created with stage4/new_run.ps1.
DEEPSEEK_API_KEY is inherited only by the host process. Never serialize env.
The fresh profile refers to this env name; no existing profiles are copied.
All actions use the official Makepad control API, never host patches.
"""
import datetime as dt, json, os, sys, time, urllib.parse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'stage1'))
import verify as v

P=Path(__file__).resolve().parents[1]
A=Path(os.environ['RIPPLE_STAGE2_AUDIT']).resolve()
assert A.parent==(P.parent/'_audits/Ripple').resolve() and A.name.startswith('Stage2-')
run=os.environ['RIPPLE_TEST_RUN']
assert run.startswith('p4-stage2-') and all(c.islower() or c.isdigit() or c=='-' for c in run)
evidence=os.environ.get('RIPPLE_STAGE2_HOST_EVIDENCE','rc6-ai')
assert evidence.startswith('rc6-') and all(c.islower() or c.isdigit() or c=='-' for c in evidence)
v.R=P/'stage2/runtime/runs'/run;v.E=A/evidence;v.E.mkdir(exist_ok=True)
v.CORE=v.R/'kernel-core';v.RC2=P/'stage4/runtime/rc6';v.HUB=P/'stage4/runtime/hub.exe';v.PORT=8187
v.check_test_isolation()
PREFIX=os.environ.get('RIPPLE_STAGE2_REVISION','s2-')
assert PREFIX.startswith('s2-') and all(c.islower() or c.isdigit() or c=='-' for c in PREFIX)
APP=v.R/(PREFIX+'business-apps/ripple')

def snapshot():return json.loads(v.request('/snap'))['s']
def scroll(dy):v.request(f'/m?k=scroll&x=850&y=620&dy={dy}&wait=1')
def read(name):return json.loads((APP/name).read_text(encoding='utf-8'))
def record(label):v.snap(label);v.state(label,revision=PREFIX)
def wait_state(seconds=55):
 end=time.monotonic()+seconds
 terminal={'DRAFT_REVIEW','NEEDS_DETAILS','AWAITING_APPROVAL','PLAN_REVIEW','NO_CHANGE','NO_CANDIDATE','FAILED','CANCELLED','STALE','COMPLETED','PARTIAL'}
 while time.monotonic()<end:
  states=[x['t'] for x in snapshot() if x.get('ty')=='Label' and x.get('t') in terminal]
  if states:return states[0]
  time.sleep(.4)
 return 'RUNNING'

def capture(label):
 # Only this isolated test core's public protocol records, never profile secrets.
 app_session=read('agent-session.json');sid=app_session.get('session_id',app_session.get('id'))
 records=[];sources=[];audits=[]
 for p in (v.CORE/'profiles/_main/data/peers').glob('ripple-*/tool_audit.jsonl'):
  rows=[json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]
  if sid is None and rows:sid=rows[-1]['session_id']
  selected=[r for r in rows if r.get('session_id')==sid]
  if selected:audits.extend(selected);sources.append({'path':str(p),'sha256':v.sha(p)})
 for p in (v.CORE/'ui-protocol').rglob('ledger-*.log'):
  chosen=[]
  for line in p.read_text(encoding='utf-8').splitlines():
   try:r=json.loads(line)
   except ValueError:continue
   e=r.get('event',{});env=e.get('envelope',{})
   if e.get('session_id')!=sid:continue
   allowed={'tool_start','tool_end','assistant_persisted','turn_completed','turn_failed','turn_cancelled'}
   if env.get('payload',{}).get('type') in allowed or e.get('kind') in allowed or e.get('metadata',{}).get('kind')=='tool_completed':chosen.append(r)
  if chosen:records.extend(chosen);sources.append({'path':str(p),'sha256_at_capture':v.sha(p)})
 v.save(label+'-kernel.json',{'classification':'OFFICIAL_RC6_REAL_PROVIDER_ATTEMPT_SYNTHETIC_USER_TASK','at_utc':v.now(),'session':app_session,'tool_audits':audits,'selected_unmodified_records':records,'sources':sources})
 print(json.dumps({'session_id':sid,'tool_records':len(audits),'ledger_records':len(records)}))

if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='prepare':v.prepare(PREFIX)
 elif mode=='start':v.start(sys.argv[2],reuse='--reuse' in sys.argv,revision=PREFIX)
 elif mode=='snapshot':v.snap(sys.argv[2])
 elif mode=='record':record(sys.argv[2])
 elif mode=='request':print(v.request(sys.argv[2]).decode())
 elif mode=='click':v.click(sys.argv[2])
 elif mode=='enter':v.enter(sys.argv[2],sys.argv[3])
 elif mode=='scroll':scroll(int(sys.argv[2]))
 elif mode=='wait':print(wait_state())
 elif mode=='capture':capture(sys.argv[2])
