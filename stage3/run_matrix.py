"""Execute a finite native regression list, recording each process exit code."""
import json
import subprocess
import sys
from host import v,WORK
v.check_test_isolation()
cases=[('finish','rc6-fixed-editor'),('draft','rc6-fixed-draft'),('decline','rc6-fixed-decline'),('stale','rc6-fixed-stale'),('cancel','rc6-fixed-cancel'),('readback','rc6-fixed-readback'),('dry','rc6-fixed-dry'),('no_candidate_fixture','rc6-fixed-no-candidate'),('reopen','rc6-fixed-reopen')]
for mode,name in cases:
    command=[sys.executable,'-B',str(WORK/'stage3/native_cases.py'),mode,name]
    with (v.E/(name+'-command.log')).open('x',encoding='utf-8') as output:
        p=subprocess.run(command,cwd=WORK,stdout=output,stderr=subprocess.STDOUT)
    v.save(name+'-command.json',{'command':command,'exit_code':p.returncode})
    print(mode,name,'exit',p.returncode,flush=True)
    if p.returncode:raise SystemExit(p.returncode)
