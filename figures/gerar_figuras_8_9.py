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

import json, os
import numpy as np, matplotlib
np.random.seed(3)   # [31/07/2026] Fig.9 usava jitter sem semente
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8.5,"axes.linewidth":0.7,
 "axes.edgecolor":"#333","axes.labelsize":9,"axes.titlesize":9.5,"axes.titleweight":"bold",
 "xtick.labelsize":8,"ytick.labelsize":8,"legend.fontsize":8,"legend.frameon":False,
 "figure.dpi":300,"savefig.dpi":300,"savefig.bbox":"tight"})
C25="#1D4E89"; ACC="#9D174D"; GREY="#6B7280"; C13="#B45309"
d=_decomp()["celulas"]
CITIES=["Coimbra","Bragança","Évora","Lisboa"]; mk={"Coimbra":"o","Bragança":"^","Évora":"s","Lisboa":"D"}

# FIG 8 — dC vs gamma_C  (criterio estrutural)
fig,ax=plt.subplots(figsize=(6.6,4.2))
ax.axhline(0,color=GREY,lw=0.7); ax.axvline(1.0,color=ACC,lw=1.2,ls="--",zorder=2)
ax.axvspan(0.30,1.0,color=ACC,alpha=0.055,zorder=0)
for c in d:
    ax.scatter(c["gamma_C_sazonal"],c["dC"],s=34,marker=mk[c["cidade"]],
               facecolor=C25 if c["rb"] in("RB1","RB2","RB3","RB4") else "none",
               edgecolor=C25,lw=1.0,alpha=0.9,zorder=4)
ex=next(c for c in d if c["rb"]=="RB2" and c["cidade"]=="Bragança")
ax.annotate("RB2 / Bragança",xy=(ex["gamma_C_sazonal"],ex["dC"]),xytext=(0.72, max(c["dC"] for c in d)*0.98),
            fontsize=7.5,arrowprops=dict(arrowstyle="-",lw=0.7,color=GREY))
ax.set_xscale("log"); ax.set_xticks([0.4,0.6,0.8,1.0,1.5,2,3])
ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.set_xlabel("Seasonal heat-balance ratio  $\\gamma_C$  [–, log scale]")
ax.set_ylabel("Cooling divergence  $\\Delta_C$  [%]")
ax.set_title("The sign of the cooling divergence is set by $\\gamma_C$")
# [01/08/2026] Segmentacao CALCULADA dos dados -- era texto fixo, e sob
# [P-alfa-A13-paridade] os numeros mudaram de lado (14/14 e 16/18).
import statistics as _st
_lt = [c for c in d if c["gamma_C_sazonal"] < 1.0]
_ge = [c for c in d if c["gamma_C_sazonal"] >= 1.0]
_pos = sum(1 for c in _lt if c["dC"] > 0); _neg = sum(1 for c in _ge if c["dC"] < 0)
_ytxt = max(c["dC"] for c in d) * 0.78
ax.text(0.62,_ytxt,"$\\gamma_C<1$: gains below losses\n%d/%d positive\nmedian %+.0f %%"
        % (_pos,len(_lt),_st.median([c["dC"] for c in _lt])),
        fontsize=7.5,color=ACC,ha="center",style="italic")
ax.text(2.1,_ytxt,"$\\gamma_C\\geq1$\n%d/%d negative\nmedian %+.0f %%"
        % (_neg,len(_ge),_st.median([c["dC"] for c in _ge])),
        fontsize=7.5,color=GREY,ha="center",style="italic")
h=[plt.Line2D([],[],marker=mk[k],ls="",color=C25,label=k) for k in CITIES]
h+=[plt.Line2D([],[],marker="o",ls="",color=C25,label="SFH (filled)"),
    plt.Line2D([],[],marker="o",ls="",mfc="none",mec=C25,label="MFH (open)")]
ax.legend(handles=h,loc="upper right",fontsize=6.8,ncol=2)
for s in("top","right"): ax.spines[s].set_visible(False)
fig.savefig(f"{OUT}/Fig8_gammaC_separator.png"); plt.close(fig)

# FIG 9 — anatomia: quatro componentes estruturais
fig,axes=plt.subplots(1,4,figsize=(7.6,3.0))
def pair(ax,a,b,la,lb,title,ylab,fmt="{:.2f}"):
    m=[np.median(a),np.median(b)]
    bars=ax.bar([0,1],m,color=[C13,C25],width=0.6,alpha=0.85)
    for i,(x,v) in enumerate(zip([0,1],m)):
        ax.text(x,v*1.02,fmt.format(v),ha="center",va="bottom",fontsize=8,fontweight="bold")
    for i,arr in enumerate([a,b]):
        ax.scatter(np.random.normal(i,0.06,len(arr)),arr,s=7,color="#333",alpha=0.45,zorder=3,lw=0)
    ax.set_xticks([0,1]); ax.set_xticklabels([la,lb],fontsize=7.5)
    ax.set_title(title,fontsize=8.8); ax.set_ylabel(ylab,fontsize=8)
    for s in("top","right"): ax.spines[s].set_visible(False)
pair(axes[0],[c["meses_H_sazonal"] for c in d],[c["meses_H_inferidos"] for c in d],
     "seasonal\n(input)","monthly\n(inferred)","Heating season","months","{:.1f}")
pair(axes[1],[c["alpha_sazonal"] for c in d],[c["alpha_mensal"] for c in d],
     "seasonal\n(tabulated)","monthly\n(from $\\tau$)","Inertia $\\alpha$","–")
pair(axes[2],[c["eta_H_sazonal"] for c in d],[c["eta_H_mensal_med"] for c in d],
     "seasonal","monthly","Gain utilisation $\\eta_H$","–")
axes[3].bar([0],[np.median([c["Q_sky_share"] for c in d])*100],color=C25,width=0.5,alpha=0.85)
axes[3].scatter(np.random.normal(0,0.05,len(d)),[c["Q_sky_share"]*100 for c in d],s=7,color="#333",alpha=0.45,zorder=3,lw=0)
_sky = np.median([c["Q_sky_share"] for c in d])*100
axes[3].text(0,_sky*1.02,"%.1f%%"%_sky,ha="center",va="bottom",fontsize=8,fontweight="bold")
axes[3].set_xticks([0]); axes[3].set_xticklabels(["monthly\nonly"],fontsize=7.5)
axes[3].set_title("Sky radiation $Q_{sky}$",fontsize=8.8); axes[3].set_ylabel("% of gross solar gains",fontsize=8)
axes[3].set_xlim(-0.5,0.5)
for s in("top","right"): axes[3].spines[s].set_visible(False)
fig.suptitle("Anatomy of the method difference: four structural components",y=1.04,fontsize=10,fontweight="bold")
fig.tight_layout()
fig.savefig(f"{OUT}/Fig9_anatomy.png"); plt.close(fig)
print("OK")
