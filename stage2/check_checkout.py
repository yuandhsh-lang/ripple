"""Export exactly Git-filtered bytes to a fresh test directory and check them."""
import hashlib, json, subprocess, sys
from run import WORK, v

def main(label):
    v.check_test_isolation()
    export=v.E/label
    export.mkdir()
    files=subprocess.check_output(['git','ls-files','stage1/bundle'],cwd=WORK,encoding='utf-8').splitlines()
    correspondence=[]
    for name in files:
        p=WORK/name
        # Write only an unreachable Git content object; no ref/index/history edit.
        obj=subprocess.check_output(['git','hash-object','-w','--path='+name,str(p)],cwd=WORK,encoding='utf-8').strip()
        content=subprocess.check_output(['git','cat-file','blob',obj],cwd=WORK)
        target=export/p.relative_to(WORK/'stage1/bundle')
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(content)
        correspondence.append({'path':name,'git_blob':obj,'byte_identical':p.read_bytes()==content})
    result=subprocess.run([str(v.HUB),'check',str(export),'--allow-unsigned','--json'],capture_output=True,text=True,encoding='utf-8')
    v.save(label+'.json',{'classification':'OFFICIAL_HUB_CHECK_OF_GIT_FILTERED_EXPORT',
        'export':str(export),'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,
        'correspondence':correspondence})
    print(label,'exit',result.returncode,'changed byte streams',sum(not x['byte_identical'] for x in correspondence))

if __name__=='__main__':main(sys.argv[1])
