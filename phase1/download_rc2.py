import hashlib,json,pathlib,urllib.request,datetime
root=pathlib.Path(__file__).resolve().parent
url='https://github.com/OctoSense-org/OctoSense/releases/download/desktop-v0.1.0-rc.2/octosense_0.1.0-rc.2_x64-setup.exe'
expected='628a68a0d9e5fa615ca01d3a6e3ff2bbd2ccd02cf71ec6acbd9e28a652c58e00'
out=root/'downloads'/'octosense_0.1.0-rc.2_x64-setup.exe'
if not out.exists():
    with urllib.request.urlopen(url,timeout=60) as src,out.open('wb') as dst:
        while True:
            block=src.read(1024*1024)
            if not block: break
            dst.write(block)
actual=hashlib.sha256(out.read_bytes()).hexdigest()
record={'url':url,'bytes':out.stat().st_size,'sha256':actual,'expected_official_sha256':expected,'matched':actual==expected,'downloaded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'executed':False}
(root/'evidence'/'rc2-download.json').write_text(json.dumps(record,indent=2))
print(json.dumps(record,indent=2),flush=True)
if actual!=expected: raise RuntimeError('Official RC2 hash mismatch; do not execute')
