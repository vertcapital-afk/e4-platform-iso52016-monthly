# -*- coding: utf-8 -*-
"""numeros_revisao.py — todos os números que o manuscrito cita, submetido vs revisto.
Saída: NUMEROS_revisao_A13.md (para a sessão de escrita).
Doutrina: absolutos ao lado das percentagens, com o denominador visível."""
import os, sys, json, statistics as st
_A = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, _A)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(_A)), "src"))
_RES = os.path.join(os.path.dirname(_A), "resultados")
from e4.matriz_nacional import RB_SPECS
PESO = {s.rb: s.peso for s in RB_SPECS}
SFH = ("RB1", "RB2", "RB3", "RB4")

def ler(sfx):
    a = json.load(open(os.path.join(_RES, f"grelha_artigo13{sfx}.json"), encoding="utf-8"))["celulas"]
    b = {(c["rb"], c["cidade"]): c for c in json.load(
        open(os.path.join(_RES, f"grelha_artigo13_2013{sfx}.json"), encoding="utf-8"))["celulas"]}
    for c in a:
        d = b[(c["rb"], c["cidade"])]
        c["nic13"], c["nh13"] = d["nic_13790_2013"], d["nh_52016_2013"]
        c["nvc13"], c["nc13"] = d["nvc_13790_2013"], d["nc_52016_2013"]
        c["dH25"] = (c["nh_52016"]/c["nic_13790"]-1)*100
        c["dC25"] = (c["nc_52016"]/c["nvc_13790"]-1)*100
        c["dH13"] = (c["nh13"]/c["nic13"]-1)*100
        c["dC13"] = (c["nc13"]/c["nvc13"]-1)*100
    return a

S, V = ler(""), ler("_REVISAO")
L = []
w = L.append
w("# NÚMEROS DA REVISÃO — Artigo 13\n")
w("**31/07/2026 · [P-alfa-A13-paridade]**\n")
w("Gerado por `studies/a13_iso52016_mensal/figures/numeros_revisao.py`.\n")
w("Vive em `studies/a13_iso52016_mensal/resultados/`. **Nao editar a mao** —\n")
w("regenerar com `py studies\\a13_iso52016_mensal\\figures\\numeros_revisao.py`.\n")
w("Submetido = estado JBE. Revisto = α_parede 0,40 + desvão 0 **nos dois ramos** + h_ce 20,0.\n")

def q(v): return st.quantiles(v, n=4)
w("\n## 1. Efeito de método — global (n=32)\n")
w("| grandeza | submetido | revisto |")
w("|---|---|---|")
for k, lab in (("dH25","ΔH DGEG2025-A"),("dH13","ΔH REG-2013"),
               ("dC25","ΔC DGEG2025-A"),("dC13","ΔC REG-2013")):
    f = lambda D: (f"med {st.median([c[k] for c in D]):+.1f}% · IQR "
                   f"[{q([c[k] for c in D])[0]:+.1f}; {q([c[k] for c in D])[2]:+.1f}] · "
                   f"neg {sum(1 for c in D if c[k]<0)}/32")
    w(f"| {lab} | {f(S)} | {f(V)} |")

w("\n## 2. Necessidades medianas (kWh/m²·a) — o denominador visível\n")
w("| grandeza | submetido | revisto |")
w("|---|---|---|")
for k, lab in (("nic_13790","N_ic 13790 (DGEG)"),("nh_52016","N_H 52016 (DGEG)"),
               ("nvc_13790","N_vc 13790 (DGEG)"),("nc_52016","N_C 52016 (DGEG)"),
               ("nic13","N_ic 13790 (2013)"),("nh13","N_H 52016 (2013)"),
               ("nvc13","N_vc 13790 (2013)"),("nc13","N_C 52016 (2013)")):
    w(f"| {lab} | {st.median([c[k] for c in S]):.2f} | {st.median([c[k] for c in V]):.2f} |")

