# -*- coding: utf-8 -*-
"""
verificar_revisao_a13.py — S2 do AUDITORIA_Fable_RevisaoA13_2026-08-01.md.

Persiste como verificacao permanente cinco checks que ate 01/08/2026 so
tinham corrido em sessao interativa: I3 (media ponderada de racios), I7a
(cruzamento ingenuo RB6/Coimbra), I9 (banda de irradiacao de referencia),
F1 (efeito de base -- orfao de todas as listas ate a auditoria Fable) e a
coerencia parametrica A13<->A14 (o proprio ponto mais forte da auditoria).

Nao recomputa fisica nova -- so persiste o que ja foi verificado por
execucao em 01/08/2026, para o ritual pre-submissao ter UM comando so.

Uso: py studies\\a13_iso52016_mensal\\verificar_revisao_a13.py
"""
import json
import os
import statistics as st
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(os.path.dirname(_AQUI))
sys.path.insert(0, os.path.join(_RAIZ, "src"))
sys.path.insert(0, _AQUI)

import run_grelha_artigo13 as g          # noqa: E402
from e4 import solar, geometria          # noqa: E402
from e4.matriz_nacional import RB_SPECS  # noqa: E402
from e4.clima_epw import (ler_epw, ler_location_epw,                 # noqa: E402
                          irradiancia_mensal_por_orientacao,
                          horas_por_mes, theta_ext_media_mensal,
                          theta_ext_anual_media)

PESO = {s.rb: s.peso for s in RB_SPECS}
RES = os.path.join(_AQUI, "resultados")

FALHAS = []
N_OK = 0


def chk(nome, ok, detalhe=""):
    global N_OK
    marca = "[PASS]" if ok else "[FALHA]"
    print(f"  {marca} {nome}" + (f"  — {detalhe}" if detalhe else ""))
    if ok:
        N_OK += 1
    else:
        FALHAS.append(nome)


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


REVISAO = dict(alfa_parede=0.40, desvao_cob=0.0, h_ce=20.0)

print("=" * 72)
print("V1 — I3: média ponderada de rácios (Tabela 7)")
print("=" * 72)
antes = _aplicar(REVISAO)
try:
    A = json.load(open(os.path.join(RES, "grelha_artigo13_REVISAO.json"), encoding="utf-8"))["celulas"]
    B = json.load(open(os.path.join(RES, "grelha_artigo13_2013_REVISAO.json"), encoding="utf-8"))["celulas"]
    dH_a = [(c["nh_52016"] / c["nic_13790"] - 1) * 100 for c in A]
    dH_b = [(c["nh_52016_2013"] / c["nic_13790_2013"] - 1) * 100 for c in B]
    pesos = [PESO[c["rb"]] for c in A]
    W = sum(pesos)
    mpr_a = sum(d * p for d, p in zip(dH_a, pesos)) / W
    mpr_b = sum(d * p for d, p in zip(dH_b, pesos)) / W
    chk("média ponderada de rácios DGEG2025-A ≈ +17,66%", abs(mpr_a - 17.66) < 0.05, f"{mpr_a:.2f}%")
    chk("média ponderada de rácios REG-2013 ≈ +9,82%", abs(mpr_b - 9.82) < 0.05, f"{mpr_b:.2f}%")
finally:
    _repor(antes)

print("\n" + "=" * 72)
print("V2 — I7a: cruzamento ingénuo RB6/Coimbra")
print("=" * 72)
antes = _aplicar(REVISAO)
try:
    irr, horas, th_m, th_a = g._ler_epw_cidade("Coimbra")
    clima_a = g._clima_dgeg2025_a("Coimbra", irr)
    nic_dgeg, _ = g.celula_13790("RB6", "Coimbra", clima_a)
    nh_dgeg, _, _ = g.celula_52016("RB6", (irr, horas, th_m, th_a))
    nic_2013, _ = g.celula_13790_2013("RB6", "Coimbra")
    from e4.clima_2013_mensal import SERIES_2013
    nh_2013, _, _ = g.celula_52016("RB6", SERIES_2013["Coimbra"])
    ingenuo = (nh_dgeg / nic_2013 - 1) * 100
    metodo_dgeg = (nh_dgeg / nic_dgeg - 1) * 100
    metodo_2013 = (nh_2013 / nic_2013 - 1) * 100
    chk("cruzamento ingénuo ≈ +11,19%", abs(ingenuo - 11.19) < 0.05, f"{ingenuo:.2f}%")
    chk("rácio DGEG/ingénuo ≈ 1,56 (não 'factor of two')",
        abs(metodo_dgeg / ingenuo - 1.56) < 0.02, f"{metodo_dgeg/ingenuo:.2f}")
finally:
    _repor(antes)

print("\n" + "=" * 72)
print("V3 — I9: banda de irradiação de referência (invariante à correção)")
print("=" * 72)
irr, _, _, _ = g._ler_epw_cidade("Coimbra")
gsul = sum(irr[m]["SV"] for m in g._MESES_FORA_JJAS) / len(g._MESES_FORA_JJAS)
chk("gsul Coimbra (fora-JJAS) ≈ 96,1 kWh/m²·mês (topo da banda submetida)",
    abs(gsul - 96.1) < 0.5, f"{gsul:.2f}")

