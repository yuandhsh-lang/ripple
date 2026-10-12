"""Windows OS access test; never read credential bytes. Restricted token != second user."""
import ctypes as c
from ctypes import wintypes as w
import json
import sys
from pathlib import Path
k=c.WinDLL('kernel32',use_last_error=True);a=c.WinDLL('advapi32',use_last_error=True)
class SA(c.Structure): _fields_=[('Sid',c.c_void_p),('Attributes',w.DWORD)]
k.GetCurrentProcess.restype=w.HANDLE
k.CreateFileW.argtypes=[w.LPCWSTR,w.DWORD,w.DWORD,c.c_void_p,w.DWORD,w.DWORD,w.HANDLE];k.CreateFileW.restype=w.HANDLE
k.CloseHandle.argtypes=[w.HANDLE]
a.OpenProcessToken.argtypes=[w.HANDLE,w.DWORD,c.POINTER(w.HANDLE)]
a.ConvertStringSidToSidW.argtypes=[w.LPCWSTR,c.POINTER(c.c_void_p)]
a.CreateRestrictedToken.argtypes=[w.HANDLE,w.DWORD,w.DWORD,c.c_void_p,w.DWORD,c.c_void_p,w.DWORD,c.POINTER(SA),c.POINTER(w.HANDLE)]
a.ImpersonateLoggedOnUser.argtypes=[w.HANDLE]
def check(ok):
    if not ok: raise c.WinError(c.get_last_error())
def open_only(p):
    h=k.CreateFileW(str(p),0x80000000,7,None,3,0,None)
    if h==c.c_void_p(-1).value:return {'opened':False,'winerror':c.get_last_error()}
    k.CloseHandle(h);return {'opened':True,'bytes_read':0}
root=Path(__file__).resolve().parent.parent
name=sys.argv[1]
if not name.startswith('p4-') or '/' in name or '\\' in name:raise ValueError('fresh stage4 only')
p=root/'stage2/runtime/runs'/name/'kernel-core/profiles/acl-canary.txt'
ordinary=open_only(p);assert ordinary['opened']
token=w.HANDLE();restricted=w.HANDLE();sid=c.c_void_p()
check(a.OpenProcessToken(k.GetCurrentProcess(),0xB,c.byref(token)))
check(a.ConvertStringSidToSidW('S-1-5-32-545',c.byref(sid)))
restrict=SA(sid,0)
try:
    check(a.CreateRestrictedToken(token,1,0,None,0,None,1,c.byref(restrict),c.byref(restricted)))
    check(a.ImpersonateLoggedOnUser(restricted))
    try: denied=open_only(p)
    finally:check(a.RevertToSelf())
finally:
    if restricted:k.CloseHandle(restricted)
    k.CloseHandle(token);k.LocalFree(sid)
result={'classification':'STAGE4_NON_SECRET_CANARY_RESTRICTED_TOKEN_NOT_SEPARATE_ACCOUNT','profile':str(p),'current_user':ordinary,'BU_restricted_token':denied,'real_other_account_test':'NOT VERIFIED'}
with (root/'stage2/evidence/runs'/name/'acl-access-check.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result));assert not denied['opened'] and denied['winerror']==5
