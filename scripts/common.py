"""Atomic outputs, bounded subprocesses and resource checks."""
import hashlib
import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def run(args):
    logging.info('%s', ' '.join(map(str, args)))
    return subprocess.run(list(map(str,args)),check=True,capture_output=True,text=True)

def probe(path):
    return json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',path]).stdout)

def validate(path):
    info=probe(path)
    if not info['streams'] or float(info['format'].get('duration',0)) <= 0:
        raise ValueError('Empty media')
    run(['ffmpeg','-v','error','-xerror','-i',path,'-f','null','-'])
    return info

def memory_available():
    values={}
    for line in Path('/proc/meminfo').read_text().splitlines():
        k,v=line.split(':',1);values[k]=int(v.strip().split()[0])*1024
    available=values['MemAvailable']
    try:
        limit=Path('/sys/fs/cgroup/memory.max').read_text().strip()
        if limit!='max':
            available=min(available,int(limit)-int(Path('/sys/fs/cgroup/memory.current').read_text()))
    except (OSError,ValueError):pass
    return max(0,available)

def capacity(path, minimum=512*1024**2):
    if shutil.disk_usage(path).free < minimum:
        raise RuntimeError('Insufficient free disk space')
    if memory_available()<256*1024**2:
        raise RuntimeError('Insufficient available memory (less than 256 MiB)')

def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024**2),b''):h.update(block)
    return h.hexdigest()

def atomic_json(path,data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(dir=path.parent,suffix='.json')
    try:
        with os.fdopen(fd,'w') as f:
            json.dump(data,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
        os.replace(name,path)
    finally:
        Path(name).unlink(missing_ok=True)

def encode(output, args):
    """Never clobber an output; validate a temporary file before publication."""
    output=Path(output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():raise FileExistsError(output)
    capacity(output.parent)
    fd,name=tempfile.mkstemp(prefix='encode-',suffix=output.suffix,dir=output.parent);os.close(fd)
    tmp=Path(name)
    try:
        run(['ffmpeg','-hide_banner','-loglevel','error','-y',*args,'-threads',os.getenv('FFMPEG_THREADS','2'),tmp])
        validate(tmp)
        os.link(tmp,output) # atomic, fails if another process published first
    finally:tmp.unlink(missing_ok=True)
