import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
export type Props = {title:string; subtitle:string; credit:string};
export const LowerThird: React.FC<{name:string; detail:string}> = ({name,detail}) => <div style={{borderLeft:'6px solid #d3ac66',paddingLeft:24}}><strong>{name}</strong><div style={{fontSize:'0.55em',marginTop:12}}>{detail}</div></div>;
export const Credits: React.FC<{text:string}> = ({text}) => <div style={{letterSpacing:4,textTransform:'uppercase',fontSize:24}}>{text}</div>;
export const Documentary: React.FC<Props> = ({title,subtitle,credit}) => {
 const f=useCurrentFrame();const {height,width,durationInFrames}=useVideoConfig();
 const opacity=interpolate(f,[0,18,durationInFrames-18,durationInFrames-1],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 const y=interpolate(f,[0,30],[24,0],{extrapolateRight:'clamp'});
 return <AbsoluteFill style={{background:'linear-gradient(135deg,#09141d,#213f4b)',color:'#f6f1e8',fontFamily:'DejaVu Sans',padding:width*0.08,justifyContent:'center'}}>
 <AbsoluteFill style={{background:'radial-gradient(ellipse at 70% 30%,#d3ac6625,transparent 65%)'}} />
 <div style={{opacity,transform:`translateY(${y}px)`,fontSize:Math.min(width*.055,90),zIndex:1}}><LowerThird name={title} detail={subtitle}/></div>
 <div style={{position:'absolute',bottom:height*.09,opacity}}><Credits text={credit}/></div>
 </AbsoluteFill>;
};
