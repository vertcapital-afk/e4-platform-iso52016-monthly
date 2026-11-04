# ---- ORDEM DE EXECUCAO OBRIGATORIA ----
# 1. gerar_figuras.py            -> Fig1..Fig7
# 2. gerar_figuras_8_9.py        -> Fig8, Fig9
# 3. gerar_figuras_fix_e_10.py   -> REESCREVE Fig1..Fig3, escreve Fig10
# Correr so o (1) deixa Fig1-Fig3 superadas em silencio.
#
# --- fonte de dados unica: dados_a13.py -----------------------------------
# [31/07/2026] O literal `T` com a base REG-2013, transcrito a mao, foi
# SUBSTITUIDO por leitura do JSON. Continha um erro de transposicao em
# RB2/Coimbra N_H que se propagou a todas as figuras da base 2013 e ao
# manuscrito submetido. Ler do JSON torna esse erro impossivel.
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from dados_a13 import carregar as _carregar, ESTADO as _ESTADO, sufixo_ficheiro as _sfx
_AQUI_F = _os.path.dirname(_os.path.abspath(__file__))
_RES_F = _os.path.join(_os.path.dirname(_AQUI_F), "resultados")
OUT = _os.path.join(_AQUI_F, "saida" + (_sfx() or "_submetido"))
_os.makedirs(OUT, exist_ok=True)
print("[dados] estado:", _ESTADO)
def _decomp(base_2013=False):
    n = "decomposicao_artigo13" + ("_2013" if base_2013 else "") + _sfx().upper() + ".json"
    import json as _j
    return _j.load(open(_os.path.join(_RES_F, n), encoding="utf-8"))

NOMES_FIGS = {
    1: "Fig1_cooling_threshold",
    2: "Fig2_method_effect_conditional",
    3: "Fig3_heatmap_dH",
    4: "Fig4_confound_cascade",
    5: "Fig5_parity_scatter",
    6: "Fig6_setpoint_scenario",
    7: "Fig7_base_effect_by_method",
}

"""Figuras do Artigo 13 — geradas a partir de grelha_artigo13.json (DGEG2025-A)
e da tabela REG-2013 do Handoff_Artigo13_08.md §2.2. Nenhum recálculo físico."""
import json, os
import numpy as np
np.random.seed(3)   # [01/08/2026] jitter reprodutivel (Fig.2)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5,
    "axes.linewidth": 0.7, "axes.edgecolor": "#333333",
    "axes.labelsize": 9, "axes.titlesize": 9.5, "axes.titleweight": "bold",
    "xtick.major.width": 0.7, "ytick.major.width": 0.7,
    "xtick.labelsize": 8, "ytick.labelsize": 8,
    "legend.fontsize": 8, "legend.frameon": False,
    "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
})

C13 = "#B45309"   # REG-2013  (ocre)
C25 = "#1D4E89"   # DGEG2025-A (azul)
GREY = "#6B7280"
ACC = "#9D174D"   # destaque

D = _carregar()
R = [[c["nic13"], c["nh13"], c["nvc13"], c["nc13"]] for c in D]
CITIES = ["Coimbra", "Bragança", "Évora", "Lisboa"]
RBS = [f"RB{i}" for i in range(1, 9)]

for i, c in enumerate(D):
    c["nic13"], c["nh13"], c["nvc13"], c["nc13"] = R[i]
    c["dH25"] = (c["nh_52016"] / c["nic_13790"] - 1) * 100
    c["dC25"] = (c["nc_52016"] / c["nvc_13790"] - 1) * 100
    c["dH13"] = (c["nh13"] / c["nic13"] - 1) * 100
    c["dC13"] = (c["nc13"] / c["nvc13"] - 1) * 100
    c["sfh"] = c["rb"] in RBS[:4]

def get(city=None, sfh=None):
    g = D
    if city: g = [c for c in g if c["cidade"] == city]
    if sfh is not None: g = [c for c in g if c["sfh"] == sfh]
    return g

def tag(ax, s):
    ax.text(-0.02, 1.06, s, transform=ax.transAxes, fontsize=10,
            fontweight="bold", ha="right", va="bottom")

