# -*- coding: utf-8 -*-
"""numeros_revisao.py — resumo estatístico dos dados depositados do A13 R1.

Saída: resultados/NUMEROS_revisao_A13.md (não editar à mão; regenerar).
Lê só ficheiros deste depósito: as duas grelhas R1 (resultados/) e os pesos do
parque transcritos em figures/estatisticas.py (lidos sem o executar). Não precisa
do motor.

É um resumo de estatísticas calculadas dos dados depositados, não uma verificação
exaustiva do manuscrito. A verificação, com âncoras e controlos negativos, é
scripts/verificar_revisao_a13.py.

Uso (Windows: «py»):  py figures\\numeros_revisao.py
A saída é determinística: regenerar e confirmar que o git não mostra diferenças.

Substitui a versão publicada com a submissão, que comparava o estado da versão
JBE com o de 31/07/2026, importava os pesos do motor privado e lia duas grelhas
que não estavam no depósito. Essa versão fica na tag
public-before-R1-ENB-D-26-06604.
"""
import ast
import json
import os
import statistics as st
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_A = os.path.dirname(os.path.abspath(__file__))
_RES = os.path.join(os.path.dirname(_A), "resultados")
SFH = ("RB1", "RB2", "RB3", "RB4")
CIDADES = ("Coimbra", "Bragança", "Évora", "Lisboa")


def pesos():
    """Os pesos do parque de figures/estatisticas.py (dicionário W), sem o executar."""
    with open(os.path.join(_A, "estatisticas.py"), encoding="utf-8") as f:
        arvore = ast.parse(f.read())
    for no in ast.walk(arvore):
        if isinstance(no, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "W" for t in no.targets):
            return ast.literal_eval(no.value)
    raise SystemExit("⛔ pesos W não encontrados em figures/estatisticas.py")


def ler():
    def j(nome):
        with open(os.path.join(_RES, nome), encoding="utf-8") as f:
            return json.load(f)["celulas"]
    a = j("grelha_artigo13_REVISAO.json")
    b = {(c["rb"], c["cidade"]): c for c in j("grelha_artigo13_2013_REVISAO.json")}
    if len(a) != 32 or len(b) != 32:
        raise SystemExit(f"⛔ esperava 32 + 32 células, obtive {len(a)} + {len(b)}")
    for c in a:
        d = b[(c["rb"], c["cidade"])]
        c["nic13"], c["nh13"] = d["nic_13790_2013"], d["nh_52016_2013"]
        c["nvc13"], c["nc13"] = d["nvc_13790_2013"], d["nc_52016_2013"]
        c["dH25"] = (c["nh_52016"] / c["nic_13790"] - 1) * 100
        c["dC25"] = (c["nc_52016"] / c["nvc_13790"] - 1) * 100
        c["dH13"] = (c["nh13"] / c["nic13"] - 1) * 100
        c["dC13"] = (c["nc13"] / c["nvc13"] - 1) * 100
    return a


PESO = pesos()
V = ler()
L = []
w = L.append


def q(v):
    return st.quantiles(v, n=4)


def resumo(v):
    return (f"med {st.median(v):+.1f}% · IQR [{q(v)[0]:+.1f}; {q(v)[2]:+.1f}] · "
            f"[{min(v):+.1f}; {max(v):+.1f}] · neg {sum(1 for x in v if x < 0)}/32")


def agregado(num, den):
    """Médias ponderadas pelo parque (cidades equiponderadas dentro de cada RB)."""
    n = d = 0.0
    for rb, p in PESO.items():
        g = [c for c in V if c["rb"] == rb]
        n += p * sum(c[num] for c in g) / len(g)
        d += p * sum(c[den] for c in g) / len(g)
    tw = sum(PESO.values())
    return d / tw, n / tw, (n / d - 1) * 100


def media_racios(k):
    tw = sum(PESO[c["rb"]] for c in V)
    return sum(PESO[c["rb"]] * c[k] for c in V) / tw


