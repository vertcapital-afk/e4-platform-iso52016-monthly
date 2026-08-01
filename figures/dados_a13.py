# -*- coding: utf-8 -*-
"""
dados_a13.py — fonte ÚNICA de dados para as figuras e estatísticas do Artigo 13.

⛔ PORQUE EXISTE: até 31/07/2026 os dados da base REG-2013 estavam transcritos
à mão como literal de string (`T = \"\"\"189.88 189.84 ...\"\"\"`) em TRÊS scripts
de figuras. O literal continha um erro de transposição (RB2/Coimbra N_H:
143.43 em vez de 134.43) que se propagou a todas as estatísticas e figuras da
base 2013 — e ao `.docx` submetido. Ler do JSON torna esse erro
estruturalmente impossível.

Melhoria adicional: o emparelhamento entre bases passa a ser por
(rb, cidade) e não por ÍNDICE. A ordem das células deixa de ser um
pressuposto silencioso.

Uso:
    from dados_a13 import carregar, ESTADO
    D = carregar()          # 32 células com os campos das duas bases

    py estatisticas.py               -> estado SUBMETIDO
    py estatisticas.py --revisao     -> estado REVISTO [P-alfa-A13-paridade]
"""
import os
import sys
import json

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RES = os.path.join(os.path.dirname(_AQUI), "resultados")

REVISAO = ("--revisao" in sys.argv) or (os.environ.get("A13_REVISAO") == "1")
_SFX = "_REVISAO" if REVISAO else ""
ESTADO = "REVISTO [P-alfa-A13-paridade]" if REVISAO else "SUBMETIDO (JBE)"


def _ler(nome):
    with open(os.path.join(_RES, nome), encoding="utf-8") as f:
        return json.load(f)["celulas"]


def carregar():
    """32 células da base DGEG2025-A, com os campos da REG-2013 acoplados.

    Campos acrescentados (nomes herdados dos scripts de figuras):
        nic13, nh13, nvc13, nc13  — base REG-2013
    """
    a = _ler(f"grelha_artigo13{_SFX}.json")
    b = _ler(f"grelha_artigo13_2013{_SFX}.json")
    m = {(c["rb"], c["cidade"]): c for c in b}
    if len(a) != 32 or len(m) != 32:
        raise SystemExit(f"⛔ esperava 32+32 células, obtive {len(a)}+{len(m)}")
    for c in a:
        d = m[(c["rb"], c["cidade"])]
        c["nic13"], c["nh13"] = d["nic_13790_2013"], d["nh_52016_2013"]
        c["nvc13"], c["nc13"] = d["nvc_13790_2013"], d["nc_52016_2013"]
    return a


def sufixo_ficheiro():
    """Sufixo para nomes de figuras — o nome de saída depende da configuração,
    para uma corrida em revisão nunca sobrescrever as figuras submetidas."""
    return _SFX.lower()