# ---------------------------------------------------------------- FIG 1
# Assinatura: divergência de arrefecimento vs magnitude do resultado sazonal
fig, ax = plt.subplots(figsize=(6.6, 4.2))
ax.axhline(0, color=GREY, lw=0.7, ls="-", zorder=1)
for c in D:
    ax.scatter(c["nvc13"], c["dC13"], s=34, marker="s", facecolor="none",
               edgecolor=C13, lw=1.0, zorder=4)
    ax.scatter(c["nvc_13790"], c["dC25"], s=30, marker="o", color=C25,
               alpha=0.85, zorder=5)
ex = [c for c in D if c["rb"] == "RB2" and c["cidade"] == "Bragança"][0]
ax.annotate("RB2 / Bragança\n$N_{vc}$ = %.2f kWh/m²·a" % ex["nvc_13790"],
            xy=(ex["nvc_13790"], ex["dC25"]), xytext=(6.0, 150),
            fontsize=7.5, color="#111", ha="left",
            arrowprops=dict(arrowstyle="-", lw=0.7, color=GREY))
ax.set_xscale("log")
ax.set_xticks([1, 2, 5, 10, 20, 50])
ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.set_xlabel("Seasonal cooling need $N_{vc}$  [kWh/m²·a, log scale]")
ax.set_ylabel("Cooling divergence  $\\Delta_C$  [%]")
ax.set_title("The seasonal magnitude alone does not separate the regimes")
_n4 = sum(1 for c in D if c["nvc_13790"] < 4.0)
# [R1 03/11] A2: nota passada para a legenda da figura.
ax.legend(handles=[
    plt.Line2D([], [], marker="o", ls="", color=C25, label="DGEG2025-A base"),
    plt.Line2D([], [], marker="s", ls="", mfc="none", mec=C13, label="REG-2013 base")],
    loc="upper right", ncol=1)
for s_ in ("top", "right"): ax.spines[s_].set_visible(False)
fig.savefig(f"{OUT}/Fig1_cooling_threshold.png")
fig.savefig(f"{OUT}/Fig1_cooling_threshold.pdf")
fig.savefig(f"{OUT}/Fig1.pdf"); plt.close(fig)

# ---------------------------------------------------------------- FIG 2
# Distribuição do efeito de método: base, arquétipo, cidade
fig, axes = plt.subplots(1, 3, figsize=(7.4, 3.5),
                         gridspec_kw={"width_ratios": [1, 1, 1.9], "wspace": 0.36})
def box(ax, data, labels, colors, title, xlab):
    bp = ax.boxplot(data, patch_artist=True, widths=0.55, showfliers=False,
                    medianprops=dict(color="#111", lw=1.4),
                    whiskerprops=dict(lw=0.8, color=GREY),
                    capprops=dict(lw=0.8, color=GREY))
    for p, col in zip(bp["boxes"], colors):
        p.set(facecolor=col, alpha=0.28, edgecolor=col, lw=1.0)
    for i, d in enumerate(data):
        ax.scatter(np.random.normal(i + 1, 0.055, len(d)), d, s=8,
                   color=colors[i], alpha=0.75, zorder=3, lw=0)
    ax.axhline(0, color=GREY, lw=0.7)
    ax.set_xticks(range(1, len(labels) + 1)); ax.set_xticklabels(labels)
    ax.set_title(title); ax.set_xlabel(xlab)
    for s in ("top", "right"): ax.spines[s].set_visible(False)

box(axes[0], [[c["dH13"] for c in D], [c["dH25"] for c in D]],
    ["REG\n2013", "DGEG\n2025-A"], [C13, C25], "By climate base", "")
axes[0].set_ylabel("Heating divergence  $\\Delta_H$  [%]")
box(axes[1], [[c["dH25"] for c in get(sfh=True)], [c["dH25"] for c in get(sfh=False)]],
    ["SFH", "MFH"], [C25, C25], "By archetype", "")
box(axes[2], [[c["dH25"] for c in get(city=k)] for k in CITIES],
    ["Coim.", "Brag.", "Évora", "Lisb."], [C25] * 4, "By city", "")
for a in axes[1:]: a.set_ylim(axes[0].get_ylim())
tag(axes[0], "a"); tag(axes[1], "b"); tag(axes[2], "c")
fig.suptitle("The method effect is conditional, not constant", y=1.02,
             fontsize=10, fontweight="bold")
