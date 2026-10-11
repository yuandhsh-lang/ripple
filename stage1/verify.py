"""Isolated official RC2 rehearsal; no provider secrets or original data access.

The remote HTTP control surface is the official Makepad test API, not a service
added to Ripple. All snapshots and command failures are preserved under evidence.
"""
import datetime, hashlib, json, os, shutil, socket, subprocess, sys, tempfile, time
import urllib.parse, urllib.request
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent
WORK = ROOT.parent
E = ROOT / 'evidence'
R = ROOT / 'runtime'
PORT = 8165
HUB = WORK / 'phase1/toolchain/OctoSense-App-Hub/target/release/hub.exe'
RC2 = WORK / 'phase1/runtime/rc2'
CORE = WORK / 'phase1/runtime/kernel-core'

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, data):
    with (E / name).open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
def request(path, timeout=20):
    raw = urllib.request.urlopen(f'http://127.0.0.1:{PORT}{path}', timeout=timeout).read()
    with (E / 'actions.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps({'at_utc':now(),'path':path,'response_bytes':len(raw)},ensure_ascii=False)+'\n')
    return raw
def command(label, cmd, **kwargs):
    p = subprocess.run(list(map(str,cmd)),capture_output=True,text=True,encoding='utf-8',errors='replace',**kwargs)
    save(label+'.json', {'at_utc':now(),'command':list(map(str,cmd)),'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    if p.returncode: raise RuntimeError(p.stdout+p.stderr)
    return p.stdout.strip()

def prepare(revision=''):
    R.mkdir(exist_ok=bool(revision))
    mirror=R/(revision+'mirror');mirror.mkdir()
    main=R/(revision+'signed-bundle');shutil.copytree(ROOT/'bundle',main)
    bootstrap=R/(revision+'bootstrap-bundle');shutil.copytree(WORK/'phase1/baseline-bundle',bootstrap)
    p=bootstrap/'manifest.json';m=json.loads(p.read_text());m.update(id='stage1.bootstrap',name='Ripple test host bootstrap',integrity={'bundle_blake3':''});p.write_text(json.dumps(m,indent=2))
    # Ephemeral rehearsal signing identity only. Existing signing/Provider keys
    # are neither inspected nor modified. Private keys never enter bundle/Git.
    with tempfile.TemporaryDirectory(prefix='RippleStage1Rehearsal-') as tmp:
        keys=Path(tmp)
        anchor=command(revision+'local-anchor',['%s'%HUB,'keygen',keys/'anchor.key'])
        command(revision+'local-working',[HUB,'keygen',keys/'working.key'])
        signer=command(revision+'local-fixture',[HUB,'keygen',keys/'fixture.key'])
        cert=command(revision+'local-cert',[HUB,'certify','--anchor',keys/'anchor.key','--working',keys/'working.key'])
        for label,bundle in [('bootstrap',bootstrap),('stage1',main)]:
            command(revision+label+'-stamp',[HUB,'stamp',bundle])
            command(revision+label+'-sign',[HUB,'sign-manifest',bundle,'--key',keys/'fixture.key','--key-id','ripple-local-rehearsal'])
            command(revision+label+'-publish',[HUB,'publish',bundle,'--catalog',mirror/'catalog.json','--key',keys/'working.key','--anchor-cert',cert,'--publisher','ripple-local-rehearsal','--publisher-key','ripple-local-rehearsal='+signer,'--out',mirror,'--anchor',anchor])
        command(revision+'mirror-verify',[HUB,'verify',mirror/'catalog.json','--anchor',anchor])
    save(revision+'mirror-receipt.json',{'classification':'ISOLATED_LOCAL_REHEARSAL_NOT_RELEASE','mirror':str(mirror),'anchor_public_hex':anchor,'temporary_signing_identity_only':True,'existing_keys_modified':False,'source_hashes':{str(p.relative_to(main)):sha(p) for p in main.rglob('*') if p.is_file()}})

def check_test_isolation():
    allowed = WORK / 'stage2/runtime/runs'
    if not R.resolve().is_relative_to(allowed.resolve()) or R.resolve() == allowed.resolve():
        raise RuntimeError('Use stage2/run.py with a fresh RIPPLE_TEST_RUN; historical runtimes are read-only.')
    if R.resolve() != R.absolute() or CORE.resolve() != (R/'kernel-core').absolute():
        raise RuntimeError('Kernel core must belong to this run; no external paths or junctions.')
    marker = json.loads((R/'isolation.json').read_text(encoding='utf-8'))
    if marker != {'runtime_root':str(R.resolve()), 'core_dir':str(CORE.resolve()), 'provider_profile_only':True}:
        raise RuntimeError('Invalid test isolation marker.')

def check_remote_available():
    # Never attach test actions to another host already using this bridge.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as guard:
        if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
            guard.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        try: guard.bind(('127.0.0.1', PORT))
        except OSError as e: raise RuntimeError('Test control port is occupied; no host launched.') from e

def start(label, reuse=False, no_provider=False,revision=''):
    check_test_isolation()
    prefix=revision+('no-provider' if no_provider and not reuse else 'business')
    home=R/(prefix+'-home');apps=R/(prefix+'-apps')
    for path in [home, apps, CORE, R/'no-provider-core']:
        if not path.resolve().is_relative_to(R.resolve()) or path.resolve() != path.absolute():
            raise RuntimeError('Runtime roots must stay inside this run without symlinks/junctions.')
    check_remote_available()
    if not reuse: home.mkdir();apps.mkdir()
    receipt=json.loads((E/(revision+'mirror-receipt.json')).read_text())
    overrides={'OCTOSENSE_HOME':str(home),'OCTOSENSE_APP_DATA':str(apps),'OCTOS_APP_CORE_DIR':str(CORE) if not no_provider else str(R/'no-provider-core'),'OCTOSENSE_HUB_CATALOG':'legacy','OCTOSENSE_HUB':receipt['mirror'],'OCTOSENSE_HUB_ANCHOR':receipt['anchor_public_hex'],'MAKEPAD_REMOTE':str(PORT),'MAKEPAD_HIDE_WINDOWS':'1'}
    env={k:v for k,v in os.environ.items() if not k.startswith(('OCTOS','MAKEPAD','RINX_'))};env.update(overrides)
    with (E/(label+'-shell.log')).open('x',encoding='utf-8') as log:
        p=subprocess.Popen([str(RC2/'octosense.exe')],cwd=RC2,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    save(label+'-process.json',{'at_utc':now(),'pid':p.pid,'environment':overrides,'shell_sha256':sha(RC2/'octosense.exe'),'kernel_sha256':sha(RC2/'octos-kernel.exe'),'preopened_card':False})
    for _ in range(40):
        if p.poll() is not None: raise RuntimeError('Shell exited '+str(p.returncode))
        try: ready=json.loads(request('/s', timeout=1))
        except (OSError, ValueError): time.sleep(.25);continue
        if ready.get('pid') != p.pid:
            p.terminate()
            raise RuntimeError('Control API belongs to another PID; spawned test host stopped.')
        break
    else:
        p.terminate()
        raise RuntimeError('Test control API not ready; spawned test host stopped.')
    print('RC2 started',p.pid,PORT)

def snap(label):
    data=json.loads(request('/snap'))
    save(label+'.json',data)
    (E/(label+'.png')).write_bytes(request('/g?raw=1'))
    print(json.dumps([x for x in data['s'] if x.get('ty') in ['Button','Label']],ensure_ascii=False))
def click(label):
    until=time.monotonic()+12
    while True:
        data=json.loads(request('/snap'))
        matches=[x for x in data['s'] if x.get('ty')=='Button' and x.get('t')==label]
        if matches or time.monotonic()>until:break
        time.sleep(.3)
    if len(matches)!=1: raise RuntimeError((label,len(matches)))
    x,y,w,h=matches[0]['r'];print(request(f'/click?x={x+w/2}&y={y+h/2}&wait=1').decode())
def state(label,revision='v2-'):
    app=R/(revision+'business-apps/ripple')
    names=['schedule.txt','weather.json','execution.json','outcome.txt','agent-choice.json','agent-session.json','agent-audit.log']
    save(label+'-state.json',{'at_utc':now(),'files':{n:{'sha256':sha(app/n),'content':(app/n).read_text(encoding='utf-8')} for n in names if (app/n).exists()},'storage_bytes':sum(p.stat().st_size for p in app.rglob('*') if p.is_file())})
def enter(widget, text):
    data=json.loads(request('/snap'))
    matches=[x for x in data['s'] if x.get('ty')=='TextInput' and x.get('i')==widget]
    if len(matches)!=1:raise RuntimeError((widget,len(matches)))
    x,y,w,h=matches[0]['r'];request(f'/click?x={x+w/2}&y={y+h/2}&wait=1')
    request('/k?k=down&c=KeyA&ctrl=1')
    request('/k?k=up&c=KeyA&ctrl=1')
    request('/t?t='+urllib.parse.quote(text)+'&wait=1')
def capture(label, turn=None):
    # Only tool/turn records for Ripple's latest session; no credential stores.
    core=CORE
    audit_path=core/'profiles/_main/data/peers/ripple-22a12f906cd27b73/tool_audit.jsonl'
    audits=[json.loads(s) for s in audit_path.read_text(encoding='utf-8').splitlines() if s.strip()]
    last=next(a for a in reversed(audits) if turn is None or a['turn_id']==turn)
    session=last['session_id'];turn=last['turn_id']
    selected=[];sources=[]
    allowed={'tool_start','tool_end','assistant_persisted','turn_completed','turn_failed','turn_cancelled'}
    for p in (core/'ui-protocol').rglob('ledger-*.log'):
        chosen=[]
        for line in p.read_text(encoding='utf-8').splitlines():
            try:record=json.loads(line)
            except ValueError:continue
            event=record.get('event',{});env=event.get('envelope',{})
            if event.get('session_id')!=session or env.get('turn_id',event.get('turn_id'))!=turn:continue
            if env.get('payload',{}).get('type') in allowed or event.get('kind') in allowed or event.get('metadata',{}).get('kind')=='tool_completed':chosen.append(record)
        if chosen:selected.extend(chosen);sources.append({'path':str(p),'sha256_at_capture':sha(p)})
    save(label+'-kernel.json',{'at_utc':now(),'classification':'REAL_DEEPSEEK_MODEL_OFFICIAL_RC2_WITH_LIVE_WEATHER','session_id':session,'turn_id':turn,'sources':sources,'selected_unmodified_records':selected,'tool_audits':[a for a in audits if a['session_id']==session and a['turn_id']==turn]})
    print('Captured actual Kernel turn',turn)

if __name__=='__main__':
    mode=sys.argv[1]
    revision=sys.argv[sys.argv.index('--revision')+1] if '--revision' in sys.argv else ''
    if mode=='prepare':prepare(revision)
    elif mode=='start':start(sys.argv[2], '--reuse' in sys.argv, '--no-provider' in sys.argv,revision)
    elif mode=='snap':snap(sys.argv[2])
    elif mode=='click':click(sys.argv[2])
    elif mode=='state':state(sys.argv[2])
    elif mode=='enter':enter(sys.argv[2],sys.argv[3])
    elif mode=='capture':capture(sys.argv[2])
    elif mode=='request':print(request(sys.argv[2]).decode())
