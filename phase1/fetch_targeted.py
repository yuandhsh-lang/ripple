import concurrent.futures, hashlib, json, pathlib, urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
def get(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Ripple-Phase1-ReadOnly'}),timeout=60).read()
def download(item):
    url,out=item
    data=get(url)
    p=ROOT/out; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)
    return {'url':url,'local_path':out,'sha256':hashlib.sha256(data).hexdigest()}
if __name__=='__main__':
    items=[]
    repos={r:json.loads(get('https://api.github.com/repos/'+r+'/commits/HEAD'))['sha'] for r in ['OctoSense-org/OctoSense','OctoSense-org/OctoSense-App-Flow','OctoSense-org/OctoSense-App-Hub','gosimfoundation/hackathon-agenticapp26']}
    (ROOT/'sources'/'commits.json').write_text(json.dumps(repos,indent=2))
    paths={
      'OctoSense-org/OctoSense':['Cargo.toml','native-runtime.lock.json','crates/shell/src/host_tools/script_apps.rs','crates/shell/src/host_tools/relay.rs','crates/shell/src/apps.rs','crates/shell/src/octosense/paths.rs','crates/ai-host/src/contained.rs','crates/ai-host/src/lib.rs','crates/kernel/src/dirs.rs','crates/kernel/src/launch.rs','apps/news/bundle/manifest.json','apps/news/bundle/tools.json','docs/ai-services.md','docs/architecture.md'],
      'OctoSense-org/OctoSense-App-Flow':['AGENTS.md','docs/QUICKSTART.md','docs/AI-SERVICES.md','docs/HOST-API-V1.md','docs/CAPABILITIES.md','docs/PUBLISHING.md','docs/SCRIPT-API.md','docs/HOST-SERVICES.md','tools/octo','tools/octo_cli/cli.py'],
      'OctoSense-org/OctoSense-App-Hub':['AGENTS.md','SUBMITTING.md','Cargo.toml','crates/app-contract/Cargo.toml','crates/app-contract/src/agent.rs','crates/app-contract/src/manifest.rs','crates/app-contract/src/runtime.rs','crates/app-hub-app/src/runner.rs','docs/DEVELOPMENT.md'],
      'gosimfoundation/hackathon-agenticapp26':['README.md','docs/rules.md','docs/octosense-miniapps.md','docs/octosense-apps.md']}
    for repo,ps in paths.items():
        for path in ps:
            items.append((f'https://raw.githubusercontent.com/{repo}/{repos[repo]}/{path}','sources/'+repo.split('/')[-1]+'/'+path))
    release=json.loads(get('https://api.github.com/repos/OctoSense-org/OctoSense/releases/tags/desktop-v0.1.0-rc.2'))
    (ROOT/'sources'/'rc2-release.json').write_text(json.dumps(release,indent=2))
    for a in release['assets']:
        if a['name'] in ['RELEASE-NOTES.md','SHA256SUMS','RELEASE-PROVENANCE.json','OctoSense_0.1.0-rc.2.windows-acceptance.json','OctoSense_0.1.0-rc.2.windows-backend-acceptance.json','OctoSense_0.1.0-rc.2.sdk-discovery.json','OctoSense_0.1.0-rc.2_windows-x64.receipt.json']:
            items.append((a['browser_download_url'],'sources/'+a['name']))
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        jobs={pool.submit(download,i):i for i in items}
        for f in concurrent.futures.as_completed(jobs):
            try: results.append(f.result())
            except Exception as e: results.append({'url':jobs[f][0],'error':str(e)})
    (ROOT/'sources'/'TARGETED-INDEX.json').write_text(json.dumps(results,indent=2))
    for r in results:
        if 'error' in r: print('Unavailable:',r['url'],r['error'],flush=True)
    print('Targeted source collection:',len(results),'items',flush=True)
