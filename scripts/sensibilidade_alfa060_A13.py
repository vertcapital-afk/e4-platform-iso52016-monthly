# -*- coding: utf-8 -*-
"""
sensibilidade_alfa060_A13.py — S1 do AUDITORIA_Fable_RevisaoA13_2026-08-01.md.

O A14 declara sensibilidade a alfa_parede=0,60 (canonizada 31/07/2026, com
figuras); o A13 revisto so declara alfa=0,40 e nao tem sensibilidade no
fatorial -- e e no A13 que o alfa mais mexe (a segmentacao gamma_C troca de
lado por causa dele). Fable pediu esta corrida para fechar a assimetria.

Grelha 32x2 bases com 0,60/0,50 NOS DOIS RAMOS (mesmo padrao try/finally do
revisao_a13_producao.py), mais a segmentacao gamma_C sob 0,60 (via
decomposicao_artigo13.py --revisao, adaptado).
"""
import json
import os
import sys
import statistics as st

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(os.path.dirname(_AQUI))
sys.path.insert(0, os.path.join(_RAIZ, "src"))
sys.path.insert(0, _AQUI)

import run_grelha_artigo13 as g          # noqa: E402
from e4 import solar, geometria          # noqa: E402
from e4.matriz_nacional import RB_SPECS  # noqa: E402

CFG60 = dict(alfa_parede=0.60, desvao_cob=0.0, h_ce=20.0)
PESO = {s.rb: s.peso for s in RB_SPECS}


def _aplicar(cfg):
    antes = dict(a52=g.A_SOL_PAREDE, d52=g.R_DESVAO_COB, hce=g.H_CE,
                 a13=solar.ALFA_PAREDE, d13=geometria.R_DESVAO_COB)
    g.A_SOL_PAREDE = cfg["alfa_parede"]
    g.R_DESVAO_COB = cfg["desvao_cob"]
    g.H_CE = cfg["h_ce"]
    solar.ALFA_PAREDE = cfg["alfa_parede"]
    geometria.R_DESVAO_COB = cfg["desvao_cob"]
    return antes


def _repor(antes):
    g.A_SOL_PAREDE, g.R_DESVAO_COB, g.H_CE = antes["a52"], antes["d52"], antes["hce"]
    solar.ALFA_PAREDE, geometria.R_DESVAO_COB = antes["a13"], antes["d13"]


def quadro(cs, sfx=""):
    dH = [100 * (c[f"nh_52016{sfx}"] - c[f"nic_13790{sfx}"]) / c[f"nic_13790{sfx}"] for c in cs]
    dC = [100 * (c[f"nc_52016{sfx}"] - c[f"nvc_13790{sfx}"]) / c[f"nvc_13790{sfx}"] for c in cs]
    W = sum(PESO[c["rb"]] for c in cs)
    pw = lambda k: sum(c[k] * PESO[c["rb"]] for c in cs) / W          # noqa: E731
    ph = 100 * (pw(f"nh_52016{sfx}") - pw(f"nic_13790{sfx}")) / pw(f"nic_13790{sfx}")
    pc = 100 * (pw(f"nc_52016{sfx}") - pw(f"nvc_13790{sfx}")) / pw(f"nvc_13790{sfx}")
    return st.median(dH), sum(1 for x in dH if x < 0), st.median(dC), \
        sum(1 for x in dC if x < 0), ph, pc


def main():
    antes40 = _aplicar(dict(alfa_parede=0.40, desvao_cob=0.0, h_ce=20.0))
    ref40_a = g.correr_grelha()["celulas"]
    ref40_b = g.correr_grelha_2013()["celulas"]
    _repor(antes40)

    antes = _aplicar(CFG60)
    try:
        a60 = g.correr_grelha()["celulas"]
        b60 = g.correr_grelha_2013()["celulas"]

        ref = json.load(open(os.path.join(_AQUI, "resultados",
                             "grelha_artigo13.json"), encoding="utf-8"))
        _aplicar(dict(alfa_parede=0.04, desvao_cob=0.14, h_ce=20.86))
        sub_check = g.correr_grelha()["celulas"]
        _aplicar(CFG60)
        assert sub_check == ref["celulas"], "REGRESSAO: estado submetido corrompido"
        print("[OK] regressão: estado submetido continua intacto\n")

        print("EFEITO DE MÉTODO -- 32 células por base, três configurações")
        print(f"{'base / alfa':22s}{'ΔH med':>9s}{'neg':>5s}{'ΔC med':>10s}{'neg':>5s}"
              f"{'ΔH pond':>10s}{'ΔC pond':>10s}")
        for base, dados, sfx in (("DGEG2025-A", [ref40_a, a60], ""),
                                 ("REG-2013", [ref40_b, b60], "_2013")):
            for tag, cs in (("α=0,40 (canónico)", dados[0]), ("α=0,60 (sensib.)", dados[1])):
                mh, nh, mc, nc, ph, pc = quadro(cs, sfx)
                print(f"{base + ' ' + tag:22s}{mh:+8.2f}%{nh:5d}{mc:+9.2f}%{nc:5d}"
                      f"{ph:+9.2f}%{pc:+9.2f}%")

        os.makedirs(os.path.join(_AQUI, "resultados"), exist_ok=True)
        meta = {"experiencia": "sensibilidade alfa=0,60 -- fecha a assimetria com o A14 (S1)",
                "config": dict(CFG60), "paridade": "aplicada NOS DOIS RAMOS"}
        with open(os.path.join(_AQUI, "resultados",
                  "sensibilidade_alfa060_A13.json"), "w", encoding="utf-8") as f:
            json.dump({"meta": meta, "dgeg2025a": a60, "reg2013": b60}, f,
                      ensure_ascii=False, indent=1)
        print("\nGravado em resultados/sensibilidade_alfa060_A13.json")
    finally:
        _repor(antes)


def segmentacao_gamma_c_060():
    """Recomputa a decomposicao (gamma_C) sob alfa=0,60, so DGEG2025-A,
    reutilizando decomposicao_artigo13.py --revisao com config sobreposta."""
    import e4.decomposicao_artigo13 as d
    antes = _aplicar(CFG60)
    try:
        celulas = d.correr("DGEG2025-A")
        gte1 = [c for c in celulas if c["gamma_C_sazonal"] >= 1]
        lt1 = [c for c in celulas if c["gamma_C_sazonal"] < 1]
        print("\nSEGMENTAÇÃO γ_C sob α=0,60 (DGEG2025-A, n=32):")
        print(f"  γ_C≥1: n={len(gte1)}  neg={sum(1 for c in gte1 if c['dC']<0)}/{len(gte1)}"
              f"  med={st.median([c['dC'] for c in gte1]):+.1f}%")
        print(f"  γ_C<1: n={len(lt1)}  neg={sum(1 for c in lt1 if c['dC']<0)}/{len(lt1)}"
              f"  med={st.median([c['dC'] for c in lt1]):+.1f}%")
        bem_classificadas = sum(1 for c in gte1 if c["dC"] < 0) + sum(1 for c in lt1 if c["dC"] > 0)
        print(f"  bem classificadas: {bem_classificadas}/32  (α=0,40: 30/32 · submetido: 29/32)")
        json.dump({"meta": {"config": "alfa=0,60"}, "celulas": celulas},
                  open(os.path.join(_AQUI, "resultados",
                       "decomposicao_artigo13_alfa060.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    finally:
        _repor(antes)


if __name__ == "__main__":
    main()
    segmentacao_gamma_c_060()
