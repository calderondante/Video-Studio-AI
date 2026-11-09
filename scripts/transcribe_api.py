"""Optional authorized OpenAI-compatible adapter for short audio chunks.
Never used by install or local transcription. No credentials are stored.
"""
import argparse
import json
import os
from pathlib import Path
import urllib.request
import uuid
from common import atomic_json
p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('output');p.add_argument('--endpoint',default='https://api.openai.com/v1/audio/transcriptions');p.add_argument('--model',default='whisper-1');a=p.parse_args()
if not a.endpoint.startswith('https://'):raise ValueError('HTTPS required')
if Path(a.output).exists():raise FileExistsError(a.output)
key=os.environ.get('TRANSCRIPTION_API_KEY')
if not key:raise RuntimeError('Configure TRANSCRIPTION_API_KEY securely for the authorized endpoint')
source=Path(a.input)
if source.stat().st_size>24*1024**2:raise ValueError('Split audio into chunks smaller than 24 MiB')
boundary=uuid.uuid4().hex
parts=[]
for name,value in [('model',a.model),('language','es'),('response_format','verbose_json')]:
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="audio.wav"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode()+source.read_bytes()+f'\r\n--{boundary}--\r\n'.encode())
request=urllib.request.Request(a.endpoint,data=b''.join(parts),headers={'Authorization':'Bearer '+key,'Content-Type':'multipart/form-data; boundary='+boundary})
with urllib.request.urlopen(request,timeout=180) as response:result=json.load(response)
if not isinstance(result,dict) or 'text' not in result:raise ValueError('Invalid transcription response')
atomic_json(a.output,result)
