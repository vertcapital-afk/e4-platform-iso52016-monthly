# -*- coding: utf-8 -*-
"""numerar_figuras_r1.py — A13 R1: renumera as figuras pela ordem da primeira chamada no
texto (regra da E&B).

Os produtores (figures/gerar_figuras*.py) mantêm a numeração da versão submetida
(FigN_*). Este passo copia a saída gerada em figures/saida_revisao/ para
figures/submissao_R1/ com a numeração R1. Correr depois de gerar as figuras.

Uso (Windows: «py»):  py scripts\\numerar_figuras_r1.py

Adaptado de revisao/numerar_figuras_r1.py do repositório do autor (03/11/2026).
No depósito: caminhos relativos à raiz do depósito, sem pasta pessoal por omissão.
O mapa de numeração não mudou.
"""
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "figures" / "saida_revisao"
OUT = RAIZ / "figures" / "submissao_R1"
OUT.mkdir(exist_ok=True)

# número submetido -> número R1 (ordem da primeira chamada no manuscrito R1)
R1 = {5: 1, 2: 2, 3: 3, 7: 4, 4: 5, 8: 6, 1: 7, 9: 8, 10: 9, 6: 10}
for velho, novo in R1.items():
    pdf = SRC / f"Fig{velho}.pdf"
    png = next(p for p in SRC.glob(f"Fig{velho}_*.png") if "graphical_abstract" not in p.name)
    shutil.copyfile(pdf, OUT / f"Fig{novo}.pdf")
    shutil.copyfile(png, OUT / f"Fig{novo}.png")
for ext in ("pdf", "png"):
    shutil.copyfile(SRC / f"Fig4_graphical_abstract.{ext}", OUT / f"Graphical_abstract.{ext}")
print("Figuras R1 em", OUT, ":", sorted(p.name for p in OUT.iterdir()))
