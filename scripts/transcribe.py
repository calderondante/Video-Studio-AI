"""Bounded Spanish ASR with content-addressed checkpoints and human review."""
import argparse
import json
import logging
import math
import os
from pathlib import Path
import tempfile
import time
from filelock import FileLock
from common import atomic_json, capacity, digest, probe, run, memory_available
from subtitles import from_segments, review, save


def hardware():
    import ctranslate2
    gpu=ctranslate2.get_cuda_device_count()>0
    return {'device':'cuda' if gpu else 'cpu','compute_type':'float16' if gpu else 'int8','model':'small' if gpu else ('base' if memory_available()>=2*1024**3 else 'tiny'),'cpu_threads':min(2,os.cpu_count() or 1)}


def process(source,output,model_name=None,chunk_seconds=300,names=(),loader=None):
    if chunk_seconds<5 or chunk_seconds>900:raise ValueError('Chunk size must be 5..900 seconds')
    source=Path(source).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    capacity(output)
    config=hardware();config['model']=model_name or config['model']
    key={'sha256':digest(source),'model':config['model'],'chunk_seconds':chunk_seconds,'language':'es','names':list(names),'pipeline_version':1}
    # Lock prevents concurrent jobs from interleaving checkpoint/export updates.
    with FileLock(str(output/'job.lock'),timeout=1):
        state_path=output/'checkpoint.json'
        state=json.loads(state_path.read_text()) if state_path.exists() else {'key':key,'chunks':{}}
        if state['key']!=key:raise ValueError('Checkpoint belongs to different source/configuration; choose another output directory')
        duration=float(probe(source)['format']['duration'])
        total=math.ceil(duration/chunk_seconds)
        pending=[i for i in range(total) if str(i) not in state['chunks']]
        if pending:
            if loader is None:
                from faster_whisper import WhisperModel
                loader=WhisperModel
            model=loader(config['model'],device=config['device'],compute_type=config['compute_type'],cpu_threads=config['cpu_threads'],download_root=str(Path('.cache/models').resolve()))
            for i in pending:
                capacity(output)
                start=i*chunk_seconds;length=min(chunk_seconds,duration-start)
                with tempfile.TemporaryDirectory(prefix='studio-asr-',dir=output) as t:
                    audio=Path(t)/'chunk.wav'
                    run(['ffmpeg','-v','error','-n','-ss',start,'-i',source,'-t',length,'-vn','-ac','1','-ar','16000',audio])
                    for attempt in range(3):
                        try:
                            segments,_=model.transcribe(str(audio),language='es',vad_filter=True,word_timestamps=True,initial_prompt=', '.join(names) or None,beam_size=5,condition_on_previous_text=False)
                            rows=[]
                            for s in segments:
                                words=[{'start':w.start+start,'end':min(w.end+start,duration),'word':w.word,'probability':w.probability} for w in (s.words or [])]
                                flags=[]
                                if s.avg_logprob < -0.7:flags.append('low_confidence')
                                if s.no_speech_prob>.5:flags.append('possible_silence')
                                if any(w['probability']<.5 for w in words):flags.append('uncertain_words')
                                rows.append({'start':s.start+start,'end':min(s.end+start,duration),'text':s.text.strip(),'avg_logprob':s.avg_logprob,'no_speech_prob':s.no_speech_prob,'words':words,'review':flags,'proper_names_to_review':[n for n in names if n.casefold() in s.text.casefold()]})
                            state['chunks'][str(i)]=rows;atomic_json(state_path,state);break
                        except (OSError,RuntimeError):
                            if attempt==2:raise
                            logging.exception('ASR chunk %s failed; safe retry %s',i,attempt+1);time.sleep(attempt+1)
        segments=[s for i in range(total) for s in state['chunks'][str(i)]]
        subs=from_segments(segments);issues=review(subs,duration)
        if any(set(i['flags'])&{'invalid_time','overlap','past_media_end'} for i in issues):raise ValueError('Invalid ASR timing; review checkpoint')
        atomic_json(output/'transcript.json',{'source_sha256':key['sha256'],'hardware':config,'duration':duration,'segments':segments,'subtitle_review':issues,'proper_names_checklist':list(names),'boundary_review_seconds':[i*chunk_seconds for i in range(1,total)]})
        # Exports are derived from the checkpoint, never from the original media.
        for name,text in [('transcript.txt','\n'.join(s['text'] for s in segments)),('transcript.srt',subs.to_string('srt'))]:
            fd,tmp=tempfile.mkstemp(dir=output,suffix='.tmp')
            with os.fdopen(fd,'w') as f:f.write(text)
            os.replace(tmp,output/name)
        logging.info('Completed %s chunks, %s cues; %s readability warnings',total,len(subs),len(issues))
    return segments


def main():
    p=argparse.ArgumentParser();p.add_argument('input',nargs='?');p.add_argument('--output',default='work/transcription');p.add_argument('--model');p.add_argument('--chunk-seconds',type=int,default=300);p.add_argument('--names',help='UTF-8 JSON array of proper names; used as hints, never automatic replacements');p.add_argument('--check',action='store_true')
    a=p.parse_args()
    if a.check:
        import faster_whisper
        from faster_whisper.vad import get_speech_timestamps, VadOptions
        import numpy as np
        assert get_speech_timestamps(np.zeros(16000,dtype=np.float32),VadOptions())==[]
        print(json.dumps(hardware()));return
    if not a.input:p.error('input required')
    process(a.input,a.output,a.model,a.chunk_seconds,json.loads(Path(a.names).read_text()) if a.names else [])

if __name__=='__main__':main()