w("\n## 3. Tabela 6 — SFH vs MFH (medianas)\n")
w("| grupo | ΔH DGEG | ΔH 2013 | ΔC DGEG | ΔC 2013 |")
w("|---|---|---|---|---|")
for lab, D, tag in (("submetido", S, ""), ("revisto", V, "")):
    for g, f in (("SFH", True), ("MFH", False)):
        sub = [c for c in D if (c["rb"] in SFH) == f]
        w(f"| {g} {lab} | {st.median([c['dH25'] for c in sub]):+.1f}% | "
          f"{st.median([c['dH13'] for c in sub]):+.1f}% | "
          f"{st.median([c['dC25'] for c in sub]):+.1f}% | "
          f"{st.median([c['dC13'] for c in sub]):+.1f}% |")

w("\n## 4. Tabela 7 — ponderado pelo stock\n")
w("| base / grandeza | 13790 | 52016 | efeito | (submetido) |")
w("|---|---|---|---|---|")
def pw(D, k): 
    W = sum(PESO[c["rb"]] for c in D)
    return sum(c[k]*PESO[c["rb"]] for c in D)/W
for base, k13, k52 in (("DGEG2025-A aquec","nic_13790","nh_52016"),
                       ("DGEG2025-A arref","nvc_13790","nc_52016"),
                       ("REG-2013 aquec","nic13","nh13"),
                       ("REG-2013 arref","nvc13","nc13")):
    a, b = pw(V,k13), pw(V,k52); a0, b0 = pw(S,k13), pw(S,k52)
    w(f"| {base} | {a:.2f} | {b:.2f} | **{100*(b-a)/a:+.1f}%** | ({100*(b0-a0)/a0:+.1f}%) |")

w("\n## 5. Por cidade — medianas\n")
w("| cidade | ΔH DGEG sub→rev | ΔH 2013 sub→rev | ΔC DGEG sub→rev | ΔC 2013 sub→rev |")
w("|---|---|---|---|---|")
for cid in ("Coimbra","Bragança","Évora","Lisboa"):
    gs=[c for c in S if c["cidade"]==cid]; gv=[c for c in V if c["cidade"]==cid]
    cel=lambda k: (f"{st.median([c[k] for c in gs]):+.1f} → "
                   f"**{st.median([c[k] for c in gv]):+.1f}**")
    w(f"| {cid} | {cel('dH25')} | {cel('dH13')} | {cel('dC25')} | {cel('dC13')} |")

w("\n## 6. Tabela S1 REVISTA — base DGEG2025-A\n")
w("| RB | cidade | N_ic 13790 | N_H 52016 | N_vc 13790 | N_C 52016 | ΔH | ΔC |")
w("|---|---|---|---|---|---|---|---|")
for c in V:
    w(f"| {c['rb']} | {c['cidade']} | {c['nic_13790']:.2f} | {c['nh_52016']:.2f} | "
      f"{c['nvc_13790']:.3f} | {c['nc_52016']:.3f} | {c['dH25']:+.1f}% | {c['dC25']:+.1f}% |")

w("\n## 7. Tabela S2 REVISTA — base REG-2013\n")
w("| RB | cidade | N_ic 13790 | N_H 52016 | N_vc 13790 | N_C 52016 | ΔH | ΔC |")
w("|---|---|---|---|---|---|---|---|")
for c in V:
    w(f"| {c['rb']} | {c['cidade']} | {c['nic13']:.2f} | {c['nh13']:.2f} | "
      f"{c['nvc13']:.3f} | {c['nc13']:.3f} | {c['dH13']:+.1f}% | {c['dC13']:+.1f}% |")

w("\n## 8. Denominadores pequenos — absolutos ao lado (regra do projecto)\n")
w("As 5 células de menor N_vc (13790) na base DGEG2025-A, onde as % enganam:\n")
w("| cidade | RB | N_vc 13790 | N_C 52016 | Δ absoluto | Δ % |")
w("|---|---|---|---|---|---|")
for c in sorted(V, key=lambda c: c["nvc_13790"])[:5]:
    w(f"| {c['cidade']} | {c['rb']} | {c['nvc_13790']:.2f} | {c['nc_52016']:.2f} | "
      f"{c['nc_52016']-c['nvc_13790']:+.2f} | {c['dC25']:+.1f}% |")

# Dado gerado -> resultados/ (o script vive em figures/, o produto nao).
_DEST = os.path.join(_RES, "NUMEROS_revisao_A13.md")
open(_DEST, "w", encoding="utf-8").write("\n".join(L))
print("gerado:", _DEST, "|", len(L), "linhas")
