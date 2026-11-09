import importlib.metadata
import json
import shutil
from common import run
from transcribe import hardware

def main():
    for cmd in ['node','npm','python3','git','ffmpeg','ffprobe','chromium']:
        if not shutil.which(cmd):raise RuntimeError('Missing '+cmd)
    filters=run(['ffmpeg','-hide_banner','-filters']).stdout
    for f in ['subtitles','ass','afftdn','loudnorm']:assert f in filters,f
    encoders=run(['ffmpeg','-hide_banner','-encoders']).stdout
    for e in ['libx264','aac']:assert e in encoders,e
    print(json.dumps({'hardware':hardware(),'python':{p:importlib.metadata.version(p) for p in ['faster-whisper','pysubs2','ctranslate2','onnxruntime']},'disk_free_gib':round(shutil.disk_usage('.').free/1024**3,2)},indent=2))
if __name__=='__main__':main()
