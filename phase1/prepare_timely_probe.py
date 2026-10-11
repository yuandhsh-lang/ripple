"""Move diagnostics after completion; never increase official execution budgets."""
import json,shutil
import converge as c
old=c.WORK/'phase1/probe-authority/bundle';out=c.WORK/'phase1/probe-authority-timely/bundle'
shutil.copytree(old,out)
s=(out/'main.splash').read_text(encoding='utf-8')
s=s.replace('    ui.call.set_text(last_call)\n    record_evidence("RECEIVED call_id=" + call_id + " tool=" + name + " request=" + request.to_json())\n','',1)
s=s.replace('    fs.write("authority-state.json", result.to_json())\n    mod.app_tools.complete(call_id, result)','    // Settle the actual read before optional quota-scanning diagnostic writes.\n    mod.app_tools.complete(call_id, result)\n    fs.write("authority-state.json", result.to_json())\n    ui.call.set_text(last_call)\n    record_evidence("RECEIVED call_id=" + call_id + " tool=" + name + " request=" + request.to_json())',1)
s=s.replace('ripple.context.read accepts only an empty object','ripple.context.read accepts only the active task_id')
(out/'main.splash').write_text(s,encoding='utf-8')
m=json.loads((out/'manifest.json').read_text());m['version']='0.1.5-phase1';(out/'manifest.json').write_text(json.dumps(m,indent=2))
c.save('timely-probe-prepared.json',{'at_utc':c.now(),'reason':'Actual real-model soak hit official Splash wall-time budget before complete; diagnostic storage writes moved after tool settlement.','official_budgets_changed':False,'previous_bundle_preserved':str(old),'new_bundle':str(out)})
