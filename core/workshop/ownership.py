"""Exclusive workspace bridge and Windows kill-on-close worker ownership."""
import ctypes
import os
import uuid
from pathlib import Path

class WorkspaceLock:
    def __init__(self,path:Path):
        path.parent.mkdir(parents=True,exist_ok=True)
        self.stream=path.open('a+b'); self.stream.seek(0)
        if path.stat().st_size==0: self.stream.write(b'0'); self.stream.flush()
        self.stream.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(self.stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError:
            self.stream.close(); raise RuntimeError('A Workshop bridge is already running for this workspace.') from None
    def close(self):
        if not self.stream.closed: self.stream.close()

def kernel_api():
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.CreateJobObjectW.argtypes=[ctypes.c_void_p,ctypes.c_wchar_p]; kernel.CreateJobObjectW.restype=ctypes.c_void_p
    kernel.OpenJobObjectW.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_wchar_p]; kernel.OpenJobObjectW.restype=ctypes.c_void_p
    kernel.GetCurrentProcess.restype=ctypes.c_void_p
    kernel.SetInformationJobObject.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_ulong]
    kernel.AssignProcessToJobObject.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
    kernel.CloseHandle.argtypes=[ctypes.c_void_p]
    return kernel

class WorkerContainment:
    def __init__(self):
        if os.name!='nt': raise RuntimeError('This Workshop worker launcher currently requires Windows process containment.')
        self.kernel=kernel_api(); self.name='Local\\PrintWorkshop-'+uuid.uuid4().hex
        self.handle=self.kernel.CreateJobObjectW(None,self.name)
        if not self.handle: raise ctypes.WinError(ctypes.get_last_error())
        class Basic(ctypes.Structure):
            _fields_=[('process_time',ctypes.c_int64),('job_time',ctypes.c_int64),('flags',ctypes.c_ulong),('min_ws',ctypes.c_size_t),('max_ws',ctypes.c_size_t),('active',ctypes.c_ulong),('affinity',ctypes.c_size_t),('priority',ctypes.c_ulong),('scheduling',ctypes.c_ulong)]
        class Extended(ctypes.Structure):
            _fields_=[('basic',Basic),('io',ctypes.c_uint64*6),('process_memory',ctypes.c_size_t),('job_memory',ctypes.c_size_t),('peak_process',ctypes.c_size_t),('peak_job',ctypes.c_size_t)]
        limits=Extended(); limits.basic.flags=0x2000 # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.kernel.SetInformationJobObject(self.handle,9,ctypes.byref(limits),ctypes.sizeof(limits)):
            error=ctypes.get_last_error(); self.close(); raise ctypes.WinError(error)
    def close(self):
        if self.handle: self.kernel.CloseHandle(self.handle); self.handle=None

def join_worker_job(name):
    """Worker joins before any action; only bridge retains the lifetime handle."""
    if os.name!='nt' or not isinstance(name,str) or not name.startswith('Local\\PrintWorkshop-'):
        raise RuntimeError('Worker requires bridge-owned Windows containment.')
    kernel=kernel_api(); handle=kernel.OpenJobObjectW(1,False,name)
    if not handle: raise ctypes.WinError(ctypes.get_last_error())
    try:
        if not kernel.AssignProcessToJobObject(handle,kernel.GetCurrentProcess()):
            raise ctypes.WinError(ctypes.get_last_error())
    finally: kernel.CloseHandle(handle)
