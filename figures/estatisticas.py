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

import json, statistics as st
D = _carregar()
R = [[c["nic13"], c["nh13"], c["nvc13"], c["nc13"]] for c in D]
for i,c in enumerate(D):
    c['nic13'],c['nh13'],c['nvc13'],c['nc13']=R[i]
    c['dH25']=(c['nh_52016']/c['nic_13790']-1)*100
    c['dC25']=(c['nc_52016']/c['nvc_13790']-1)*100
    c['dH13']=(c['nh13']/c['nic13']-1)*100
    c['dC13']=(c['nc13']/c['nvc13']-1)*100
    c['sfh']=c['rb'] in ('RB1','RB2','RB3','RB4')
def s(v): return "med %.1f [%.1f, %.1f] IQR %.1f-%.1f"%(st.median(v),min(v),max(v),st.quantiles(v,n=4)[0],st.quantiles(v,n=4)[2])
print("== GLOBAL (n=32) ==")
for k in ('dH25','dH13','dC25','dC13'):
    print(" ",k, s([c[k] for c in D]), "| neg:",sum(1 for c in D if c[k]<0))
print("\n== POR CIDADE: mediana dH25 / dH13 / dC25 / dC13 ==")
for city in ('Coimbra','Bragança','Évora','Lisboa'):
    g=[c for c in D if c['cidade']==city]
    print("  %-9s %6.1f %6.1f %7.1f %7.1f  (dH13 neg %d/8)"%(city,st.median([c['dH25'] for c in g]),st.median([c['dH13'] for c in g]),st.median([c['dC25'] for c in g]),st.median([c['dC13'] for c in g]),sum(1 for c in g if c['dH13']<0)))
print("\n== SFH (RB1-4) vs MFH (RB5-8): mediana dH25 / dH13 ==")
for lab,f in (('SFH',True),('MFH',False)):
    g=[c for c in D if c['sfh']==f]
    print("  %s %.1f  %.1f"%(lab,st.median([c['dH25'] for c in g]),st.median([c['dH13'] for c in g])))
print("\n== EFEITO DA BASE (2013 -> DGEG2025-A), mesmo metodo, mesma altitude ==")
seasH=[(c['nic_13790']/c['nic13']-1)*100 for c in D]
mensH=[(c['nh_52016']/c['nh13']-1)*100 for c in D]
seasC=[(c['nvc_13790']/c['nvc13']-1)*100 for c in D]
mensC=[(c['nc_52016']/c['nc13']-1)*100 for c in D]
print("  aquecimento sazonal:",s(seasH)); print("  aquecimento mensal :",s(mensH))
print("  arrefec.  sazonal  :",s(seasC)); print("  arrefec.  mensal   :",s(mensC))
print("\n== Q2: celulas com Nvc(sazonal) < 4 kWh/m2.a ==")
q=[c for c in D if c['nvc_13790']<4.0]
print("  n=%d ; mediana dC25 %.0f%% ; max %.0f%% (%s/%s)"%(len(q),st.median([c['dC25'] for c in q]),max(c['dC25'] for c in q),*[ (c['rb'],c['cidade']) for c in q if c['dC25']==max(x['dC25'] for x in q)][0]))
q13=[c for c in D if c['nvc13']<4.0]
print("  base 2013: n=%d ; mediana dC13 %.0f%% ; max %.0f%%"%(len(q13),st.median([c['dC13'] for c in q13]),max(c['dC13'] for c in q13)))
r=[c for c in D if c['nvc_13790']>=4.0]
print("  Nvc>=4 (DGEG): n=%d ; mediana dC25 %.0f%%"%(len(r),st.median([c['dC25'] for c in r])))
print("\n== CENARIO 20C vs N_H@18 ==")
sc=[(c['nh20_52016_cenario']/c['nh_52016']-1)*100 for c in D]
print(" ",s(sc))
for city in ('Coimbra','Bragança','Évora','Lisboa'):
    g=[c for c in D if c['cidade']==city]
    print("  %-9s med %.0f%%"%(city,st.median([(c['nh20_52016_cenario']/c['nh_52016']-1)*100 for c in g])))
print("\n== RB6/Coimbra: os quatro cantos, z=255 m ==")
c=[x for x in D if x['rb']=='RB6' and x['cidade']=='Coimbra'][0]
print("  2013 : Nic %.2f  N_H %.2f  dH %+.1f%%"%(c['nic13'],c['nh13'],c['dH13']))
print("  DGEG : Nic %.2f  N_H %.2f  dH %+.1f%%"%(c['nic_13790'],c['nh_52016'],c['dH25']))
print("  naive N_H(DGEG)/Nic(2013) = %+.1f%%"%((c['nh_52016']/c['nic13']-1)*100))
print("\n== correlacao de sinal: dH25 vs dH13 ==")
print("  celulas com dH negativo nas duas bases:",sum(1 for x in D if x['dH25']<0 and x['dH13']<0))
print("  so na base 2013:",sum(1 for x in D if x['dH25']>=0 and x['dH13']<0))

print("\n== AGREGADO PONDERADO PELO STOCK (convencao Artigo 11) ==")
W={'RB1':10.00,'RB2':24.64,'RB3':12.44,'RB4':3.52,'RB5':4.54,'RB6':20.76,'RB7':19.18,'RB8':4.91}
tw=sum(W.values())
def wmean(key):
    # media ponderada por peso de stock, cidades equiponderadas dentro de cada RB
    tot=0
    for rb,w in W.items():
        g=[c for c in D if c['rb']==rb]
        tot += w*sum(c[key] for c in g)/len(g)
    return tot/tw
def wagg(ns,ds):
    # efeito de metodo sobre agregados ponderados de necessidades (nao media de racios)
    num=den=0
    for rb,w in W.items():
        g=[c for c in D if c['rb']==rb]
        num += w*sum(c[ns] for c in g)/len(g)
        den += w*sum(c[ds] for c in g)/len(g)
    return (num/den-1)*100, den/tw, num/tw
for lab,(ns,ds) in {'DGEG2025-A':('nh_52016','nic_13790'),'REG-2013':('nh13','nic13')}.items():
    d,seas,mens=wagg(ns,ds)
    print("  %-11s aquecimento: sazonal %6.1f  mensal %6.1f  -> %+.1f%%"%(lab,seas,mens,d))
for lab,(ns,ds) in {'DGEG2025-A':('nc_52016','nvc_13790'),'REG-2013':('nc13','nvc13')}.items():
    d,seas,mens=wagg(ns,ds)
    print("  %-11s arrefecim. : sazonal %6.2f  mensal %6.2f  -> %+.1f%%"%(lab,seas,mens,d))
print("  media ponderada dos racios dH25 %.1f%% | dH13 %.1f%%"%(wmean('dH25'),wmean('dH13')))
print("  simples (nao ponderada) dH25 %.1f%% | dH13 %.1f%%"%(sum(c['dH25'] for c in D)/32,sum(c['dH13'] for c in D)/32))