print("\n" + "=" * 72)
print("V4 — F1: efeito de base (REG-2013 → DGEG2025-A), órfão até 01/08")
print("=" * 72)
antes = _aplicar(REVISAO)
try:
    A = json.load(open(os.path.join(RES, "grelha_artigo13_REVISAO.json"), encoding="utf-8"))["celulas"]
    B = json.load(open(os.path.join(RES, "grelha_artigo13_2013_REVISAO.json"), encoding="utf-8"))["celulas"]
    m = {(c["rb"], c["cidade"]): c for c in B}
    saz = [100 * (a["nic_13790"] / m[(a["rb"], a["cidade"])]["nic_13790_2013"] - 1) for a in A]
    men = [100 * (a["nh_52016"] / m[(a["rb"], a["cidade"])]["nh_52016_2013"] - 1) for a in A]
    chk("efeito de base, sazonal, mediana ≈ −0,1%", abs(st.median(saz) - (-0.1)) < 0.3,
        f"{st.median(saz):.2f}% [{min(saz):.1f};{max(saz):.1f}]")
    chk("efeito de base, mensal, mediana ≈ +7,1%", abs(st.median(men) - 7.1) < 0.3,
        f"{st.median(men):.2f}% [{min(men):.1f};{max(men):.1f}]")
finally:
    _repor(antes)

print("\n" + "=" * 72)
print("V5 — Coerência paramétrica A13 ↔ A14 (o ponto mais forte da auditoria Fable)")
print("=" * 72)
antes = _aplicar(REVISAO)
try:
    canon_p = os.path.join(_RAIZ, "studies", "a14_iso52016_horario", "resultados",
                           "grelha_a14_canonica.json")
    epw_dir = os.path.join(_RAIZ, "src", "e4", "fixtures", "clima_corrigido")
    if os.path.exists(canon_p) and os.path.isdir(epw_dir):
        canon = json.load(open(canon_p, encoding="utf-8"))
        cel = {(c["cidade"], c["rb"]): c for c in canon["celulas"] if c.get("alfa", 0.4) == 0.4}
        piores = []
        for cidade, fich in (("Coimbra", "Coimbra_255m"), ("Lisboa", "Lisboa_114m"),
                             ("Braganca", "Braganca_907m"), ("Evora", "Evora_296m")):
            cam = os.path.join(epw_dir, fich + ".epw")
            if not os.path.exists(cam):
                continue
            regs = ler_epw(cam); loc = ler_location_epw(cam)
            ser = (irradiancia_mensal_por_orientacao(regs, loc), horas_por_mes(regs),
                  theta_ext_media_mensal(regs), theta_ext_anual_media(regs))
            for rb in ("RB1", "RB6", "RB8"):
                if (cidade, rb) not in cel:
                    continue
                nh, nc, _ = g.celula_52016(rb, ser)
                ref = cel[(cidade, rb)]
                piores.append(max(abs(nh - ref["nh_men"]), abs(nc - ref["nc_men"])))
        if piores:
            chk("A13 revisto == braço mensal canónico do A14 (12 células)",
                max(piores) < 0.01, f"desvio máx {max(piores):.4f} kWh/m²·a")
        else:
            chk("V5 executável", False, "nenhuma célula de controlo disponível")
    else:
        chk("V5 executável", False, "grelha_a14_canonica.json ou clima_corrigido/ ausentes neste ambiente")
finally:
    _repor(antes)

print("\n" + "=" * 72)
print("V6 — Sensibilidade α=0,60 (S1): honesto sobre a não-monotonia")
print("=" * 72)
p60 = os.path.join(RES, "sensibilidade_alfa060_A13.json")
p60d = os.path.join(RES, "decomposicao_artigo13_alfa060.json")
if os.path.exists(p60):
    d60 = json.load(open(p60, encoding="utf-8"))
    dgeg60 = d60["dgeg2025a"]
    dH60 = [100 * (c["nh_52016"] - c["nic_13790"]) / c["nic_13790"] for c in dgeg60]
    chk("α=0,60 DGEG2025-A ΔH mediana ≈ +18,91%", abs(st.median(dH60) - 18.91) < 0.1,
        f"{st.median(dH60):.2f}%")
else:
    chk("sensibilidade_alfa060_A13.json presente", False, "correr sensibilidade_alfa060_A13.py")
if os.path.exists(p60d):
    d = json.load(open(p60d, encoding="utf-8"))["celulas"]
    gte1 = [c for c in d if c["gamma_C_sazonal"] >= 1]
    lt1 = [c for c in d if c["gamma_C_sazonal"] < 1]
    bem = sum(1 for c in gte1 if c["dC"] < 0) + sum(1 for c in lt1 if c["dC"] > 0)
    print(f"  [NOTA] segmentação γ_C bem classificada sob α=0,60: {bem}/32"
          f"  (α=0,40: 30/32 · submetido: 29/32) — NÃO é monótona em α; reportar como está.")
else:
    print("  [NOTA] decomposicao_artigo13_alfa060.json ausente — correr sensibilidade_alfa060_A13.py")

print("\n" + "=" * 72)
print(f"RESULTADO: {N_OK}/{N_OK + len(FALHAS)} PASS")
if FALHAS:
    print("Falhas:")
    for f in FALHAS:
        print(f"   • {f}")
print("=" * 72)