fig.savefig(f"{OUT}/Fig2_method_effect_conditional.png")
fig.savefig(f"{OUT}/Fig2_method_effect_conditional.pdf")
fig.savefig(f"{OUT}/Fig2.pdf"); plt.close(fig)

# ---------------------------------------------------------------- FIG 3
# Heatmaps ΔH nas duas bases
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1))
M13 = np.array([[[c for c in D if c["rb"] == r and c["cidade"] == k][0]["dH13"]
                 for r in RBS] for k in CITIES])
M25 = np.array([[[c for c in D if c["rb"] == r and c["cidade"] == k][0]["dH25"]
                 for r in RBS] for k in CITIES])
vm = max(abs(M13).max(), abs(M25).max())
for ax, M, t in zip(axes, [M13, M25], ["REG-2013 base", "DGEG2025-A base"]):
    im = ax.imshow(M, cmap="RdBu_r", vmin=-vm, vmax=vm, aspect="auto")
    ax.set_xticks(range(8)); ax.set_xticklabels(RBS, fontsize=7.5)
    ax.set_yticks(range(4)); ax.set_yticklabels(CITIES, fontsize=8)
    ax.set_title(t, fontsize=9)
    for i in range(4):
        for j in range(8):
            v = M[i, j]
            ax.text(j, i, f"{v:+.0f}", ha="center", va="center", fontsize=6.6,
                    color="white" if abs(v) > 0.55 * vm else "#111")
    ax.set_xticks(np.arange(-.5, 8, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 4, 1), minor=True)
    ax.grid(which="minor", color="white", lw=1.1); ax.tick_params(which="minor", size=0)
cb = fig.colorbar(im, ax=axes, fraction=0.028, pad=0.02)
cb.set_label("$\\Delta_H$  [%]", fontsize=8.5); cb.ax.tick_params(labelsize=7.5)
fig.suptitle("Heating divergence across the 32 building×city combinations",
             y=1.02, fontsize=10, fontweight="bold")
fig.savefig(f"{OUT}/Fig3_heatmap_dH.png")
fig.savefig(f"{OUT}/Fig3_heatmap_dH.pdf")
fig.savefig(f"{OUT}/Fig3.pdf"); plt.close(fig)

# ---------------------------------------------------------------- FIG 4
# [R1 03/11, decisor] Tres contrastes nominais recuperaveis (proposta de auditoria, aceite):
# sem a barra dos +70 % (irreprodutivel) nem a dos +21 % (altitude, historica).
c=next(c for c in D if c['rb']=='RB6' and c['cidade']=='Coimbra')
vals=[100*(c['nh_52016']/c['nic13']-1),c['dH13'],c['dH25']]
fig,ax=plt.subplots(figsize=(6.0,3.3))
labels=['Naive cross-base','Method effect\nREG-2013','Method effect\nDGEG2025-A']
bars=ax.bar(range(3),vals,color=[GREY,C13,C25],width=.62)
for b,v in zip(bars,vals):
    ax.text(b.get_x()+b.get_width()/2,v+.3,f'{v:+.1f}%',ha='center')
ax.set_xticks(range(3));ax.set_xticklabels(labels)
ax.set_ylabel('Heating divergence [%]')
ax.set_title('RB6 / Coimbra')
ax.set_ylim(0,max(vals)*1.25)
for s_ in("top","right"): ax.spines[s_].set_visible(False)
for ext in ['png','pdf']:
    fig.savefig(f'{OUT}/Fig4_confound_cascade.{ext}')
    fig.savefig(f'{OUT}/Fig4_graphical_abstract.{ext}')
fig.savefig(f'{OUT}/Fig4.pdf');plt.close(fig)

# ---------------------------------------------------------------- FIG 5
# Paridade: sazonal vs mensal, aquecimento, duas bases
fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.5), sharex=True, sharey=True)
mk = {"Coimbra": "o", "Bragança": "^", "Évora": "s", "Lisboa": "D"}
for ax, (xs, ys, col, t) in zip(axes, [
        ("nic13", "nh13", C13, "REG-2013 base"),
        ("nic_13790", "nh_52016", C25, "DGEG2025-A base")]):
    lim = [0, 380]
    ax.plot(lim, lim, color=GREY, lw=0.8, ls="--", zorder=1)
    for c in D:
        ax.scatter(c[xs], c[ys], s=30, marker=mk[c["cidade"]],
                   facecolor=col if c["sfh"] else "none", edgecolor=col,
                   lw=1.0, alpha=0.9, zorder=3)
    ax.set_xlim(lim); ax.set_ylim(lim); ax.set_aspect("equal")
    ax.set_title(t, fontsize=9); ax.set_xlabel("Seasonal  $N_{ic}$  [kWh/m²·a]")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
