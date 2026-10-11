"""Fork the retained probe; no edits to previous versions or production bundle."""
import json
import shutil
from pathlib import Path
import converge as c

old=c.WORK/'phase1/probe-quota/bundle'
out=c.WORK/'phase1/probe-authority/bundle'
assert not out.exists()
shutil.copytree(old,out)
s=(out/'main.splash').read_text(encoding='utf-8')
s=s.replace('let busy = false','let busy = false\nlet task_generation = 0\nlet active_task = ""\nlet last_read = nil\nlet response_guard = "IDLE"',1)
authority=(c.WORK/'phase1/authority/time_and_guard.splash').read_text(encoding='utf-8')
s=s.replace('// Same record format',authority+'\n// Same record format',1)
s=s.replace('    for k v in args {\n        record_evidence("FAILED call_id=" + call_id + " invalid_args")', '    for k v in args {\n        if k == "task_id" { continue }\n        record_evidence("FAILED call_id=" + call_id + " invalid_args")',1)
s=s.replace('    let retrieved = time_now()', '    if !busy || field(args, "task_id") != active_task { mod.app_tools.fail(call_id, "stale_task: no active matching read task") return }\n    let fingerprint = schedule_fingerprint()\n    let task = active_task\n    let retrieved = time_now()',1)
s=s.replace('rev >= 0)', 'rev >= 0 && floor(rev) == rev && valid_epoch(s) && valid_epoch(e))',1)
s=s.replace('data_source: "ripple-sandbox-synthetic" retrieved_at: retrieved})','data_source: "ripple-sandbox-synthetic" retrieved_at: retrieved time_authority: authoritative_time(s, e)})',1)
s=s.replace('let result = {events: events retrieved_at: retrieved data_source: "ripple-sandbox-synthetic"}', 'let result = {task_id: task read_token: call_id events: events retrieved_at: retrieved data_source: "ripple-sandbox-synthetic"}\n    if task != active_task || fingerprint != schedule_fingerprint() { mod.app_tools.fail(call_id, "stale_context: task or schedule changed") return }',1)
s=s.replace('    mod.app_tools.complete(call_id, result)', '    last_read = {task_id: task read_token: call_id events: events fingerprint: fingerprint}\n    fs.write("authority-state.json", result.to_json())\n    mod.app_tools.complete(call_id, result)',1)
begin=s.index('fn ask(){')
end=s.index('\nui :=',begin)
s=s[:begin]+'''fn finish_model(generation, text){
    let verdict = validate_model_read(generation, text)
    if generation != task_generation || !busy { record_evidence(verdict) return }
    response_guard = verdict
    busy = false
    if verdict == "ACCEPTED: actual tool data only; no schedule was changed" {
        let result = {task_id: active_task task_generation: generation data_source: "AGENT" verified_events: last_read.events status: "READ_ONLY_COMPLETE"}
        fs.write("authority-turn.json", result.to_json())
        let shown = "No current events. SYNTHETIC / program time / no writes"
        if last_read.events.len() > 0 {
            let e = last_read.events[0]
            shown = "SYNTHETIC / epoch UTC: " + e.start + " - " + e.end + "\\nUTC+8: " + e.time_authority.start_utc8 + " - " + e.time_authority.end_utc8 + "\\nUTC: " + e.time_authority.start_utc + " - " + e.time_authority.end_utc
        }
        ui.authority_panel.set_text(shown)
    }
    record_evidence(verdict)
    ui.answer_panel.set_text(verdict)
}
fn interrupt_task(){
    abandon_task("CANCELLED: obsolete replies will be discarded")
    ui.answer_panel.set_text(response_guard)
    host.request("octos.turn.interrupt", {}, fn(r){ record_evidence("INTERRUPT reply=" + r.is_ok) })
}
fn ask(){
    if busy { record_evidence("DUPLICATE ANALYZE IGNORED") return }
    let id = "ripple-task-" + time_now() + "-" + (task_generation + 1)
    let generation = begin_task(id)
    status = response_guard ui.answer_panel.set_text(status)
    let deadline = 45
    // Operator-only fault setup. Never an Agent argument or Provider setting.
    if fs.exists("model-deadline-fixture.txt") {
        let requested = fs.read("model-deadline-fixture.txt").to_f64()
        if requested >= 0.2 && requested <= 45 { deadline = requested }
    }
    start_timeout(deadline, || {
        if busy && generation == task_generation {
            abandon_task("TIMEOUT: app request deadline; no schedule was changed")
            ui.answer_panel.set_text(response_guard)
            record_evidence(response_guard)
            host.request("octos.turn.interrupt", {}, fn(r){ record_evidence("TIMEOUT INTERRUPT=" + r.is_ok) })
        }
    })
    host.request("octos.session.open", {}, fn(s){
        if generation != task_generation || !busy { return }
        if !s.is_ok { busy = false status = "SESSION ERROR: " + s.error ui.answer_panel.set_text(status) return }
        fs.write("phase1-session.json", s.data.to_json())
        let text = ui.prompt.text() + "\\nRead task_id=" + id + ". Call ripple.context.read with this task_id. Return ONLY JSON with exactly task_id, read_token, event_id, revision copied from the actual tool result. For no events use null event_id and revision. Do not output or calculate dates or any other fields."
        host.request("octos.turn.start", {text: text trigger: "person" from: "Ripple isolated read task"}, fn(r){
            if generation != task_generation || !busy { record_evidence("DISCARDED obsolete MODEL callback") return }
            if r.is_ok { finish_model(generation, field(r.data, "text")) }
            else { busy = false status = "TURN ERROR: " + r.error record_evidence(status) ui.answer_panel.set_text(status) }
        })
    })
}
''' + s[end:]
s=s.replace('    call := Label', '    authority_panel := Label{width: Fill text: "Program time only / UTC and UTC+8 / no model date rendering" draw_text.color: ink draw_text.text_style.font_size: 13}\n    call := Label',1)
s=s.replace('on_click: || { host.request("octos.turn.interrupt", {}, fn(r){ status = "Interrupt reply: " + r.is_ok ui.answer_panel.set_text(status) }) }','on_click: || interrupt_task()',1)
s=s.replace('floor(', 'whole(')
(out/'main.splash').write_text(s,encoding='utf-8')
manifest=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
manifest['version']='0.1.4-phase1';manifest['integrity']={'bundle_blake3':''}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
tools=json.loads((out/'tools.json').read_text(encoding='utf-8'))
t=tools['tools'][0]
t['input_schema']={'type':'object','properties':{'task_id':{'type':'string','minLength':1,'maxLength':96}},'required':['task_id'],'additionalProperties':False}
event=t['output_schema']['properties']['events']['items']
event['properties']['time_authority']={'type':'object','properties':{k:{'type':'string'} for k in ['epoch_unit','display_zone','start_utc','end_utc','start_utc8','end_utc8']},'required':['epoch_unit','display_zone','start_utc','end_utc','start_utc8','end_utc8'],'additionalProperties':False}
event['required'].append('time_authority')
t['output_schema']['properties'].update({'task_id':{'type':'string'},'read_token':{'type':'string'}})
t['output_schema']['required']+=['task_id','read_token']
(out/'tools.json').write_text(json.dumps(tools,indent=2)+'\n',encoding='utf-8')
(out/'AGENT.md').write_text((old/'AGENT.md').read_text(encoding='utf-8')+'\nThe application supplies an active task_id. Pass it to ripple.context.read. Final answer MUST be raw JSON (no fences) with exactly task_id, read_token, event_id and revision copied from that tool result. For no events use null event_id and revision. Never compute dates or append explanations. The app displays only independently verified program timestamps. If a tool fails, report failure; never invent an acknowledgement.\n',encoding='utf-8')
c.save('authority-source-prepared.json',{'at_utc':c.now(),'version':'0.1.4-phase1','path':str(out),'previous_probes_modified':False,'model_text_rendered':False,'source_sha256':{p.relative_to(out).as_posix():c.sha(p) for p in out.rglob('*') if p.is_file()}})
print(out)
