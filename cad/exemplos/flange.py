"""Exemplo: flange simples em build123d e desenho técnico automático com draftwright.

Rode com:  .venv-cad/bin/python cad/exemplos/flange.py
Gera cad/saida/flange.step, .svg, .dxf (e o PDF pelo CLI do draftwright).
"""
from pathlib import Path

from build123d import BuildPart, Box, Cylinder, Hole, Locations, PolarLocations, export_step, Mode
from draftwright import make_drawing

saida = Path(__file__).resolve().parents[1] / "saida"
saida.mkdir(exist_ok=True)

with BuildPart() as flange:
    Cylinder(radius=60, height=12)
    Hole(radius=20)
    with PolarLocations(radius=45, count=4):
        Hole(radius=6)

export_step(flange.part, str(saida / "flange.step"))
make_drawing(
    flange.part,
    out=str(saida / "flange"),
    title="FLANGE DN50",
    number="AGEL-001",
    tolerance="ISO 2768-m",
    drawn_by="Agel Brasil",
)
print("Arquivos em", saida)
