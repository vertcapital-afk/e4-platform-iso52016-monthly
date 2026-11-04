# -*- coding: utf-8 -*-
"""
revisao_a13_producao.py — grelha de produção do Artigo 13, revisão R1
(Energy & Buildings, ENB-D-26-06604; manuscrito em revisão, não aceite nem
publicado).

⚠️ Precisa do motor do autor (pacote privado, disponível a pedido). Num clone
limpo deste depósito não corre: sai com o código 2. Os números depositados
verificam-se sem motor com scripts/verificar_revisao_a13.py.

[P-alfa-A13-paridade] — decisão do autor, 31/07/2026:

    · α_parede   0,04 -> 0,40   NOS DOIS RAMOS (52016 e 13790)
    · desvão     0,14 -> 0,0    NOS DOIS RAMOS
    · h_ce      20,86 -> 20,0   só no ramo 52016 (o 13790 não usa o conceito;
                                usa R_se = 0,04, convenção própria de cada
                                método, declarada nos Métodos)
    · α_cobertura = 0,50        já estava em paridade; não se toca

⛔ PORQUÊ «NOS DOIS RAMOS»: a absortância e o desvão vivem em sítios diferentes
para cada ramo (52016 em run_grelha_artigo13.py; 13790 em e4/solar.py e
e4/geometria.py). Corrigir só um lado quebra a PARIDADE DE ENVOLVENTE e fabrica
um efeito de método falso. A sobreposição é em runtime, com try/finally: os
módulos partilhados do motor ficam com os valores por omissão.

R1 (04/11/2026), diferenças face à versão publicada com a submissão:
    · a leitura do EPW é EXPLÍCITA: ler_epw_com_hora(..., "verificada") no lugar
      de run_grelha_artigo13._ler_epw_cidade, com a mesma cadeia de irradiância,
      horas e temperaturas; --hora cabecalho reproduz a coluna histórica;
    · a regressão é contra resultados/fontes_HV/RESULTADO_A13_COMPLETO.json
      (a grelha da versão JBE, que a versão anterior usava, não está neste
      depósito); se falhar, nada se grava;
    · escreve só em --saida, uma pasta fora do motor e fora do depósito;
    · os caminhos são relativos ao depósito e ao motor indicado.

Uso (Windows: «py»):
    py scripts\\revisao_a13_producao.py --motor C:\\motor --saida C:\\pasta_nova
        64 células (32 por base); regressão a 3 casas, 320 valores; grava as
        duas grelhas em --saida.
    py scripts\\revisao_a13_producao.py --motor C:\\motor --celula RB6 Coimbra
        uma célula; regressão a 1e-9 contra a fonte; não grava nada.

Código de saída: 0 regressão reproduzida; 1 regressão falhou (nada se grava);
2 motor, argumentos ou pasta de saída inválidos.
"""
import argparse
import json
import os
import statistics as st
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.dont_write_bytecode = True     # não escrever __pycache__ no motor

AQUI = os.path.dirname(os.path.abspath(__file__))
DEPOSITO = os.path.dirname(AQUI)
FONTE_HV = os.path.join(DEPOSITO, "resultados", "fontes_HV", "RESULTADO_A13_COMPLETO.json")

REVISAO = dict(alfa_parede=0.40, desvao_cob=0.0, h_ce=20.0)
CAMPOS = ("nic_13790", "nvc_13790", "nh_52016", "nc_52016", "nh20_52016_cenario")
CAMPOS_2013 = ("nic_13790_2013", "nvc_13790_2013", "nh_52016_2013", "nc_52016_2013",
               "nh20_52016_2013_cenario")
TOL = 1e-9


# ------------------------------------------------------------------ motor
def carregar_motor(raiz):
    """Importa o motor a partir de `raiz` (src/e4 + studies/a13_iso52016_mensal)."""
    if not raiz:
        print("⛔ Indicar a raiz do motor do autor: --motor CAMINHO ou a variável E4_MOTOR.")
        raise SystemExit(2)
    raiz = os.path.abspath(raiz)
    src = os.path.join(raiz, "src")
    est = os.path.join(raiz, "studies", "a13_iso52016_mensal")
    for p in (os.path.join(src, "e4", "__init__.py"), os.path.join(est, "run_grelha_artigo13.py")):
        if not os.path.exists(p):
            print(f"⛔ Motor incompleto: não encontrado {p}")
            raise SystemExit(2)
    sys.path[:0] = [src, est]
    import run_grelha_artigo13 as g
    from e4 import solar, geometria
    from e4.matriz_nacional import RB_SPECS
    from e4.clima_horario_a14 import ler_epw_com_hora
    if not os.path.normcase(os.path.abspath(g.__file__)).startswith(os.path.normcase(est)):
        print(f"⛔ run_grelha_artigo13 veio de {g.__file__}, não de {est}")
        raise SystemExit(2)
    return dict(g=g, solar=solar, geometria=geometria, ler=ler_epw_com_hora, raiz=raiz,
                peso={s.rb: s.peso for s in RB_SPECS})


