import React from "react";
import { Series, useVideoConfig } from "remotion";
import { Abertura } from "./cenas/Abertura";
import { Final } from "./cenas/Final";
import { Mapa } from "./cenas/Mapa";
import { Misterios } from "./cenas/Misterios";
import { PassoAPasso } from "./cenas/PassoAPasso";
import { PorQue } from "./cenas/PorQue";

export const VideoTerco: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <Series>
      <Series.Sequence name="Abertura" durationInFrames={150} premountFor={fps}><Abertura /></Series.Sequence>
      <Series.Sequence name="Por que rezar" durationInFrames={390} premountFor={fps}><PorQue /></Series.Sequence>
      <Series.Sequence name="Mapa do terço" durationInFrames={240} premountFor={fps}><Mapa /></Series.Sequence>
      <Series.Sequence name="Passo a passo" durationInFrames={960} premountFor={fps}><PassoAPasso /></Series.Sequence>
      <Series.Sequence name="Mistérios de cada dia" durationInFrames={300} premountFor={fps}><Misterios /></Series.Sequence>
      <Series.Sequence name="Encerramento" durationInFrames={210} premountFor={fps}><Final /></Series.Sequence>
    </Series>
  );
};