w("# NÚMEROS DA REVISÃO R1 — Artigo 13\n")
w("Resumo de estatísticas calculadas dos dados depositados do R1 (Energy & Buildings, "
  "ENB-D-26-06604; manuscrito em revisão, não aceite nem publicado). **Não é uma verificação "
  "exaustiva do manuscrito**: a verificação, com âncoras e controlos negativos, é "
  "`scripts/verificar_revisao_a13.py`.\n")
w("Gerado por `figures/numeros_revisao.py` a partir de `resultados/grelha_artigo13_REVISAO.json` "
  "(DGEG2025-A, hora solar verificada) e `resultados/grelha_artigo13_2013_REVISAO.json` "
  "(REG-2013, clima tabelado). **Não editar à mão**: regenerar com `py figures\\numeros_revisao.py`.\n")
w("Configuração R1: α_parede 0,40 e desvão 0 **nos dois ramos**, h_ce 20,0 no ramo mensal. "
  "Δ = método mensal (ISO 52016-1) face ao sazonal (ISO 13790), em percentagem do sazonal. "
  "Necessidades em kWh/m²·a.\n")

w("\n## 1. Efeito de método — global (n = 32 por base)\n")
w("| grandeza | mediana · IQR · [mín; máx] · negativas |")
w("|---|---|")
for k, lab in (("dH25", "Δ_H DGEG2025-A"), ("dH13", "Δ_H REG-2013"),
               ("dC25", "Δ_C DGEG2025-A"), ("dC13", "Δ_C REG-2013")):
    w(f"| {lab} | {resumo([c[k] for c in V])} |")

w("\n## 2. Necessidades medianas — o denominador visível\n")
w("| grandeza | mediana |")
w("|---|---|")
for k, lab in (("nic_13790", "N_ic sazonal (DGEG2025-A)"), ("nh_52016", "N_H mensal (DGEG2025-A)"),
               ("nvc_13790", "N_vc sazonal (DGEG2025-A)"), ("nc_52016", "N_C mensal (DGEG2025-A)"),
               ("nic13", "N_ic sazonal (REG-2013)"), ("nh13", "N_H mensal (REG-2013)"),
               ("nvc13", "N_vc sazonal (REG-2013)"), ("nc13", "N_C mensal (REG-2013)")):
    w(f"| {lab} | {st.median([c[k] for c in V]):.2f} |")

w("\n## 3. Unifamiliares (RB1–RB4) e multifamiliares (RB5–RB8) — medianas\n")
w("| grupo | Δ_H DGEG2025-A | Δ_H REG-2013 | Δ_C DGEG2025-A | Δ_C REG-2013 |")
w("|---|---|---|---|---|")
for g, f in (("unifamiliares", True), ("multifamiliares", False)):
    sub = [c for c in V if (c["rb"] in SFH) == f]
    w(f"| {g} | " + " | ".join(f"{st.median([c[k] for c in sub]):+.1f}%"
                              for k in ("dH25", "dH13", "dC25", "dC13")) + " |")

w("\n## 4. Agregado ponderado pelo parque\n")
w("Pesos do parque (Census) de `figures/estatisticas.py`; cidades equiponderadas em cada arquétipo. "
  "O efeito é o rácio das necessidades ponderadas, não a média dos rácios.\n")
w("| base / uso | sazonal | mensal | efeito |")
w("|---|---|---|---|")
for lab, num, den in (("DGEG2025-A aquecimento", "nh_52016", "nic_13790"),
                      ("DGEG2025-A arrefecimento", "nc_52016", "nvc_13790"),
                      ("REG-2013 aquecimento", "nh13", "nic13"),
                      ("REG-2013 arrefecimento", "nc13", "nvc13")):
    s, m, e = agregado(num, den)
    w(f"| {lab} | {s:.2f} | {m:.2f} | **{e:+.1f}%** |")
w(f"\nMédia ponderada dos rácios (aquecimento), para comparação: DGEG2025-A "
  f"{media_racios('dH25'):+.2f}%, REG-2013 {media_racios('dH13'):+.2f}%.\n")

