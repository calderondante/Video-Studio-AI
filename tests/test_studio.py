import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from common import encode, probe, run, validate, digest
from subtitles import from_segments, review
from transcribe import process

ROOT=Path(__file__).resolve().parents[1]
PYTHON=sys.executable

def media(*args):
    return run([PYTHON,ROOT/'scripts/media.py',*args])

class Subtitles(unittest.TestCase):
    def test_wrap_and_timing(self):
        subs=from_segments([{'start':0,'end':15,'text':'La memoria de los protagonistas permite comprender la historia. Este testimonio conserva los nombres y las experiencias de quienes estuvieron presentes.'}])
        self.assertGreater(len(subs),1)
        self.assertEqual(review(subs,15),[])
        self.assertEqual(subs[-1].end,15000)
    def test_detect_invalid_timing(self):
        import pysubs2
        subs=pysubs2.SSAFile();subs.append(pysubs2.SSAEvent(start=1000,end=500,text='Hola'))
        self.assertIn('invalid_time',review(subs)[0]['flags'])

class Media(unittest.TestCase):
    def test_real_processing_and_subtitle_frames(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);source=p/'source.mp4'
            media('synthetic','unused',source);original=digest(source)
            captions=p/'sample.srt';captions.write_text('1\n00:00:00,500 --> 00:00:02,500\nMemoria y testimonio.\n')
            out=p/'sub.mp4';media('burn',source,out,'--subtitles',captions)
            d=validate(out);video=next(s for s in d['streams'] if s['codec_type']=='video');audio=next(s for s in d['streams'] if s['codec_type']=='audio')
            self.assertEqual(video['codec_name'],'h264');self.assertEqual(audio['codec_name'],'aac');self.assertAlmostEqual(float(d['format']['duration']),3,delta=.1)
            def raw(path,at):
                return subprocess.run(['ffmpeg','-v','error','-ss',str(at),'-i',str(path),'-frames:v','1','-f','rawvideo','-pix_fmt','gray','-'],check=True,capture_output=True).stdout
            import numpy as np
            def diff(at):
                return np.abs(np.frombuffer(raw(source,at),dtype=np.uint8).astype(float)-np.frombuffer(raw(out,at),dtype=np.uint8).astype(float)).sum()
            self.assertGreater(diff(1),diff(.1)*3+1000)
            media('audio',source,p/'audio.wav');self.assertEqual(probe(p/'audio.wav')['streams'][0]['sample_rate'],'16000')
            media('normalize',source,p/'normal.mp4')
            media('resize',source,p/'resized.mp4','--width','320','--height','240','--fps','24')
            self.assertEqual(probe(p/'resized.mp4')['streams'][0]['width'],320)
            manifest=p/'list.json';manifest.write_text(json.dumps([str(source),str(source)]))
            media('concat',manifest,p/'joined.mp4');self.assertAlmostEqual(float(probe(p/'joined.mp4')['format']['duration']),6,delta=.15)
            media('frame',out,p/'frame.png');self.assertEqual(probe(p/'frame.png')['streams'][0]['codec_name'],'png')
            with self.assertRaises(subprocess.CalledProcessError):media('audio',source,p/'audio.wav')
            self.assertEqual(digest(source),original)

class Resume(unittest.TestCase):
    def test_checkpoints_reuse_and_reject_changed_configuration(self):
        # Fake ASR isolates recovery correctness; this is not a real inference test.
        class Model:
            calls=0
            def __init__(self,*args,**kwargs):pass
            def transcribe(self,*args,**kwargs):
                Model.calls+=1
                s=SimpleNamespace(start=0,end=2,text='Hola Argentina',avg_logprob=-.2,no_speech_prob=.01,words=[])
                return iter([s]),None
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);media('synthetic','unused',p/'source.mp4')
            process(p/'source.mp4',p/'asr','test',5,loader=Model)
            self.assertEqual(Model.calls,1)
            process(p/'source.mp4',p/'asr','test',5,loader=Model)
            self.assertEqual(Model.calls,1)
            self.assertIn('Hola Argentina',(p/'asr/transcript.srt').read_text())
            with self.assertRaises(ValueError):process(p/'source.mp4',p/'asr','test',6,loader=Model)

if __name__=='__main__':unittest.main()