def leitor(M, hora):
    """O leitor do EPW com a hora explícita; uma leitura por cidade."""
    g, cache = M["g"], {}

    def _ler_epw_cidade(cidade):
        if cidade not in cache:
            epw = os.path.join(M["raiz"], "src", "e4", "fixtures", "clima", g._EPW[cidade] + ".epw")
            regs, loc = M["ler"](epw, hora)
            cache[cidade] = (g.irradiancia_mensal_por_orientacao(regs, loc), g.horas_por_mes(regs),
                             g.theta_ext_media_mensal(regs), g.theta_ext_anual_media(regs))
        return cache[cidade]
    return _ler_epw_cidade


def _aplicar(M, cfg):
    """Põe a configuração NOS DOIS RAMOS. Devolve o estado anterior."""
    g, solar, geo = M["g"], M["solar"], M["geometria"]
    antes = dict(a52=g.A_SOL_PAREDE, d52=g.R_DESVAO_COB, hce=g.H_CE,
                 a13=solar.ALFA_PAREDE, d13=geo.R_DESVAO_COB, epw=g._ler_epw_cidade)
    g.A_SOL_PAREDE = cfg["alfa_parede"]          # ramo 52016
    g.R_DESVAO_COB = cfg["desvao_cob"]
    g.H_CE = cfg["h_ce"]
    solar.ALFA_PAREDE = cfg["alfa_parede"]       # ramo 13790 (paridade)
    geo.R_DESVAO_COB = cfg["desvao_cob"]
    return antes


def _repor(M, antes):
    g, solar, geo = M["g"], M["solar"], M["geometria"]
    g.A_SOL_PAREDE, g.R_DESVAO_COB, g.H_CE = antes["a52"], antes["d52"], antes["hce"]
    solar.ALFA_PAREDE, geo.R_DESVAO_COB = antes["a13"], antes["d13"]
    g._ler_epw_cidade = antes["epw"]


def corrida(M, cfg, hora, celula=None):
    """(células DGEG2025-A, células REG-2013). Com `celula`, só essa e sem
    arredondar; sem ela, as grelhas completas do produtor (3 casas)."""
    g = M["g"]
    antes = _aplicar(M, cfg)
    g._ler_epw_cidade = leitor(M, hora)
    try:
        if celula:
            rb, cid = celula
            s = g._ler_epw_cidade(cid)
            nic, nvc = g.celula_13790(rb, cid, g._clima_dgeg2025_a(cid, s[0]))
            nh, nc, nh20 = g.celula_52016(rb, s)
            nic13, nvc13 = g.celula_13790_2013(rb, cid)
            nh13, nc13, nh20_13 = g.celula_52016_2013(rb, cid)
            a = [dict(rb=rb, cidade=cid, **dict(zip(CAMPOS, (nic, nvc, nh, nc, nh20))))]
            b = [dict(rb=rb, cidade=cid, **dict(zip(CAMPOS_2013, (nic13, nvc13, nh13, nc13, nh20_13))))]
            return a, b
        return g.correr_grelha()["celulas"], g.correr_grelha_2013()["celulas"]
    finally:
        _repor(M, antes)      # os módulos partilhados NUNCA ficam alterados


def regressao(a, b, hora, completa):
    """Compara com a fonte HV: a 1e-9 numa célula; a 3 casas, exacto, nas grelhas."""
    with open(FONTE_HV, encoding="utf-8") as f:
        F = {(c["rb"], c["cidade"]): c for c in json.load(f)["celulas"]}
    difs, n = [], 0
    for cs, chave, campos in ((a, ("necessidades", hora), CAMPOS),
                              (b, ("controlo_REG2013", None), CAMPOS_2013)):
        for c in cs:
            ref = F[(c["rb"], c["cidade"])][chave[0]]
            ref = ref[chave[1]] if chave[1] else ref
            for k in campos:
                n += 1
                ok = (abs(c[k] - ref[k]) < TOL) if not completa else (c[k] == round(ref[k], 3))
                if not ok:
                    difs.append(f"{c['rb']}/{c['cidade']} {k}: {c[k]} vs fonte {ref[k]}")
    if completa and (len(a), len(b)) != (32, 32):
        difs.append(f"células: {len(a)} + {len(b)}, esperado 32 + 32")
    return n, difs


