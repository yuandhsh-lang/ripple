"""Recompute Stage 3 pairs read-only; do not replay past activities or model calls."""
import hashlib,json
from pathlib import Path
W=Path(__file__).resolve().parent.parent;S=Path('F:/CodexWorkspace/Projects/RipplePhase1-20261010');E=W/'stage4/evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[];runs=[]
assert sha(W/'stage1/bundle/main.splash')==sha(S/'stage1/bundle/main.splash')
for run in ['p3-rc2-after-01','p3-rc6-after-01']:
    p=S/'stage2/evidence/runs'/run/'ai-vs-rule.json';data=json.loads(p.read_text(encoding='utf-8'))
    audit=Path(data['audit_path']);assert sha(audit)==data['audit_sha256']
    assert data['source_sha256']==sha(W/'stage1/bundle/main.splash')
    batch=[]
    for index,r in enumerate(data['rows']):
        if 'same_as_earliest' not in r:continue
        candidates=r['search']['candidates'];a=min(candidates,key=lambda x:x['start'])
        selected=[x for x in candidates if x['candidate_id']==r['choice']['candidate_id']]
        b=selected[0] if len(selected)==1 else None
        bounds=r['search']['constraints'];ctx=r['context']
        legal=b is not None and b['start']>=bounds['min_start'] and b['end']<=bounds['max_end'] and b['end']-b['start']==bounds['duration_seconds'] and all(b['checks'][k] for k in ['future','full_weather_coverage','weather_safe','time_bounds'])
        assert legal and ctx['weather_revision']==r['search']['weather_revision']
        batch.append({'source_row':index,'same_returned_candidate_set':True,'same_weather_revision':True,'candidate_set_sha256':hashlib.sha256(json.dumps(candidates,sort_keys=True).encode()).hexdigest(),'candidate_count':len(candidates),'candidate_start_span_seconds':max(c['start'] for c in candidates)-min(c['start'] for c in candidates),'legal_model_selection':legal,'model_equals_earliest':a==b,'observed_model_post_search_seconds':r['post_search_wait_seconds'],'rule_runtime_benchmark':'NOT MEASURED','real_user_constraints':'NOT RECORDED','user_acceptance':'USER_TRIAL_BLOCKED','user_usefulness':'NOT VERIFIED'})
    assert len(batch)==5
    runs.append({'source':str(p),'sha256':sha(p),'audit_sha256':sha(audit),'rows':batch});rows+=batch
result={'classification':'STAGE4_READ_ONLY_REANALYSIS_OF_STAGE3_REAL_MODEL_EVIDENCE_NOT_NEW_TRIALS','source_sha256':sha(W/'stage1/bundle/main.splash'),'paired_proposals':len(rows),'legal_count':sum(r['legal_model_selection'] for r in rows),'same_as_earliest':sum(r['model_equals_earliest'] for r in rows),'additional_value_demonstrated':False,'scope':'Existing selection observations only, not a causal benchmark or independent user evaluation','no_past_runtime_data_copied':True,'runs':runs}
with (E/'ai-existing-pairs-rechecked.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
print(json.dumps({k:v for k,v in result.items() if k!='runs'}))
