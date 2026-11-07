#!/usr/bin/env bash
# Prepara o ambiente de CAD na sessão de nuvem do Claude Code.
#   scripts/setup-cad.sh            -> cria .venv-cad com CadQuery, build123d e draftwright
#   scripts/setup-cad.sh --freecad  -> também baixa o FreeCAD 1.0.2 (AppImage, ~800 MB) em /opt/freecad
# O FreeCAD é só para a nuvem (Linux, sem interface). Não rode --freecad na sua máquina.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -x .venv-cad/bin/python ]; then
  python3 -m venv .venv-cad
fi
.venv-cad/bin/pip install -q --upgrade pip
.venv-cad/bin/pip install -q -r requirements-cad.txt
.venv-cad/bin/python -c "import cadquery, build123d, draftwright; print('CAD Python OK')"

if [ "${1:-}" = "--freecad" ]; then
  FC_DIR=/opt/freecad
  FC_URL=https://github.com/FreeCAD/FreeCAD/releases/download/1.0.2/FreeCAD_1.0.2-conda-Linux-x86_64-py311.AppImage
  if [ ! -x "$FC_DIR/squashfs-root/usr/bin/freecadcmd" ]; then
    mkdir -p "$FC_DIR"
    curl -sSL -o "$FC_DIR/FreeCAD.AppImage" "$FC_URL"
    chmod +x "$FC_DIR/FreeCAD.AppImage"
    (cd "$FC_DIR" && ./FreeCAD.AppImage --appimage-extract >/dev/null)
    rm "$FC_DIR/FreeCAD.AppImage"
  fi
  printf '#!/bin/sh\nexec %s freecadcmd "$@"\n' "$FC_DIR/squashfs-root/AppRun" > /usr/local/bin/freecadcmd
  chmod +x /usr/local/bin/freecadcmd
  echo "FreeCAD OK: freecadcmd script.py"
fi
