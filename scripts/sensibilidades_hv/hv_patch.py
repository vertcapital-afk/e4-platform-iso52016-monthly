# -*- coding: utf-8 -*-
"""
hv_patch.py — leitura do EPW em hora solar verificada para o motor do autor
(Artigo 13, revisão R1; sensibilidades de 03/11/2026).

Substitui só run_grelha_artigo13._ler_epw_cidade pela leitura
ler_epw_com_hora(..., "verificada"), com a mesma cadeia de irradiância, horas e
temperaturas. Correndo-o directamente, confere a regressão das 32 células
DGEG2025-A contra RESULTADO_A13_COMPLETO.json (1e-9) e o controlo negativo com o
leitor de cabeçalho, que não pode reproduzir.

⚠️ NÃO corre a partir desta pasta do depósito. Precisa de uma CÓPIA de trabalho
do motor do autor (pacote privado, disponível a pedido), com esta disposição:

    PASTA/src/e4/...                          (motor)
    PASTA/studies/a13_iso52016_mensal/...     (estudo)
    PASTA/hv_patch.py e PASTA/run_hv.py       (copiados desta pasta)
    PASTA/RESULTADO_A13_COMPLETO.json         (de resultados/fontes_HV/)

Uma CÓPIA, nunca o repositório do motor: os produtores das sensibilidades gravam
os resultados ao lado de si. O módulo recusa uma pasta com .git (pasta ou ficheiro).
Ver LEIA-ME.md. Lógica igual à usada em 03/11/2026; no depósito acrescentaram-se
este cabeçalho, a recusa acima e a leitura explícita em UTF-8.
"""
import sys, os, json
W=os.path.dirname(os.path.abspath(__file__))
if not os.path.isfile(os.path.join(W,"src","e4","__init__.py")) or not os.path.isfile(os.path.join(W,"studies","a13_iso52016_mensal","run_grelha_artigo13.py")):
    print(f"hv_patch.py: {W} não é uma cópia de trabalho do motor (falta src/e4 ou studies/a13_iso52016_mensal). Ver LEIA-ME.md.")
    raise SystemExit(2)
if os.path.exists(os.path.join(W,".git")):   # pasta ou ficheiro (worktree)
    print(f"hv_patch.py: {W} tem .git: parece o repositório do motor. Corra numa CÓPIA (os produtores gravam ao lado de si).")
    raise SystemExit(2)
sys.dont_write_bytecode=True
sys.path[:0]=[os.path.join(W,"src"), os.path.join(W,"studies","a13_iso52016_mensal")]
import run_grelha_artigo13 as g
import revisao_a13_producao as r
from e4.clima_horario_a14 import ler_epw_com_hora
_CACHE={}
_orig=g._ler_epw_cidade
def _hv(cidade):
    if cidade not in _CACHE:
        epw=os.path.join(W,"src","e4","fixtures","clima",g._EPW[cidade]+".epw")
        regs,loc=ler_epw_com_hora(epw,"verificada")
        _CACHE[cidade]=(g.irradiancia_mensal_por_orientacao(regs,loc),g.horas_por_mes(regs),g.theta_ext_media_mensal(regs),g.theta_ext_anual_media(regs))
    return _CACHE[cidade]
g._ler_epw_cidade=_hv
def regressao():
    ref={(c["rb"],c["cidade"]):c["necessidades"]["verificada"] for c in json.load(open(os.path.join(W,"RESULTADO_A13_COMPLETO.json"),encoding="utf-8"))["celulas"]}
    falhas=0
    for (rb,cid),v in ref.items():
        antes=r._aplicar(r.REVISAO)
        try:
            s=g._ler_epw_cidade(cid)
            nic,nvc=g.celula_13790(rb,cid,g._clima_dgeg2025_a(cid,s[0]))
            nh,nc,nh20=g.celula_52016(rb,s)
        finally: r._repor(antes)
        got=dict(nic_13790=nic,nvc_13790=nvc,nh_52016=nh,nc_52016=nc,nh20_52016_cenario=nh20)
        d=max(abs(got[k]-v[k]) for k in got)
        if d>1e-9: falhas+=1; print("FALHA",rb,cid,d)
    print(f"regressao HV: {len(ref)-falhas}/{len(ref)} celulas a 1e-9")
    return falhas==0
if __name__=="__main__":
    ok=regressao()
    # controlo negativo: leitor original (cabecalho) NAO deve reproduzir HV
    g._ler_epw_cidade=_orig; _CACHE.clear()
    print("CN (cabecalho deve falhar):", "detectado" if not regressao() else "NAO DETECTADO")
