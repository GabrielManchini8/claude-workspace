"""Exemplo FreeCAD sem interface: lê um STEP e mostra volume e caixa envolvente.

Rode com:  freecadcmd cad/exemplos/freecad_step_info.py  (depois de scripts/setup-cad.sh --freecad)
Arquivo lido: variável de ambiente STEP, padrão cad/saida/flange.step
"""
import os

import Part

caminho = os.environ.get("STEP", "cad/saida/flange.step")
forma = Part.Shape()
forma.read(caminho)
bb = forma.BoundBox
print(f"{caminho}: volume {forma.Volume:.1f} mm3, caixa {bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f} mm")
