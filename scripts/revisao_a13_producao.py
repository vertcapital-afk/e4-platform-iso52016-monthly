# -*- coding: utf-8 -*-
"""
revisao_a13_producao.py — grelha de REVISÃO do Artigo 13.

[P-alfa-A13-paridade] — vetado por S. Tadeu, 31/07/2026:

    · α_parede   0,04 -> 0,40   NOS DOIS RAMOS (52016 e 13790)
    · desvão     0,14 -> 0,0    NOS DOIS RAMOS
    · h_ce      20,86 -> 20,0   só no ramo 52016 (o 13790 não usa o conceito;
                                usa R_se=0,04, i.e. h_se=25 — convenção própria
                                de cada método, a declarar nos Métodos)
    · α_cobertura = 0,50        já estava em paridade; não se toca

⛔ PORQUÊ "NOS DOIS RAMOS": a absortância e o desvão vivem em sítios diferentes
para cada ramo — 52016 em run_grelha_artigo13.py, 13790 em e4/solar.py e
e4/geometria.py. Corrigir só um lado quebra a PARIDADE DE ENVOLVENTE, que é a
tese central do artigo, e fabrica um efeito de método falso (ΔN_C mediana
+86,8% em vez de +1,9%). Medido em 31/07/2026.

⛔ Os módulos partilhados NÃO ficam alterados: a sobreposição é em runtime, com
try/finally. `solar.py` e `geometria.py` mantêm os valores submetidos por
omissão — a decisão sobre eles pertence ao Artigo 11 (em revisão na E&B),
noutra conversa.

Uso:
    py studies\\a13_iso52016_mensal\\revisao_a13_producao.py

Saída: resultados/grelha_artigo13_REVISAO.json
       resultados/grelha_artigo13_2013_REVISAO.json
       + tabela comparativa submetido vs revisto no stdout
"""
import os
import sys
import json
import statistics as st

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(os.path.dirname(_AQUI))
sys.path.insert(0, os.path.join(_RAIZ, "src"))
sys.path.insert(0, _AQUI)

import run_grelha_artigo13 as g          # noqa: E402
from e4 import solar, geometria          # noqa: E402
from e4.matriz_nacional import RB_SPECS  # noqa: E402

# ------------------------------------------------------------------ decisão
REVISAO = dict(alfa_parede=0.40, desvao_cob=0.0, h_ce=20.0)
SUBMETIDO = dict(alfa_parede=0.04, desvao_cob=0.14, h_ce=20.86)

PESO = {s.rb: s.peso for s in RB_SPECS}
OUT = os.path.join(_AQUI, "resultados")


def _aplicar(cfg):
    """Põe a configuração NOS DOIS RAMOS. Devolve o estado anterior."""
    antes = dict(a52=g.A_SOL_PAREDE, d52=g.R_DESVAO_COB, hce=g.H_CE,
                 a13=solar.ALFA_PAREDE, d13=geometria.R_DESVAO_COB)
    g.A_SOL_PAREDE = cfg["alfa_parede"]          # ramo 52016
    g.R_DESVAO_COB = cfg["desvao_cob"]
    g.H_CE = cfg["h_ce"]
    solar.ALFA_PAREDE = cfg["alfa_parede"]       # ramo 13790 (paridade)
    geometria.R_DESVAO_COB = cfg["desvao_cob"]
    return antes


def _repor(antes):
    g.A_SOL_PAREDE, g.R_DESVAO_COB, g.H_CE = antes["a52"], antes["d52"], antes["hce"]
    solar.ALFA_PAREDE, geometria.R_DESVAO_COB = antes["a13"], antes["d13"]


def corrida(cfg):
    antes = _aplicar(cfg)
    try:
        return g.correr_grelha()["celulas"], g.correr_grelha_2013()["celulas"]
    finally:
        _repor(antes)   # os módulos partilhados NUNCA ficam alterados


def quadro(cs, sfx):
    """(ΔH mediana, nº negativas, ΔC mediana, nº negativas, ΔH pond., ΔC pond.)"""
    dH = [100 * (c[f"nh_52016{sfx}"] - c[f"nic_13790{sfx}"]) / c[f"nic_13790{sfx}"] for c in cs]
    dC = [100 * (c[f"nc_52016{sfx}"] - c[f"nvc_13790{sfx}"]) / c[f"nvc_13790{sfx}"] for c in cs]
    W = sum(PESO[c["rb"]] for c in cs)
    pw = lambda k: sum(c[k] * PESO[c["rb"]] for c in cs) / W          # noqa: E731
    ph = 100 * (pw(f"nh_52016{sfx}") - pw(f"nic_13790{sfx}")) / pw(f"nic_13790{sfx}")
    pc = 100 * (pw(f"nc_52016{sfx}") - pw(f"nvc_13790{sfx}")) / pw(f"nvc_13790{sfx}")
    return st.median(dH), sum(1 for x in dH if x < 0), st.median(dC), \
        sum(1 for x in dC if x < 0), ph, pc


def main():
    sub_a, sub_b = corrida(SUBMETIDO)
    rev_a, rev_b = corrida(REVISAO)

    # regressão obrigatória: a configuração submetida tem de reproduzir o JSON
    # submetido célula a célula. Se falhar, alguma coisa mudou por baixo.
    ref = json.load(open(os.path.join(OUT, "grelha_artigo13.json"), encoding="utf-8"))
    if sub_a != ref["celulas"]:
        print("⛔ REGRESSÃO: a config submetida já não reproduz grelha_artigo13.json")
        return 1
    print("[OK] regressão: config submetida reproduz os 64 valores submetidos\n")

    meta = {"decisao": "[P-alfa-A13-paridade] vetado por S. Tadeu 31/07/2026",
            "correccoes": REVISAO, "paridade": "aplicada NOS DOIS RAMOS",
            "modulos_partilhados": "solar.py/geometria.py NÃO alterados (Artigo 11)"}
    for nome, cs in (("grelha_artigo13_REVISAO.json", rev_a),
                     ("grelha_artigo13_2013_REVISAO.json", rev_b)):
        with open(os.path.join(OUT, nome), "w", encoding="utf-8") as f:
            json.dump({"meta": meta, "celulas": cs}, f, ensure_ascii=False, indent=1)

    print("EFEITO DE MÉTODO (52016 − 13790) — 32 células por base")
    print(f"{'base / estado':28s}{'ΔH med':>9s}{'neg':>5s}{'ΔC med':>10s}{'neg':>5s}"
          f"{'ΔH pond':>10s}{'ΔC pond':>10s}")
    for base, s_, r_, sfx in (("DGEG2025-A", sub_a, rev_a, ""),
                              ("REG-2013", sub_b, rev_b, "_2013")):
        for tag, cs in ((" submetido", s_), (" REVISTO  ", r_)):
            mh, nh, mc, nc, ph, pc = quadro(cs, sfx)
            print(f"{base + tag:28s}{mh:+8.2f}%{nh:5d}{mc:+9.2f}%{nc:5d}"
                  f"{ph:+9.2f}%{pc:+9.2f}%")
    print("\nGravado em resultados/*_REVISAO.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
