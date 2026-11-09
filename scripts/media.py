"""Non-destructive FFmpeg operations. Run with --help."""
import argparse
import json
from pathlib import Path
import tempfile
from common import encode, probe, run, validate


def main():
    p=argparse.ArgumentParser();p.add_argument('operation',choices=['synthetic','audio','normalize','burn','resize','frame','concat','verify'])
    p.add_argument('input');p.add_argument('output',nargs='?');p.add_argument('--subtitles');p.add_argument('--width',type=int,default=1920);p.add_argument('--height',type=int,default=1080);p.add_argument('--fps',type=int,default=30);p.add_argument('--at',type=float,default=1)
    a=p.parse_args()
    if a.operation=='verify':print(json.dumps(validate(a.input),indent=2));return
    if not a.output:p.error('output required')
    if a.operation=='synthetic':
        encode(a.output,['-f','lavfi','-i','color=c=0x142c3b:s=640x360:r=30:d=3','-f','lavfi','-i','sine=frequency=440:duration=3','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest','-movflags','+faststart']);return
    if a.operation=='concat':
        # JSON array; normalize mismatching source formats before concatenating.
        files=[Path(x).resolve() for x in json.loads(Path(a.input).read_text())]
        if not files:raise ValueError('Empty concat list')
        signatures=[]
        for f in files:
            d=probe(f);signatures.append([(s['codec_type'],s['codec_name'],s.get('width'),s.get('height'),s.get('r_frame_rate'),s.get('sample_rate'),s.get('channels'),s.get('time_base'),s.get('extradata_size')) for s in d['streams']])
        if any(s!=signatures[0] for s in signatures):raise ValueError('Incompatible streams; normalize first')
        with tempfile.TemporaryDirectory() as t:
            manifest=Path(t)/'concat.txt'
            manifest.write_text(''.join("file '"+str(f).replace("'","'\\''")+"'\n" for f in files))
            encode(a.output,['-f','concat','-safe','0','-i',manifest,'-c','copy','-movflags','+faststart'])
        return
    args=['-i',Path(a.input).resolve()]
    if a.operation=='audio':args+=['-vn','-ac','1','-ar','16000','-c:a','pcm_s16le']
    elif a.operation=='frame':args+=['-ss',str(a.at),'-frames:v','1']
    else:
        if a.operation=='normalize':args+=['-af','afftdn=nf=-25,loudnorm=I=-16:TP=-1.5:LRA=11']
        elif a.operation=='resize':
            if a.width%2 or a.height%2 or min(a.width,a.height,a.fps)<=0:raise ValueError('Positive even dimensions and positive fps required')
            args+=['-vf',f'scale={a.width}:{a.height}:force_original_aspect_ratio=decrease,pad={a.width}:{a.height}:(ow-iw)/2:(oh-ih)/2,fps={a.fps}']
        elif a.operation=='burn':
            if not a.subtitles:p.error('--subtitles required')
            # Normalize both SRT and ASS to a resolution-aware Documentary preset.
            import pysubs2
            from subtitles import save, review
            info=probe(a.input)
            video=next(s for s in info['streams'] if s['codec_type']=='video')
            subs=pysubs2.load(a.subtitles)
            issues=review(subs,float(info['format']['duration']))
            if any(set(i['flags']) & {'invalid_time','overlap','past_media_end'} for i in issues):
                raise ValueError('Subtitle synchronization is invalid')
            with tempfile.TemporaryDirectory(prefix='studio-subs-') as t:
                safe=Path(t)/'captions.ass'
                save(subs,safe,video['width'],video['height'])
                encode(a.output,args+['-vf',f'ass=filename={safe}','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart'])
            return
        args+=['-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart']
    # PNG has no duration; validate separately, retaining non-overwrite semantics.
    if a.operation=='frame':
        out=Path(a.output)
        out.parent.mkdir(parents=True,exist_ok=True)
        run(['ffmpeg','-v','error','-n',*args,out])
        if probe(out)['streams'][0]['codec_name']!='png':raise ValueError('Expected PNG')
    else:encode(a.output,args)

if __name__=='__main__':main()
