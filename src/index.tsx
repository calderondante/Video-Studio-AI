import React from 'react';
import {registerRoot, Composition} from 'remotion';
import {Documentary} from './templates';
const Root: React.FC = () => <>
  <Composition id="Documental" component={Documentary} durationInFrames={90} fps={30} width={1920} height={1080} defaultProps={{title:'Video Studio AI',subtitle:'Historias que merecen ser contadas',credit:'Archivo documental'}} />
  <Composition id="Vertical" component={Documentary} durationInFrames={90} fps={30} width={1080} height={1920} defaultProps={{title:'Video Studio AI',subtitle:'Memoria en primera persona',credit:'Archivo documental'}} />
</>;
registerRoot(Root);
