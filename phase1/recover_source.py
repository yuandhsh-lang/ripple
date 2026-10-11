"""Recover official Git blobs by verified content, never patch source or gates."""
import concurrent.futures, hashlib, json, os, subprocess, urllib.request, sys
import converge as c
env=os.environ.copy();env['GIT_NO_LAZY_FETCH']='1'
def git(*args,input=None):
    return subprocess.run(['git',*args],cwd=c.SRC,env=env,input=input,capture_output=True,check=True).stdout
tree=git('ls-tree','-rz',c.COMMITS[-1])
entries=[]
for raw in tree.split(b'\0'):
    if not raw: continue
    meta,path=raw.split(b'\t',1);mode,typ,sha=meta.decode().split()
    path=path.decode('utf-8')
    if typ!='blob' or path.startswith(('rom/','docs/','desktop/docs/','phone/docs/')): continue
    entries.append((sha,path))
check=git('cat-file','--batch-check',input=('\n'.join(s for s,p in entries)+'\n').encode()).decode().splitlines()
missing=[entry for entry,line in zip(entries,check) if line.endswith(' missing')]
prefix='retry-' if '--retry' in sys.argv else ''
c.save(prefix+'missing-source-blobs.json',{'selected_files':len(entries),'missing':missing,'verified_commit':c.COMMITS[-1]})
print('selected',len(entries),'missing',len(missing),flush=True)
def fetch(item):
    sha,path=item
    url='https://raw.githubusercontent.com/OctoSense-org/OctoSense/'+c.COMMITS[-1]+'/'+urllib.parse.quote(path)
    if prefix: url+='?verified_blob='+sha
    try:
        with urllib.request.urlopen(url,timeout=20) as r:data=r.read()
        assert len(data)<=32*1024*1024,'blob too large for this recovery'
        expected=hashlib.sha1(('blob '+str(len(data))+'\0').encode()+data).hexdigest()
        assert expected==sha,'Git blob identity mismatch'
        actual=git('hash-object','-w','--stdin',input=data).decode().strip();assert actual==sha
        return {'path':path,'git_blob':sha,'bytes':len(data),'status':'VERIFIED_OFFICIAL_CONTENT'}
    except Exception as e:return {'path':path,'git_blob':sha,'status':'BLOCKED','error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=16 if prefix else 8) as pool:
    results=list(pool.map(fetch,missing))
c.save(prefix+'raw-source-recovery.json',{'classification':'OFFICIAL_CONTENT_FETCH_AND_GIT_IDENTITY_CHECK','records':results})
print('verified',sum(r['status']=='VERIFIED_OFFICIAL_CONTENT' for r in results),'blocked',sum(r['status']=='BLOCKED' for r in results),flush=True)
