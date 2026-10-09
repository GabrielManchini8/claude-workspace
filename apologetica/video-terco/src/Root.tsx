import React from "react";
import { Composition, Folder } from "remotion";
import { Abertura } from "./cenas/Abertura";
import { Final } from "./cenas/Final";
import { Mapa } from "./cenas/Mapa";
import { Misterios } from "./cenas/Misterios";
import { PassoAPasso } from "./cenas/PassoAPasso";
import { PorQue } from "./cenas/PorQue";
import { VideoTerco } from "./VideoTerco";

const base = { width: 1080, height: 1920, fps: 30 } as const;

export const RemotionRoot: React.FC = () => (
  <>
    <Folder name="Cenas">
      <Composition id="Abertura" component={Abertura} {...base} durationInFrames={150} />
      <Composition id="PorQue" component={PorQue} {...base} durationInFrames={390} />
      <Composition id="Mapa" component={Mapa} {...base} durationInFrames={240} />
      <Composition id="PassoAPasso" component={PassoAPasso} {...base} durationInFrames={960} />
      <Composition id="Misterios" component={Misterios} {...base} durationInFrames={300} />
      <Composition id="Final" component={Final} {...base} durationInFrames={210} />
    </Folder>
    <Composition id="ComoRezarOTerco" component={VideoTerco} {...base} durationInFrames={2250} />
  </>
);