axes[0].set_ylabel("Monthly  $N_H$  [kWh/m²·a]")
h = [plt.Line2D([], [], marker=mk[k], ls="", color=GREY, label=k) for k in CITIES]
h += [plt.Line2D([], [], marker="o", ls="", color=GREY, label="SFH (filled)"),
      plt.Line2D([], [], marker="o", ls="", mfc="none", mec=GREY, label="MFH (open)")]
axes[1].legend(handles=h, loc="lower right", fontsize=6.8, ncol=2)
fig.suptitle("Monthly versus seasonal heating needs, envelope parity enforced",
             y=1.0, fontsize=10, fontweight="bold")
fig.savefig(f"{OUT}/Fig5_parity_scatter.png")
fig.savefig(f"{OUT}/Fig5_parity_scatter.pdf")
fig.savefig(f"{OUT}/Fig5.pdf"); plt.close(fig)

# ---------------------------------------------------------------- FIG 6
# Cenário 20 °C
fig, ax = plt.subplots(figsize=(6.2, 3.3))
w = 0.19
x = np.arange(8)
for i, k in enumerate(CITIES):
    up = [(c["nh20_52016_cenario"] / c["nh_52016"] - 1) * 100
          for r in RBS for c in D if c["rb"] == r and c["cidade"] == k]
    ax.bar(x + (i - 1.5) * w, up, width=w, label=k,
           color=plt.cm.viridis(i / 3.4), alpha=0.9)
ax.set_xticks(x); ax.set_xticklabels(RBS)
ax.set_ylabel("Increase in $N_H$  [%]")
ax.set_title("Prospective setpoint scenario: 18 °C → 20 °C (monthly axis)")
ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.16))
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.savefig(f"{OUT}/Fig6_setpoint_scenario.png")
fig.savefig(f"{OUT}/Fig6_setpoint_scenario.pdf")
fig.savefig(f"{OUT}/Fig6.pdf"); plt.close(fig)

# ---------------------------------------------------------------- FIG 7
# Efeito de base por método (slopegraph agregado)
fig, ax = plt.subplots(figsize=(4.6, 3.6))
for c in D:
    ax.plot([0, 1], [c["nic13"], c["nic_13790"]], color=C13, lw=0.6, alpha=0.4)
    ax.plot([2, 3], [c["nh13"], c["nh_52016"]], color=C25, lw=0.6, alpha=0.4)
for pos, key, col in [(0, "nic13", C13), (1, "nic_13790", C13),
                      (2, "nh13", C25), (3, "nh_52016", C25)]:
    ax.scatter([pos] * 32, [c[key] for c in D], s=12, color=col, zorder=3, alpha=0.8)
ax.set_xticks([0, 1, 2, 3])
ax.set_xticklabels(["2013", "2025", "2013", "2025"], fontsize=8)
ax.text(0.5, -0.155, "Seasonal", transform=ax.get_xaxis_transform(),
        ha="center", fontsize=8.5, color=C13, fontweight="bold")
ax.text(2.5, -0.155, "Monthly", transform=ax.get_xaxis_transform(),
        ha="center", fontsize=8.5, color=C25, fontweight="bold")
ax.set_ylabel("Heating need  [kWh/m²·a]")
_ms = np.median([(c["nic_13790"]/c["nic13"]-1)*100 for c in D])
_mm = np.median([(c["nh_52016"]/c["nh13"]-1)*100 for c in D])
ax.set_title("Response of each method to a change of\nclimate base (median %+.1f %% vs %+.1f %%)" % (_ms, _mm),
             fontsize=9)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.savefig(f"{OUT}/Fig7_base_effect_by_method.png")
fig.savefig(f"{OUT}/Fig7_base_effect_by_method.pdf")
fig.savefig(f"{OUT}/Fig7.pdf"); plt.close(fig)

print("OK ->", sorted(os.listdir(OUT)))
