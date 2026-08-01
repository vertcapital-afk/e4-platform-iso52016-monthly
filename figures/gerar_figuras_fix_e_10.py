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

import json, os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8.5,"axes.linewidth":0.7,
 "axes.edgecolor":"#333","axes.labelsize":9,"axes.titlesize":9.5,"axes.titleweight":"bold",
 "xtick.labelsize":8,"ytick.labelsize":8,"legend.fontsize":8,"legend.frameon":False,
 "figure.dpi":300,"savefig.dpi":300,"savefig.bbox":"tight"})
C13="#B45309"; C25="#1D4E89"; GREY="#6B7280"; ACC="#9D174D"
D = _carregar()
R = [[c["nic13"], c["nh13"], c["nvc13"], c["nc13"]] for c in D]
CITIES=["Coimbra","Bragança","Évora","Lisboa"]; RBS=[f"RB{i}" for i in range(1,9)]
for i,c in enumerate(D):
    c["nvc13"],c["nc13"]=R[i][2],R[i][3]
    c["dC25"]=(c["nc_52016"]/c["nvc_13790"]-1)*100
    c["dC13"]=(R[i][3]/R[i][2]-1)*100
    c["dH25"]=(c["nh_52016"]/c["nic_13790"]-1)*100
    c["dH13"]=(R[i][1]/R[i][0]-1)*100

# ---- FIG 1 (revista 01/08/2026): o proxy dimensional NAO separa ----
# [01/08/2026] A versao anterior desenhava um limiar de 4 kWh/m2.a e anunciava
# "median +93%" / "median -7%" como texto FIXO. Sob [P-alfa-A13-paridade] o
# proxy cai de 11 para 3 celulas e deixa de separar: o criterio que carrega o
# resultado e o gamma_C adimensional (Fig. 8). Anotacoes agora CALCULADAS.
fig,ax=plt.subplots(figsize=(6.6,4.2))
ax.axhline(0,color=GREY,lw=0.7)
for c in D:
    ax.scatter(c["nvc13"],c["dC13"],s=34,marker="s",facecolor="none",edgecolor=C13,lw=1.0,zorder=4)
    ax.scatter(c["nvc_13790"],c["dC25"],s=30,marker="o",color=C25,alpha=0.85,zorder=5)
ex=[c for c in D if c["rb"]=="RB2" and c["cidade"]=="Bragança"][0]
ax.annotate("RB2 / Bragança\n$N_{vc}$ = %.2f kWh/m²·a" % ex["nvc_13790"],
            xy=(ex["nvc_13790"],ex["dC25"]),xytext=(6.5,150),fontsize=7.5,ha="left",
            arrowprops=dict(arrowstyle="-",lw=0.7,color=GREY))
ax.set_xscale("log"); ax.set_xticks([1,2,5,10,20,50])
ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.set_xlabel("Seasonal cooling need $N_{vc}$  [kWh/m²·a, log scale]")
ax.set_ylabel("Cooling divergence  $\\Delta_C$  [%]")
ax.set_title("The seasonal magnitude alone does not separate the regimes")
_n4=sum(1 for c in D if c["nvc_13790"]<4.0)
ax.text(0.98,0.05,"only %d of 32 cells fall below 4 kWh/m²·a;\nthe separating criterion is $\\gamma_C$ (Fig. 8)"%_n4,
        transform=ax.transAxes,fontsize=7.2,color=GREY,ha="right",style="italic")
ax.legend(handles=[plt.Line2D([],[],marker="o",ls="",color=C25,label="DGEG2025-A base"),
 plt.Line2D([],[],marker="s",ls="",mfc="none",mec=C13,label="REG-2013 base")],
 loc="upper right",fontsize=7.2)
_lo=min(min(c["dC13"] for c in D),min(c["dC25"] for c in D))
_hi=max(max(c["dC13"] for c in D),max(c["dC25"] for c in D))
ax.set_ylim(_lo-25,_hi+45)
for s_ in("top","right"): ax.spines[s_].set_visible(False)
fig.savefig(f"{OUT}/Fig1_cooling_threshold.png"); plt.close(fig)

# ---- FIG 2 (corrigida): nomes completos no painel c ----
def box(ax,data,labels,colors,title):
    bp=ax.boxplot(data,patch_artist=True,widths=0.55,showfliers=False,
        medianprops=dict(color="#111",lw=1.4),whiskerprops=dict(lw=0.8,color=GREY),
        capprops=dict(lw=0.8,color=GREY))
    for p,col in zip(bp["boxes"],colors): p.set(facecolor=col,alpha=0.28,edgecolor=col,lw=1.0)
    for i,d in enumerate(data):
        ax.scatter(np.random.normal(i+1,0.055,len(d)),d,s=8,color=colors[i],alpha=0.75,zorder=3,lw=0)
    ax.axhline(0,color=GREY,lw=0.7)
    ax.set_xticks(range(1,len(labels)+1)); ax.set_xticklabels(labels,fontsize=7.6)
    ax.set_title(title)
    for s in("top","right"): ax.spines[s].set_visible(False)
np.random.seed(3)
fig,axes=plt.subplots(1,3,figsize=(7.6,3.5),gridspec_kw={"width_ratios":[1,1,2.1],"wspace":0.34})
box(axes[0],[[c["dH13"] for c in D],[c["dH25"] for c in D]],["REG\n2013","DGEG\n2025-A"],[C13,C25],"By climate base")
axes[0].set_ylabel("Heating divergence  $\\Delta_H$  [%]")
sf=lambda f:[c["dH25"] for c in D if (c["rb"] in RBS[:4])==f]
box(axes[1],[sf(True),sf(False)],["SFH","MFH"],[C25,C25],"By archetype")
box(axes[2],[[c["dH25"] for c in D if c["cidade"]==k] for k in CITIES],CITIES,[C25]*4,"By city")
for a in axes[1:]: a.set_ylim(axes[0].get_ylim())
for a,t in zip(axes,"abc"):
    a.text(-0.02,1.06,t,transform=a.transAxes,fontsize=10,fontweight="bold",ha="right",va="bottom")