w("\n## 5. Por cidade — medianas\n")
w("| cidade | Δ_H DGEG2025-A | Δ_H REG-2013 | Δ_C DGEG2025-A | Δ_C REG-2013 |")
w("|---|---|---|---|---|")
for cid in CIDADES:
    g = [c for c in V if c["cidade"] == cid]
    w(f"| {cid} | " + " | ".join(f"{st.median([c[k] for c in g]):+.1f}%"
                                for k in ("dH25", "dH13", "dC25", "dC13")) + " |")

w("\n## 6. Efeito de base (REG-2013 → DGEG2025-A), mesmo método\n")
w("| grandeza | mediana | [mín; máx] |")
w("|---|---|---|")
for lab, a, b in (("aquecimento, sazonal", "nic_13790", "nic13"), ("aquecimento, mensal", "nh_52016", "nh13"),
                  ("arrefecimento, sazonal", "nvc_13790", "nvc13"), ("arrefecimento, mensal", "nc_52016", "nc13")):
    v = [(c[a] / c[b] - 1) * 100 for c in V]
    w(f"| {lab} | {st.median(v):+.1f}% | [{min(v):+.1f}; {max(v):+.1f}] |")

c = next(x for x in V if x["rb"] == "RB6" and x["cidade"] == "Coimbra")
w("\n## 7. RB6/Coimbra — os quatro cantos e o cruzamento ingénuo\n")
w("| base | N_ic sazonal | N_H mensal | Δ_H |")
w("|---|---|---|---|")
w(f"| REG-2013 | {c['nic13']:.2f} | {c['nh13']:.2f} | {c['dH13']:+.1f}% |")
w(f"| DGEG2025-A | {c['nic_13790']:.2f} | {c['nh_52016']:.2f} | {c['dH25']:+.1f}% |")
w(f"\nCruzamento ingénuo N_H(DGEG2025-A) / N_ic(REG-2013): {(c['nh_52016'] / c['nic13'] - 1) * 100:+.1f}% "
  f"(calculado das grelhas a 3 casas; o valor de precisão completa está em "
  f"`resultados/cruzamento_ingenuo_rb6_coimbra_REVISAO.json`).\n")

for titulo, kic, kh, kvc, kc, kdh, kdc in (
        ("8. Por célula — base DGEG2025-A", "nic_13790", "nh_52016", "nvc_13790", "nc_52016", "dH25", "dC25"),
        ("9. Por célula — base REG-2013", "nic13", "nh13", "nvc13", "nc13", "dH13", "dC13")):
    w(f"\n## {titulo}\n")
    w("| RB | cidade | N_ic | N_H | N_vc | N_C | Δ_H | Δ_C |")
    w("|---|---|---|---|---|---|---|---|")
    for x in V:
        w(f"| {x['rb']} | {x['cidade']} | {x[kic]:.2f} | {x[kh]:.2f} | {x[kvc]:.3f} | "
          f"{x[kc]:.3f} | {x[kdh]:+.1f}% | {x[kdc]:+.1f}% |")

w("\n## 10. Denominadores pequenos — absolutos ao lado\n")
w("As cinco células de menor N_vc sazonal na base DGEG2025-A, onde as percentagens enganam:\n")
w("| cidade | RB | N_vc sazonal | N_C mensal | Δ absoluto | Δ % |")
w("|---|---|---|---|---|---|")
for x in sorted(V, key=lambda x: x["nvc_13790"])[:5]:
    w(f"| {x['cidade']} | {x['rb']} | {x['nvc_13790']:.2f} | {x['nc_52016']:.2f} | "
      f"{x['nc_52016'] - x['nvc_13790']:+.2f} | {x['dC25']:+.1f}% |")

_DEST = os.path.join(_RES, "NUMEROS_revisao_A13.md")
with open(_DEST, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(L) + "\n")
print("gerado:", _DEST, "|", len(L), "linhas")
