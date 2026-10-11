import concurrent.futures,json,pathlib,sys
from fetch_targeted import download,get,ROOT
main=json.loads((ROOT/'sources'/'commits.json').read_text())
requests=[]
for repo, paths in {
 'OctoSense-org/OctoSense-App-Hub':['docs/SUBMITTING.md','docs/PUBLISHING.md','docs/HOST-API.md','crates/app-policy/src/agent.rs','crates/appstore/src/script_tools.rs','crates/appstore/src/script_tools_json.rs','crates/app-contract/src/host_api.rs'],
 'gosimfoundation/hackathon-agenticapp26':['AGENTS.md','src/main.ts','src/en.json','site.config.json'],
}.items():
    for p in paths: requests.append((f'https://raw.githubusercontent.com/{repo}/{main[repo]}/{p}','sources/'+repo.split('/')[-1]+'/'+p))
rc2='4ccf8e068399b1da139771a9ed94cef05fa6ae60'
paths=['AGENTS.md','Cargo.toml','Cargo.lock','native-runtime.lock.json','crates/shell/src/host_tools/script_apps.rs','crates/shell/src/apps.rs','crates/shell/src/lib.rs','crates/shell/src/dev_mode.rs','crates/ai-host/src/contained.rs','crates/ai-host/src/lib.rs','crates/kernel/src/dirs.rs','crates/kernel/src/launch.rs','tools/fixtures/host-api-lab/README.md','tools/fixtures/host-api-lab/bundle/manifest.json','tools/fixtures/host-api-lab/bundle/main.splash','tools/fixtures/host-api-lab/bundle/tools.json','desktop/scripts/host_api_lab.py','desktop/scripts/ai_providers_remote.sh']
for p in paths: requests.append((f'https://raw.githubusercontent.com/OctoSense-org/OctoSense/{rc2}/{p}','sources/RC2/'+p))
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    jobs={pool.submit(download,i):i for i in requests}
    for f in concurrent.futures.as_completed(jobs):
        try: results.append(f.result())
        except Exception as e: results.append({'url':jobs[f][0],'error':str(e)})
(ROOT/'sources'/'PINNED-INDEX.json').write_text(json.dumps(results,indent=2))
for r in results:
    if 'error' in r: print(r['url'],r['error'])
print('Pinned sources collected',len(results),flush=True)
