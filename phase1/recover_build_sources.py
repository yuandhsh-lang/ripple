"""Verified HTTP byte-range recovery for prematurely closed official transfers."""
import concurrent.futures,hashlib,http.client,json,os,subprocess,urllib.request
import converge as c
env=os.environ.copy();env['GIT_NO_LAZY_FETCH']='1'
blocked=[r for r in json.loads((c.E/'retry-raw-source-recovery.json').read_text())['records'] if r['status']=='BLOCKED' and not r['path'].endswith(('.png','.jpg','.mp4','.webp','.pdf'))]
def fetch(item):
    sha,path=item['git_blob'],item['path'];url='https://raw.githubusercontent.com/OctoSense-org/OctoSense/'+c.COMMITS[-1]+'/'+path
    chunks=[];data=b'';total=None
    for attempt in range(12):
        req=urllib.request.Request(url,headers={'Range':'bytes='+str(len(data))+'-'+str(len(data)+65535),'Accept-Encoding':'identity'})
        try:
            with urllib.request.urlopen(req,timeout=15) as r:
                status=r.status;cr=r.headers.get('Content-Range');expected=r.headers.get('Content-Length')
                try:piece=r.read()
                except http.client.IncompleteRead as e:piece=e.partial
                chunks.append({'status':status,'content_range':cr,'received_bytes':len(piece),'advertised_bytes':expected})
                if status==206 and cr and cr.startswith('bytes '+str(len(data))+'-'):
                    total=int(cr.split('/')[-1]);data+=piece
                elif status==200:
                    total=int(expected) if expected else len(piece);data=piece
                else: raise ValueError('range response identity invalid')
                if len(data)==total:
                    identity=hashlib.sha1(('blob '+str(len(data))+'\0').encode()+data).hexdigest()
                    if identity!=sha:raise ValueError('complete content Git identity mismatch')
                    p=subprocess.run(['git','hash-object','-w','--stdin'],cwd=c.SRC,env=env,input=data,capture_output=True,check=True);assert p.stdout.decode().strip()==sha
                    return {'path':path,'git_blob':sha,'status':'VERIFIED_OFFICIAL_CONTENT','chunks':chunks}
        except Exception as e:chunks.append({'error':str(e)})
    partial=c.R/'partial-source-blobs';partial.mkdir(exist_ok=True);(partial/sha).write_bytes(data)
    return {'path':path,'git_blob':sha,'status':'BLOCKED','chunks':chunks,'partial_bytes_preserved':len(data)}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(fetch,blocked))
c.save('range-build-source-recovery.json',{'classification':'OFFICIAL_BYTE_RANGE_FETCH_GIT_IDENTITY_VERIFIED','results':results})
print('build source verified',sum(r['status']=='VERIFIED_OFFICIAL_CONTENT' for r in results),'blocked',sum(r['status']=='BLOCKED' for r in results),flush=True)
