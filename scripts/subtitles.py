"""SRT/ASS conversion, documentary styling and timing/readability review."""
import argparse
import json
from pathlib import Path
import re
import textwrap
import pysubs2


def from_segments(segments):
    subs=pysubs2.SSAFile()
    for s in segments:
        text=s['text'].strip()
        # Prefer punctuation boundaries, then balanced line wrapping.
        phrases=re.split(r'(?<=[.!?;,])\s+',text)
        groups=[];current=''
        for phrase in phrases:
            if len(current)+len(phrase)+1>84 and current:groups.append(current);current=''
            current=(current+' '+phrase).strip()
        if current:groups.append(current)
        chunks=[]
        for group in groups:
            words=textwrap.wrap(group,42,break_long_words=False,break_on_hyphens=False)
            chunks.extend(['\n'.join(words[i:i+2]) for i in range(0,len(words),2)])
        total=sum(len(c) for c in chunks) or 1;cursor=float(s['start']);end=float(s['end'])
        for c in chunks:
            stop=min(end,cursor+(end-float(s['start']))*len(c)/total)
            subs.append(pysubs2.SSAEvent(start=round(cursor*1000),end=round(stop*1000),text=c.replace('\n',r'\N')));cursor=stop
    return subs


def review(subs,duration=None):
    issues=[];previous=0
    for i,s in enumerate(subs,1):
        text=s.plaintext; seconds=(s.end-s.start)/1000
        flags=[]
        if s.start<0 or s.end<=s.start:flags.append('invalid_time')
        if s.start<previous:flags.append('overlap')
        if duration is not None and s.end>duration*1000+50:flags.append('past_media_end')
        if len(text.splitlines())>2 or any(len(l)>42 for l in text.splitlines()):flags.append('line_length')
        if seconds>0 and len(text.replace('\n',''))/seconds>20:flags.append('reading_speed')
        if flags:issues.append({'cue':i,'flags':flags})
        previous=s.end
    return issues


def save(subs,path,width=1920,height=1080):
    path=Path(path)
    if path.exists():raise FileExistsError(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    subs.info.update(PlayResX=str(width),PlayResY=str(height),WrapStyle='0')
    subs.styles['Default']=pysubs2.SSAStyle(fontname='DejaVu Sans',fontsize=48*height/1080,primarycolor=pysubs2.Color(255,255,255),outlinecolor=pysubs2.Color(0,0,0),outline=2.5*height/1080,shadow=1,alignment=pysubs2.Alignment.BOTTOM_CENTER,marginl=round(width*.07),marginr=round(width*.07),marginv=round(height*.065))
    subs.save(str(path))


def main():
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('output');p.add_argument('--duration',type=float);p.add_argument('--width',type=int,default=1920);p.add_argument('--height',type=int,default=1080)
    a=p.parse_args();src=Path(a.input)
    if src.suffix=='.json':
        d=json.loads(src.read_text());subs=from_segments(d if isinstance(d,list) else d['segments'])
    else:subs=pysubs2.load(str(src))
    issues=review(subs,a.duration);print(json.dumps(issues,indent=2))
    if any(set(i['flags']) & {'invalid_time','overlap','past_media_end'} for i in issues):raise ValueError('Invalid subtitle timing')
    save(subs,a.output,a.width,a.height)

if __name__=='__main__':main()
