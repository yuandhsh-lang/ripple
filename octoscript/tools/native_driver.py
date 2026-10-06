"""Drive only the native card-host instance explicitly named by --pid.
Uses documented Makepad remote routes; never invokes Splash handlers directly.
"""
import argparse, datetime, hashlib, json, pathlib, time, urllib.parse, urllib.request
ROOT = pathlib.Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / ".delivery-private/octoscript-migration"
BASE = "http://127.0.0.1:8141"
EVIDENCE.mkdir(parents=True, exist_ok=True)

def get(route, params=None):
    url = BASE + route + ("?" + urllib.parse.urlencode(params) if params else "")
    with urllib.request.urlopen(url, timeout=20) as response:
        raw = response.read()
    return json.loads(raw)

def snapshot():
    return get("/snap")

def log(action, detail, result):
    row = {"time": datetime.datetime.now(datetime.timezone.utc).isoformat(), "action": action, "detail": detail, "result": result}
    with (EVIDENCE / "actions.jsonl").open("a", encoding="utf-8") as target:
        target.write(json.dumps(row, ensure_ascii=False) + "\n")

def scroll(amount):
    result=get("/m", {"k":"scroll", "x":206, "y":700, "dy":amount, "wait":1})
    log("native scroll", amount, result)

def find(target, kind):
    for attempt in range(10):
        widgets=snapshot()["s"]
        matches=[w for w in widgets if w.get("ty")==kind and (w.get("t")==target or w.get("i")==target)]
        if not matches:
            scroll(-600 if attempt % 2 == 0 else 600)
            continue
        widget=matches[0]
        x,y,w,h=widget["r"]
        if y >= 35 and y+h <= 875:
            return widget
        scroll(400 if y+h>875 else -500)
    raise RuntimeError("Control could not be reached by scrolling: "+target)

def click(target):
    w=find(target, "Button")
    x,y,width,height=w["r"]
    result=get("/click", {"x":x+width/2,"y":y+height/2,"wait":1})
    log("native click",target,result)

def text(target,value):
    w=find(target, "TextInput")
    x,y,width,height=w["r"]
    get("/click", {"x":x+width-15,"y":y+height/2,"wait":1})
    get("/k", {"k":"down","c":"End","wait":1})
    for _ in range(len(w.get("t",""))+2):
        get("/k", {"k":"down","c":"Backspace","wait":1})
    result=get("/t", {"t":value,"wait":1})
    current=next(w for w in snapshot()["s"] if w.get("ty")=="TextInput" and w.get("i")==target)
    if current.get("t")!=value:
        raise AssertionError("Native text entry mismatch: "+repr(current))
    log("native type",{"field":target,"value":value},result)

def capture_state(name):
    d=snapshot()
    (EVIDENCE/("snap-"+name+".json")).write_text(json.dumps(d,ensure_ascii=False),encoding="utf-8")
    calendar=ROOT/"octoscript/.local-state/ripple/schedule.txt"
    state={"name":name,"calendar_exists":calendar.exists(),"record":calendar.read_text() if calendar.exists() else None,"sha256":hashlib.sha256(calendar.read_bytes()).hexdigest() if calendar.exists() else None}
    (EVIDENCE/("state-"+name+".json")).write_text(json.dumps(state),encoding="utf-8")
    log("observed state",name,state)
    visible=[{"ty":w.get("ty"),"t":w.get("t"),"r":w.get("r")} for w in d["s"] if w.get("ty") in ("Label","Button","TextInput")]
    print(json.dumps({"state":state,"widgets":visible},ensure_ascii=False))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pid",type=int,required=True)
    p.add_argument("action",choices=["click","text","scroll","state"])
    p.add_argument("target")
    p.add_argument("value",nargs="?")
    args=p.parse_args()
    identity=get("/s")
    if identity.get("pid")!=args.pid or identity.get("app")!="card-host.exe":
        raise RuntimeError("Bridge is not the explicitly owned instance: "+repr(identity))
    if args.action=="click":click(args.target)
    elif args.action=="text":text(args.target,args.value)
    elif args.action=="scroll":scroll(float(args.target))
    else:capture_state(args.target)
if __name__=="__main__":main()