fig.suptitle("The method effect is conditional, not constant",y=1.02,fontsize=10,fontweight="bold")
fig.savefig(f"{OUT}/Fig2_method_effect_conditional.png"); plt.close(fig)

# ---- FIG 3 (corrigida): espaçamento entre heatmaps ----
M13=np.array([[[c for c in D if c["rb"]==r and c["cidade"]==k][0]["dH13"] for r in RBS] for k in CITIES])
M25=np.array([[[c for c in D if c["rb"]==r and c["cidade"]==k][0]["dH25"] for r in RBS] for k in CITIES])
vm=max(abs(M13).max(),abs(M25).max())
fig,axes=plt.subplots(1,2,figsize=(8.2,3.1),gridspec_kw={"wspace":0.42})
for ax,M,t in zip(axes,[M13,M25],["REG-2013 base","DGEG2025-A base"]):
    im=ax.imshow(M,cmap="RdBu_r",vmin=-vm,vmax=vm,aspect="auto")
    ax.set_xticks(range(8)); ax.set_xticklabels(RBS,fontsize=7.5)
    ax.set_yticks(range(4)); ax.set_yticklabels(CITIES,fontsize=8)
    ax.set_title(t,fontsize=9)
    for i in range(4):
        for j in range(8):
            v=M[i,j]
            ax.text(j,i,f"{v:+.0f}",ha="center",va="center",fontsize=6.6,
                    color="white" if abs(v)>0.55*vm else "#111")
    ax.set_xticks(np.arange(-.5,8,1),minor=True); ax.set_yticks(np.arange(-.5,4,1),minor=True)
    ax.grid(which="minor",color="white",lw=1.1); ax.tick_params(which="minor",size=0)
cb=fig.colorbar(im,ax=axes,fraction=0.028,pad=0.02)
cb.set_label("$\\Delta_H$  [%]",fontsize=8.5); cb.ax.tick_params(labelsize=7.5)
fig.suptitle("Heating divergence across the 32 building×city combinations",y=1.04,fontsize=10,fontweight="bold")
fig.savefig(f"{OUT}/Fig3_heatmap_dH.png"); plt.close(fig)

# ---- FIG 10 (nova): mapa de operação do fator de utilização ----
G=_decomp()["celulas"]
def eta(g,a):
    g=np.asarray(g,dtype=float)
    out=np.where(np.abs(g-1)<1e-9,a/(a+1),(1-g**a)/(1-g**(a+1)))
    return out
gg=np.linspace(0.05,2.6,400)
fig,ax=plt.subplots(figsize=(6.4,4.2))
for a,col,lab,ls in ((4.2,C13,"$\\alpha$ = 4.2 (tabulated, heavy)","-"),
                     (2.6,C13,"$\\alpha$ = 2.6 (tabulated, medium)","--"),
                     (2.06,C25,"$\\alpha$ = 2.06 (median from $\\tau$)","-")):
    ax.plot(gg,eta(gg,a),color=col,ls=ls,lw=1.4,label=lab)
ev=[c for c in G if c["cidade"]=="Évora"]
ot=[c for c in G if c["cidade"]!="Évora"]
ax.scatter([c["gamma_H_sazonal"] for c in ot],[c["eta_H_sazonal"] for c in ot],
           s=26,marker="o",facecolor=C13,alpha=0.75,lw=0,zorder=5,label="seasonal operating points")
ax.scatter([c["gamma_H_sazonal"] for c in ev],[c["eta_H_sazonal"] for c in ev],
           s=42,marker="s",facecolor="none",edgecolor=ACC,lw=1.3,zorder=6,label="seasonal, Évora")
ax.scatter([c["gamma_H_mensal_med"] for c in ot],[c["eta_H_mensal_med"] for c in ot],
           s=26,marker="o",facecolor=C25,alpha=0.75,lw=0,zorder=5,label="monthly operating points (median month)")
ax.scatter([c["gamma_H_mensal_med"] for c in ev],[c["eta_H_mensal_med"] for c in ev],
           s=42,marker="s",facecolor="none",edgecolor=C25,lw=1.3,zorder=6,label="monthly, Évora")
ax.set_xlabel("Heat-balance ratio  $\\gamma_H$  [–]")
ax.set_ylabel("Gain-utilisation factor  $\\eta_H$  [–]")
ax.set_title("Operating map of the gain-utilisation factor")
ax.set_xlim(0,2.6); ax.set_ylim(0.28,1.02)
ax.legend(loc="lower left",fontsize=6.8)
ax.annotate("seasonal: low $\\gamma$, high tabulated $\\alpha$\n→ near-total utilisation",
            xy=(0.52,0.955),fontsize=7.2,color=C13,ha="left")
ax.annotate("monthly: higher $\\gamma$, physical $\\alpha$\n→ lower utilisation",
            xy=(1.35,0.62),fontsize=7.2,color=C25,ha="left")
for s in("top","right"): ax.spines[s].set_visible(False)
fig.savefig(f"{OUT}/Fig10_utilisation_map.png"); plt.close(fig)
print("OK figs 1,2,3,10")
