"""Compare recorded real Agent choices to the earliest SAME returned candidate."""
import json
import sys
from pathlib import Path
import host
from host import v
v.check_test_isolation()
audit=v.R/'soak-business-apps/ripple/agent-audit.log'
contexts={};searches={};rows=[]
decoder=json.JSONDecoder()
for line in audit.read_text(encoding='utf-8').splitlines():
    at=float(line.split(' ',1)[0])
    if ' name=ripple.context.read result=' in line:
        value=json.loads(line.split(' result=',1)[1]);contexts[value['task_id']]=value
    elif ' name=ripple.slots.search result=' in line:
        value=json.loads(line.split(' result=',1)[1]);searches[value['search_id']]=(at,value)
    elif ' MODEL_CHOICE ' in line:
        tail=line.split(' text=',1)[1]
        try:choice,end=decoder.raw_decode(tail)
        except ValueError:
            rows.append({'at':at,'valid_json':False,'raw_evidence_line':line});continue
        row={'at':at,'choice':choice,'verdict':tail[end:].strip(),'user_availability':'NOT VERIFIED','user_usefulness':'BLOCKED_NO_INDEPENDENT_USER'}
        if choice.get('decision')=='PROPOSE' and choice.get('search_id') in searches:
            search_at,search=searches[choice['search_id']];ctx=contexts[choice['task_id']]
            candidates=search['candidates'];earliest=min(candidates,key=lambda r:r['start'])
            selected=next((x for x in candidates if x['candidate_id']==choice['candidate_id']),None)
            row.update(context=ctx,search=search,selected=selected,rule_earliest=earliest,
                       legal_returned_id=selected is not None,
                       same_as_earliest=selected==earliest,
                       post_search_wait_seconds=at-search_at,
                       same_weather_revision=search['weather_revision']==ctx['weather_revision'])
        rows.append(row)
proposals=[r for r in rows if 'same_as_earliest' in r]
result={'classification':'REAL_MODEL_CHOICES_VS_EARLIEST_OF_IDENTICAL_RECORDED_CANDIDATES_NO_NEW_SEARCH_ALGORITHM','host':host.host,'source_sha256':v.sha(v.R/'soak-signed-bundle/main.splash'),'audit_path':str(audit),'audit_sha256':v.sha(audit),'rows':rows,'proposal_count':len(proposals),'same_as_earliest_count':sum(r['same_as_earliest'] for r in proposals),'legal_id_count':sum(r['legal_returned_id'] for r in proposals),'observable_user_benefit':'NOT VERIFIED','independent_user_trial':'BLOCKED','causal_speed_benchmark':'NOT RUN; only observed post-search waiting is reported'}
v.save(sys.argv[1],result)
print(json.dumps({k:x for k,x in result.items() if k!='rows'},ensure_ascii=False))
