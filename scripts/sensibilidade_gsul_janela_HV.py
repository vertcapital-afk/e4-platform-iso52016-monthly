# -*- coding: utf-8 -*-
"""sensibilidade_gsul_janela_HV.py — janela do G_sul de referência (Artigo 13, R1).

So celula_13790, DGEG2025-A, quatro janelas (Out-Abr de producao, Nov-Mar,
Out-Mar, Nov-Abr), em hora solar verificada; corre numa copia externa do motor.
Nao corre git, eixo mensal, produtores de grelhas ou geradores.

Precisa do motor do autor (pacote privado, disponivel a pedido):
    py scripts\\sensibilidade_gsul_janela_HV.py --motor C:\\motor --saida C:\\pasta_nova
--saida (fora do motor e do deposito) recebe a copia de trabalho (trabalho/), o registo
PROGRESSO_gsul.md e o resultado sensibilidade_gsul_janela_HV.json. O motor fica
protegido contra escrita por um audit hook. Controlos: regressao 32/32 a 1e-9
contra resultados/fontes_HV/RESULTADO_A13_COMPLETO.json, controlo negativo com o
leitor de cabecalho, perturbacao efectiva do G_sul nas quatro cidades.

Deposito R1 (04/11/2026): logica igual a da corrida de 04/11/2026 que produziu
resultados/sensibilidade_gsul_janela_HV.json (script com o SHA-256 registado no
meta desse ficheiro); mudaram so os caminhos, agora dados por --motor e --saida,
a referencia (a do deposito) e a origem do hv_patch.py (a deste deposito).
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import statistics
import sys

sys.dont_write_bytecode=True
sys.stdout.reconfigure(encoding='utf-8')
DEPOSITO=Path(__file__).resolve().parents[1]
REF=DEPOSITO/'resultados'/'fontes_HV'/'RESULTADO_A13_COMPLETO.json'
HV_PATCH=DEPOSITO/'scripts'/'sensibilidades_hv'/'hv_patch.py'
_ap=argparse.ArgumentParser(description='Janela do G_sul, A13 R1 (precisa do motor do autor).')
_ap.add_argument('--motor',default=os.environ.get('E4_MOTOR'),help='raiz do motor do autor')
_ap.add_argument('--saida',help='pasta nova, fora do motor')
_args=_ap.parse_args()
if not _args.motor or not _args.saida:
    print('Indicar --motor (ou E4_MOTOR) e --saida. Codigo 2.');raise SystemExit(2)
ROOT=Path(_args.motor).resolve()
OUT=Path(_args.saida).resolve()
if not (ROOT/'src'/'e4'/'__init__.py').is_file():
    print(f'Motor incompleto: falta {ROOT/"src"/"e4"}. Codigo 2.');raise SystemExit(2)
for _proibida in (ROOT,DEPOSITO):
    if OUT==_proibida or OUT.is_relative_to(_proibida):
        print(f'--saida {OUT} esta dentro de {_proibida} (motor ou deposito). Codigo 2.');raise SystemExit(2)
OUT.mkdir(parents=True,exist_ok=True)
WORK=OUT/'trabalho'
PROGRESS=OUT/'PROGRESSO_gsul.md'
WINDOWS={'Out–Abr':(10,11,12,1,2,3,4),'Nov–Mar':(11,12,1,2,3),
         'Out–Mar':(10,11,12,1,2,3),'Nov–Abr':(11,12,1,2,3,4)}

def log(text):
    with PROGRESS.open('a',encoding='utf-8') as f:
        f.write(text+'\n\n');f.flush()
    print(text,flush=True)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def protect(event,args):
    def inside(p):return isinstance(p,(str,bytes,os.PathLike)) and Path(os.fsdecode(p)).resolve().is_relative_to(ROOT)
    if event=='open':
        p,mode,flags=args
        write=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
        if write and inside(p):raise PermissionError('Arvore do decisor protegida')
    elif event in ('os.mkdir','os.remove','os.rmdir','os.rename','os.link','os.symlink') and any(inside(p) for p in args[:2]):
        raise PermissionError('Arvore do decisor protegida')

def main():
    PROGRESS.write_text('# Aberto L — progresso, 04/11/2026\n\n','utf-8')
    assert not WORK.resolve().is_relative_to(ROOT)
    sys.addaudithook(protect)
    log('⚙ Passo1 iniciado: copia externa; nenhum comando Git ou escrita na arvore.')
    ignore=shutil.ignore_patterns('__pycache__','*.pyc','.pytest_cache')
    shutil.copytree(ROOT/'src',WORK/'src',dirs_exist_ok=True,ignore=ignore)
    log('⚙ Passo1a fechado: src copiado.')
    study=Path('studies/a13_iso52016_mensal')
    shutil.copytree(ROOT/study,WORK/study,dirs_exist_ok=True,ignore=ignore)
    shutil.copyfile(REF,WORK/'RESULTADO_A13_COMPLETO.json')
    shutil.copyfile(HV_PATCH,WORK/'hv_patch.py')
    inputs={str(REF):sha(REF),str(ROOT/study/'run_grelha_artigo13.py'):sha(ROOT/study/'run_grelha_artigo13.py'),
            str(ROOT/study/'revisao_a13_producao.py'):sha(ROOT/study/'revisao_a13_producao.py'),
            str(HV_PATCH):sha(HV_PATCH)}
    log('⚙ Passo1 fechado: estudo, referencia e hv_patch copiados; imports seguintes usam a copia.')
    sys.path.insert(0,str(WORK))
    import hv_patch as h
    g,r=h.g,h.r
    assert Path(g.__file__).resolve().is_relative_to(WORK)
    reference=json.loads((WORK/'RESULTADO_A13_COMPLETO.json').read_text('utf-8'))
    refs={(c['rb'],c['cidade']):c['necessidades']['verificada']['nic_13790'] for c in reference['celulas']}
    assert len(refs)==len(reference['celulas'])==32
    for city in g.CIDADES:
        p=ROOT/'src/e4/fixtures/clima'/(g._EPW[city]+'.epw');inputs[str(p)]=sha(p)
    original_window=g._MESES_FORA_JJAS
    state=r._aplicar(r.REVISAO)
    calls=0
    def evaluate(label,reader):
        nonlocal calls
        window=WINDOWS[label];g._MESES_FORA_JJAS=window
        records=[];solar={}
        for city in g.CIDADES:
            irr=reader(city)[0]
            gsul=sum(irr[m]['SV'] for m in window)/len(window)
            solar[city]=gsul
            climate=g._clima_dgeg2025_a(city,irr)
            for rb in g.RB_ORDEM:
                nic,_=g.celula_13790(rb,city,climate);calls+=1
                records.append(dict(rb=rb,cidade=city,janela=label,gsul=gsul,nic=nic))
        return records,solar
    try:
        baseline,solar0=evaluate('Out–Abr',h._hv)
        errors=[dict(rb=c['rb'],cidade=c['cidade'],nic=c['nic'],referencia=refs[c['rb'],c['cidade']],erro_abs=abs(c['nic']-refs[c['rb'],c['cidade']])) for c in baseline]
        bad=[c for c in errors if c['erro_abs']>1e-9]
        log(f"⚙ Passo2: regressao HV {32-len(bad)}/32 a1e-9; erro maximo {max(c['erro_abs'] for c in errors):.17g} kWh/m2.a.")
        if bad:
            log('⚙ PARAGEM: regressao falhou: '+json.dumps(bad,ensure_ascii=False));return 1
        cn,_=evaluate('Out–Abr',h._orig)
        cn_bad=[dict(rb=c['rb'],cidade=c['cidade'],nic_cabecalho=c['nic'],nic_HV=refs[c['rb'],c['cidade']],erro_abs=abs(c['nic']-refs[c['rb'],c['cidade']])) for c in cn if abs(c['nic']-refs[c['rb'],c['cidade']])>1e-9]
        log(f'⚙ Passo3: CN cabecalho: {len(cn_bad)}/32 divergencias de Nic face a HV; razao: valores sazonais diferentes, sem erro de importacao/execucao.')
        if not cn_bad:
            log('⚙ PARAGEM: controlo negativo nao discriminou.');return 1
        nov,solar_nov=evaluate('Nov–Mar',h._hv)
        changed={city:dict(producao=solar0[city],nov_mar=solar_nov[city],delta=solar_nov[city]-solar0[city]) for city in g.CIDADES}
        assert all(abs(v['delta'])>1e-10 for v in changed.values())
        log('⚙ Passo4: perturbacao efectiva nas quatro cidades: '+json.dumps(changed,ensure_ascii=False))
        log('⚙ Controlos fechados; iniciada a reuniao dos resultados por janela.')
        sets={'Out–Abr':(baseline,solar0),'Nov–Mar':(nov,solar_nov)}
        for label in ('Out–Mar','Nov–Abr'):
            sets[label]=evaluate(label,h._hv);log('⚙ Janela fechada: '+label)
        production={(c['rb'],c['cidade']):c['nic'] for c in baseline}
        cells=[];summary={};solar_city={city:{} for city in g.CIDADES}
        for label in WINDOWS:
            records,solar=sets[label]
            for c in records:
                c['delta_pct']=100*(c['nic']/production[c['rb'],c['cidade']]-1)
                cells.append(c)
            values=[c['delta_pct'] for c in records]
            summary[label]=dict(mediana=statistics.median(values),minimo=min(values),maximo=max(values),
                                sinais=dict(negativos=sum(v<0 for v in values),zeros=sum(v==0 for v in values),positivos=sum(v>0 for v in values)))
            for city in g.CIDADES:solar_city[city][label]=solar[city]
        target=summary['Nov–Mar'];observed=[round(target[k],2) for k in ('mediana','minimo','maximo')]
        same=observed==[0.0,-3.23,4.42]
        comparison=dict(LEIA_ME=[0.0,-3.23,4.42],observado_a_duas_casas=observed,coincide=same)
    finally:
        g._MESES_FORA_JJAS=original_window;r._repor(state)
        restored=dict(a52=g.A_SOL_PAREDE,d52=g.R_DESVAO_COB,hce=g.H_CE,a13=r.solar.ALFA_PAREDE,d13=r.geometria.R_DESVAO_COB)
        assert restored==state and g._MESES_FORA_JJAS==original_window
        log('⚙ Configuracao e janela repostas na copia, em finally.')
    for p,digest in inputs.items():assert sha(p)==digest,p
    doc=dict(meta=dict(base='DGEG2025-A',hora='verificada',eixo='sazonal celula_13790 apenas',configuracao=r.REVISAO,
                       janelas={k:list(v) for k,v in WINDOWS.items()},celulas_por_janela=32,observacoes=128,chamadas_sazonais_incluindo_CN=calls,
                       tolerancia_regressao=1e-9,fontes_sha256=inputs,script_sha256=sha(Path(__file__)),reposicao_confirmada=True),
             controlos=dict(regressao=errors,CN_cabecalho=cn_bad,perturbacao_gsul=changed),
             celulas=cells,resumo_por_janela=summary,gsul_por_cidade_e_janela=solar_city,comparacao_LEIA_ME=comparison)
    output=OUT/'sensibilidade_gsul_janela_HV.json'
    output.write_text(json.dumps(doc,ensure_ascii=False,indent=2,allow_nan=False)+'\n','utf-8')
    log('⚙ Passo5 fechado: 128 observacoes (32celulas x4janelas); JSON por celula e resumos gravados.')
    log('⚙ Comparacao com LEIA-ME: '+json.dumps(comparison,ensure_ascii=False))
    if not same:log('⚙ DIVERGENCIA reportada; nenhuma explicacao ou interpretacao proposta.')
    log('⚙ Concluido: tres ficheiros principais entregues; copia auxiliar em trabalho/. Sem Git, sem eixo mensal, sem escrita na arvore.')
    return 0

if __name__=='__main__':raise SystemExit(main())
