"""Minimal readonly candidate tool; never changes the frozen bundle/state machine."""
import json,re,shutil
import converge as c
old=c.WORK/'phase1/probe-authority-timely/bundle';out=c.WORK/'phase2/readonly-prep/bundle'
shutil.copytree(old,out)
base=(c.WORK/'bundle/main.splash').read_text(encoding='utf-8')
# Reuse original rain thresholds and overlap coverage; positive epoch math only.
rules=base[base.index('fn wet(h)'):base.index('fn alternative(s)')].replace('floor(', 'whole(')
s=(out/'main.splash').read_text(encoding='utf-8')
s=s.replace('let response_guard = "IDLE"','let response_guard = "IDLE"\nlet weather = []\nlet search_sequence = 0\nlet last_search = nil\nlet last_weather_fingerprint = nil')
s=s.replace('    let args = field(request, "args")','    let args = field(request, "args")',1)
s=s.replace('    if name != "ripple.context.read" {','    if name == "ripple.slots.search" { slots_tool(call_id, field(request, "args")) return }\n    if name != "ripple.context.read" {',1)
s=s.replace('    last_read = nil\n    busy = true','    last_read = nil last_search = nil\n    busy = true',1)
s += '\n'+rules+'\n'+(c.WORK/'phase1/authority/slots.splash').read_text(encoding='utf-8')
(out/'main.splash').write_text(s,encoding='utf-8')
m=json.loads((out/'manifest.json').read_text());m['version']='0.2.0-readonly-prep';m['integrity']={'bundle_blake3':''};(out/'manifest.json').write_text(json.dumps(m,indent=2))
t=json.loads((out/'tools.json').read_text())
t['tools'].append({'name':'ripple.slots.search','description':'Read-only deterministic candidate search over the current synthetic event and app-owned verified weather. At most three candidates; unknown, stale, mismatched weather is rejected. No personal-calendar free/busy claim, no schedule writes.','implemented_by':'app','risk':'read','private_data':False,'input_schema':{'type':'object','properties':{'task_id':{'type':'string','minLength':1,'maxLength':96},'read_token':{'type':'string','minLength':1},'min_start':{'type':'integer','minimum':0,'maximum':4102444799},'max_end':{'type':'integer','minimum':0,'maximum':4102444799},'max_candidates':{'type':'integer','minimum':1,'maximum':3}},'required':['task_id','read_token','min_start','max_end','max_candidates'],'additionalProperties':False},'output_schema':{'type':'object','properties':{'task_id':{'type':'string'},'search_id':{'type':'string'},'read_token':{'type':'string'},'context_revision':{'type':'integer'},'weather_revision':{'type':'string'},'weather_source':{'type':'string','enum':['LIVE','FIXTURE']},'weather_fetched_at':{'type':'number'},'expires_at':{'type':'number'},'calendar_source':{'type':'string','const':'SYNTHETIC'},'constraints':{'type':'object'},'candidates':{'type':'array','maxItems':3,'items':{'type':'object','properties':{'candidate_id':{'type':'string'},'start':{'type':'integer'},'end':{'type':'integer'},'time_authority':{'type':'object'},'checks':{'type':'object'}},'required':['candidate_id','start','end','time_authority','checks'],'additionalProperties':False}}},'required':['task_id','search_id','read_token','context_revision','weather_revision','weather_source','weather_fetched_at','expires_at','calendar_source','constraints','candidates'],'additionalProperties':False}})
(out/'tools.json').write_text(json.dumps(t,indent=2))
(out/'AGENT.md').write_text((old/'AGENT.md').read_text()+'\nCandidate preparation only: when explicitly asked for a bounded candidate search, first read context, then pass the actual read_token and explicit epoch constraints to ripple.slots.search. Never invent candidate IDs or weather facts. Candidate tools have no write capability. This probe has no approval/execution integration.\n')
c.save('slots-prepared.json',{'at_utc':c.now(),'classification':'UNPUBLISHED_READ_ONLY_PREPARATION','actual_model_two_tool_workflow':'NOT TESTED','existing_approval_state_machine_changed':False,'reused_functions':['wet','coverage'],'calendar_scope':'one synthetic target event only','bundle':str(out)})