def quadro(cs, sfx, peso):
    """(ΔH mediana, n.º negativas, ΔC mediana, n.º negativas, ΔH ponderado, ΔC ponderado)"""
    dH = [100 * (c[f"nh_52016{sfx}"] - c[f"nic_13790{sfx}"]) / c[f"nic_13790{sfx}"] for c in cs]
    dC = [100 * (c[f"nc_52016{sfx}"] - c[f"nvc_13790{sfx}"]) / c[f"nvc_13790{sfx}"] for c in cs]
    W = sum(peso[c["rb"]] for c in cs)
    pw = lambda k: sum(c[k] * peso[c["rb"]] for c in cs) / W          # noqa: E731
    ph = 100 * (pw(f"nh_52016{sfx}") - pw(f"nic_13790{sfx}")) / pw(f"nic_13790{sfx}")
    pc = 100 * (pw(f"nc_52016{sfx}") - pw(f"nvc_13790{sfx}")) / pw(f"nvc_13790{sfx}")
    return st.median(dH), sum(1 for x in dH if x < 0), st.median(dC), \
        sum(1 for x in dC if x < 0), ph, pc


def pasta_saida_valida(saida, M):
    """--saida não pode estar dentro do motor nem dentro do depósito."""
    s = os.path.normcase(os.path.abspath(saida))
    for proibida in (M["raiz"], DEPOSITO):
        p = os.path.normcase(os.path.abspath(proibida))
        if s == p or s.startswith(p + os.sep):
            return f"--saida {saida} está dentro de {proibida}"
    return None


def argumentos(argv, descricao):
    ap = argparse.ArgumentParser(description=descricao)
    ap.add_argument("--motor", default=os.environ.get("E4_MOTOR"), help="raiz do motor do autor")
    ap.add_argument("--saida", help="pasta onde gravar (obrigatória sem --celula)")
    ap.add_argument("--celula", nargs=2, metavar=("RB", "CIDADE"), help="só uma célula; não grava")
    ap.add_argument("--hora", choices=("verificada", "cabecalho"), default="verificada",
                    help="base de tempo da leitura do EPW (R1: verificada)")
    a = ap.parse_args(argv)
    if not a.celula and not a.saida:
        print("⛔ Sem --celula, é obrigatório indicar --saida (pasta nova, fora do motor e do depósito).")
        raise SystemExit(2)
    return a


def main(argv=None):
    a = argumentos(argv, "Grelha de produção do A13 R1 (precisa do motor do autor).")
    M = carregar_motor(a.motor)
    if a.saida:
        erro = pasta_saida_valida(a.saida, M)
        if erro:
            print("⛔", erro)
            return 2
    print(f"motor: {M['raiz']} · hora: {a.hora} · configuração: {REVISAO}")
    a52, b13 = corrida(M, REVISAO, a.hora, tuple(a.celula) if a.celula else None)
    n, difs = regressao(a52, b13, a.hora, completa=not a.celula)
    criterio = "1e-9" if a.celula else "3 casas, exacto"
    if difs:
        print(f"⛔ REGRESSÃO: {len(difs)}/{n} valores diferem da fonte HV ({criterio}). Nada gravado.")
        for d in difs[:10]:
            print("   ", d)
        return 1
    print(f"[OK] regressão: {n}/{n} valores iguais à fonte HV ({criterio}), hora {a.hora}")
    if a.celula:
        return 0

    print("\nEFEITO DE MÉTODO (52016 − 13790) — 32 células por base, configuração R1")
    print(f"{'base':14s}{'ΔH med':>9s}{'neg':>5s}{'ΔC med':>10s}{'neg':>5s}{'ΔH pond':>10s}{'ΔC pond':>10s}")
    for base, cs, sfx in (("DGEG2025-A", a52, ""), ("REG-2013", b13, "_2013")):
        mh, nh, mc, nc, ph, pc = quadro(cs, sfx, M["peso"])
        print(f"{base:14s}{mh:+8.2f}%{nh:5d}{mc:+9.2f}%{nc:5d}{ph:+9.2f}%{pc:+9.2f}%")

    os.makedirs(a.saida, exist_ok=True)
    meta = {"decisao": "[P-alfa-A13-paridade] (autor, 31/07/2026)", "correccoes": REVISAO,
            "paridade": "aplicada NOS DOIS RAMOS", "hora": a.hora,
            "origem": "scripts/revisao_a13_producao.py do depósito R1, com o motor do autor",
            "regressao": f"{n}/{n} valores iguais a resultados/fontes_HV ({criterio})"}
    for nome, cs in (("grelha_artigo13_REVISAO.json", a52),
                     ("grelha_artigo13_2013_REVISAO.json", b13)):
        with open(os.path.join(a.saida, nome), "w", encoding="utf-8") as f:
            json.dump({"meta": meta, "celulas": cs}, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print(f"\nGravado em {a.saida}: as duas grelhas (as células coincidem com resultados/; "
          f"o bloco meta é o desta corrida).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
