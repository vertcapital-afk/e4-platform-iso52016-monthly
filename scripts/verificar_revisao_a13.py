# -*- coding: utf-8 -*-
"""
verificar_revisao_a13.py — verificação numérica do depósito da revisão R1 do
Artigo 13 (Energy & Buildings, ENB-D-26-06604; manuscrito em revisão, não
aceite nem publicado).

Substitui, no depósito R1, o verificador de 01/08/2026 (anunciado como 9/9),
que fica arquivado na tag public-before-R1-ENB-D-26-06604. As contagens
históricas não valem para o R1: vale o registo desta execução.

USO (a partir de qualquer pasta; no Windows, «py» em vez de «python»)

    python scripts/verificar_revisao_a13.py
        Verificações de DADOS. Correm num clone limpo deste depósito, só com a
        biblioteca padrão do Python. As verificações FÍSICAS saem SKIP.

    python scripts/verificar_revisao_a13.py --motor CAMINHO
        Acrescenta as verificações FÍSICAS, com o motor do autor (pacote
        privado, disponível a pedido). CAMINHO é a raiz que contém `src/e4/` e
        `studies/a13_iso52016_mensal/`; também pela variável E4_MOTOR. Com o
        motor indicado mas inutilizável, as físicas FALHAM (não saem SKIP).

    python scripts/verificar_revisao_a13.py --a14 FICHEIRO
        Grelha canónica do A14 para o V5 (informativo). Com --motor, procura-se
        em studies/a14_iso52016_horario/resultados/grelha_a14_canonica.json.

    python scripts/verificar_revisao_a13.py --controlo-negativo
        Um controlo negativo por verificação: corre primeiro a linha de base,
        depois perturba os dados EM MEMÓRIA e confirma que cada verificação
        falha, e pela razão esperada. Confirma também o código de saída.

CÓDIGO DE SAÍDA
    0   todas as verificações executadas passaram (SKIP e INFO não contam);
        com --controlo-negativo: todos os controlos detectados pela razão certa
    1   pelo menos uma FALHA, ou um controlo negativo não detectado

ÂNCORAS
    Uma âncora é o número publicado. Passa se o valor recalculado, arredondado
    às casas da âncora, der exactamente a âncora. Cada âncora leva também o
    número tal como está no texto do R1, com a secção.

O QUE CADA VERIFICAÇÃO LÊ
    V0  integridade: grelhas, decomposição e cruzamento derivados das fontes de
        precisão completa (resultados/fontes_HV/); pesos iguais aos de
        figures/estatisticas.py
    V1  média ponderada dos rácios e rácio das necessidades ponderadas (§3.4)
    V2  cruzamento ingénuo RB6/Coimbra, com a hora verificada escolhida
        explicitamente na fonte (§3.1)
    V3  G_sul de referência de Coimbra: janela de produção Out–Abr, valor e
        banda Nov–Mar (§3.3, §4.4, Tabela 2)
    V4  efeito de base REG-2013 → DGEG2025-A, mesmo método (§3.1)
    V5  INFORMATIVO: braço mensal do A13 contra o do A14 em 12 células. Não
        conta e não faz falhar. Este depósito não afirma identidade.
    V6  sensibilidade α = 0,60 (§4.4, Tabela 2)
    V7  sensibilidades da Tabela 2: Eq. (97) (§2.4), sombreamento de Verão,
        H_gr ± 22 % (§4.4) e isolamento do termo de solo (§3.3)
    F1  (motor) paridade de envolvente na configuração R1 e reposição dos
        módulos partilhados depois da sobreposição em runtime
    F2  (motor) RB6/Coimbra recalculada com o leitor de hora verificada
        explícito; o leitor de cabeçalho tem de dar outro resultado
    F3  (motor) G_sul de Coimbra recalculado do EPW, com a janela do produtor

Nada é escrito: o script só lê. Com o motor, os imports não gravam __pycache__.
"""
import argparse
import ast
import copy
import json
import os
import statistics as st
import subprocess
import sys
import tempfile
import unicodedata

if hasattr(sys.stdout, "reconfigure"):
    # Windows: sem isto, redireccionar a saída para ficheiro morre no primeiro
    # carácter fora do cp1252, e o erro pode sair reportado como outra coisa.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.dont_write_bytecode = True

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
RES = os.path.join(RAIZ, "resultados")
FIG = os.path.join(RAIZ, "figures")

# Pesos do parque (Census; Tabela 1 do manuscrito), cidades equiponderadas.
# O V0 confirma que são os mesmos de figures/estatisticas.py.
PESO = {"RB1": 10.00, "RB2": 24.64, "RB3": 12.44, "RB4": 3.52,
        "RB5": 4.54, "RB6": 20.76, "RB7": 19.18, "RB8": 4.91}
CIDADES = ("Coimbra", "Bragança", "Évora", "Lisboa")
UNIVERSO = {(rb, cid) for rb in PESO for cid in CIDADES}
CAMPOS = ("nic_13790", "nvc_13790", "nh_52016", "nc_52016", "nh20_52016_cenario")
CAMPOS_2013 = ("nic_13790_2013", "nvc_13790_2013", "nh_52016_2013", "nc_52016_2013",
               "nh20_52016_2013_cenario")
JANELA_PRODUCAO = {10, 11, 12, 1, 2, 3, 4}          # Out–Abr
JANELAS_GSUL = ("Out–Abr", "Nov–Mar", "Out–Mar", "Nov–Abr")
CONFIG_R1 = dict(alfa_parede=0.40, desvao_cob=0.0, h_ce=20.0)
TOL_REGRESSAO = 1e-9
AMOSTRA_A14 = ("RB1", "RB6", "RB8")                 # as 12 células do V5 histórico

FICHEIROS = {
    "grelha": "grelha_artigo13_REVISAO.json",
    "grelha13": "grelha_artigo13_2013_REVISAO.json",
    "decomp": "decomposicao_artigo13_REVISAO.json",
    "fontes": os.path.join("fontes_HV", "RESULTADO_A13_COMPLETO.json"),
    "intermed": os.path.join("fontes_HV", "INTERMEDIARIOS_A13_COMPLETO.json"),
    "cruz": "cruzamento_ingenuo_rb6_coimbra_REVISAO.json",
    "gsul": "sensibilidade_gsul_janela_HV.json",
    "alfa060": "sensibilidade_alfa060_A13.json",
    "decomp060": "decomposicao_artigo13_alfa060.json",
    "eq97": "sensibilidade_eq97_REVISAO.json",
    "sombra": "sensibilidade_sombreamento_REVISAO.json",
    "hgr": "sensibilidade_hgr22_REVISAO.json",
    "isol": "isolamento_solo_artigo13_REVISAO.json",
}


# --------------------------------------------------------------- resultados
class ErroCobertura(Exception):
    pass


def resultado(vid, nome, ok, motivo, detalhe):
    return dict(vid=vid, nome=nome, estado="PASS" if ok else "FALHA",
                motivo=None if ok else motivo, detalhe=detalhe)


def info(vid, nome, detalhe):
    return dict(vid=vid, nome=nome, estado="INFO", motivo=None, detalhe=detalhe)


def skip(vid, nome, detalhe):
    return dict(vid=vid, nome=nome, estado="SKIP", motivo=None, detalhe=detalhe)


def _casas(s):
    return len(s.split(".")[1]) if "." in s else 0


def ancora(vid, nome, valor, publicado, texto=None):
    """`publicado` e `texto[0]` são strings ('17.54', '17.5'); `texto[1]` é a secção."""
    obtido = f"{valor:.{_casas(publicado)}f}"
    ok = obtido == publicado
    det = f"{valor:.6f} → {obtido} (âncora {publicado})"
    if texto:
        t, local = texto
        ot = f"{valor:.{_casas(t)}f}"
        ok = ok and ot == t
        det += f"; texto {t} ({local}) → {ot}"
    return resultado(vid, nome, ok, "ancora", det)


def por_celula(lista, nome):
    m = {}
    for c in lista:
        k = (c["rb"], c["cidade"])
        if k in m:
            raise ErroCobertura(f"{nome}: célula repetida {k}")
        m[k] = c
    if set(m) != UNIVERSO:
        falta = sorted(UNIVERSO - set(m))[:3]
        sobra = sorted(set(m) - UNIVERSO)[:3]
        raise ErroCobertura(f"{nome}: {len(m)} células; em falta {falta}; a mais {sobra}")
    return m


def protegido(vid, nome_check):
    """Uma excepção dentro de uma verificação é uma FALHA com a sua razão,
    nunca um sucesso silencioso nem uma «dependência em falta»."""
    def deco(fn):
        def corre(*a, **k):
            try:
                return fn(*a, **k)
            except ErroCobertura as e:
                return [resultado(vid, nome_check, False, "cobertura", str(e))]
            except KeyError as e:
                return [resultado(vid, nome_check, False, "estrutura", f"chave em falta: {e!r}")]
            except Exception as e:  # noqa: BLE001
                return [resultado(vid, nome_check, False, "excepcao", repr(e))]
        corre.__name__ = fn.__name__
        return corre
    return deco


# --------------------------------------------------------------- dados
def _pesos_estatisticas():
    """Lê o dicionário W de figures/estatisticas.py sem o executar."""
    p = os.path.join(FIG, "estatisticas.py")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        arvore = ast.parse(f.read())
    for no in ast.walk(arvore):
        if isinstance(no, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "W"
                                              for t in no.targets):
            return ast.literal_eval(no.value)
    return None


def carregar_dados():
    D, faltas = {}, []
    for chave, nome in FICHEIROS.items():
        p = os.path.join(RES, nome)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                D[chave] = json.load(f)
        else:
            faltas.append(nome)
    D["pesos_estatisticas"] = _pesos_estatisticas()
    return D, faltas


def _fonte(D):
    return por_celula(D["fontes"]["celulas"], "fontes_HV/RESULTADO_A13_COMPLETO.json")


# --------------------------------------------------------------- V0
@protegido("V0", "integridade das derivações")
def v0(D):
    out = []
    F = _fonte(D)
    A = por_celula(D["grelha"]["celulas"], FICHEIROS["grelha"])
    B = por_celula(D["grelha13"]["celulas"], FICHEIROS["grelha13"])
    n = len(UNIVERSO) * len(CAMPOS)
    dif = [(k, c) for k in sorted(UNIVERSO) for c in CAMPOS
           if A[k][c] != round(F[k]["necessidades"]["verificada"][c], 3)]
    out.append(resultado("V0", "grelha DGEG2025-A = fonte HV (necessidades.verificada) a 3 casas",
                         not dif, "integridade", f"{n - len(dif)}/{n} valores"
                         + (f"; primeiro diferente {dif[0]}" if dif else "")))
    dif = [(k, c) for k in sorted(UNIVERSO) for c in CAMPOS_2013
           if B[k][c] != round(F[k]["controlo_REG2013"][c], 3)]
    out.append(resultado("V0", "grelha REG-2013 = fonte (controlo_REG2013) a 3 casas",
                         not dif, "integridade", f"{n - len(dif)}/{n} valores"
                         + (f"; primeiro diferente {dif[0]}" if dif else "")))
    anat = [c["anatomia"] for c in D["intermed"]["celulas"] if c["hora"] == "verificada"]
    out.append(resultado("V0", "decomposição DGEG2025-A = anatomia HV dos intermediários",
                         anat == D["decomp"]["celulas"], "integridade",
                         f"{len(anat)} células HV nos intermediários; "
                         f"{len(D['decomp']['celulas'])} no ficheiro depositado"))
    pe = D["pesos_estatisticas"]
    out.append(resultado("V0", "pesos do parque iguais aos de figures/estatisticas.py",
                         pe == PESO, "integridade", f"estatisticas.py: {pe}"))
    return out


# --------------------------------------------------------------- V1
def _mpr(cs, num, den):
    tot = sum(PESO[c["rb"]] for c in cs)
    return sum(PESO[c["rb"]] * (c[num] / c[den] - 1) * 100 for c in cs) / tot


def _agregado(cs, num, den):
    """Rácio das necessidades ponderadas (não média de rácios)."""
    n = d = 0.0
    for rb, w in PESO.items():
        g = [c for c in cs if c["rb"] == rb]
        n += w * sum(c[num] for c in g) / len(g)
        d += w * sum(c[den] for c in g) / len(g)
    return (n / d - 1) * 100


@protegido("V1", "agregação ponderada")
def v1(D):
    A = list(por_celula(D["grelha"]["celulas"], FICHEIROS["grelha"]).values())
    B = list(por_celula(D["grelha13"]["celulas"], FICHEIROS["grelha13"]).values())
    return [
        ancora("V1", "média ponderada dos rácios, DGEG2025-A",
               _mpr(A, "nh_52016", "nic_13790"), "17.54", ("17.5", "§3.4")),
        ancora("V1", "média ponderada dos rácios, REG-2013",
               _mpr(B, "nh_52016_2013", "nic_13790_2013"), "9.82", ("9.8", "§3.4")),
        ancora("V1", "rácio das necessidades ponderadas, DGEG2025-A",
               _agregado(A, "nh_52016", "nic_13790"), "10.4", ("10.4", "§3.4, §5")),
        ancora("V1", "rácio das necessidades ponderadas, REG-2013",
               _agregado(B, "nh_52016_2013", "nic_13790_2013"), "2.8", ("2.8", "§3.4, §5")),
    ]


# --------------------------------------------------------------- V2
@protegido("V2", "cruzamento ingénuo RB6/Coimbra")
def v2(D, hora="verificada"):
    c = _fonte(D)[("RB6", "Coimbra")]
    v = c["necessidades"][hora]          # leitor explícito: a hora escolhe-se aqui
    r = c["controlo_REG2013"]
    ingenuo = (v["nh_52016"] / r["nic_13790_2013"] - 1) * 100
    met25 = (v["nh_52016"] / v["nic_13790"] - 1) * 100
    met13 = (r["nh_52016_2013"] / r["nic_13790_2013"] - 1) * 100
    sub = (1 - ingenuo / met25) * 100
    out = [
        ancora("V2", f"cruzamento ingénuo (hora {hora})", ingenuo, "9.71", ("9.7", "§3.1")),
        ancora("V2", f"efeito de método DGEG2025-A (hora {hora})", met25, "16.48", ("16.5", "§3.1")),
        ancora("V2", "efeito de método REG-2013", met13, "10.07", ("10.1", "§3.1")),
        ancora("V2", "rácio efeito DGEG / cruzamento ingénuo", met25 / ingenuo, "1.70"),
        resultado("V2", "subestimação do efeito DGEG, «about 40%» (§3.1)",
                  round(sub / 10) * 10 == 40, "ancora",
                  f"{sub:.2f}% → dezena {round(sub / 10) * 10}"),
    ]
    cz = D["cruz"]
    pares = (("cruzamento_ingenuo", ingenuo), ("efeito_metodo_dgeg", met25),
             ("efeito_metodo_2013", met13))
    dif = [(k, cz[k], f"{x:.2f}") for k, x in pares if f"{cz[k]:.2f}" != f"{x:.2f}"]
    out.append(resultado("V2", "cruzamento_ingenuo_rb6_coimbra_REVISAO.json = recalculado a 2 casas",
                         not dif, "integridade", "3/3 campos" if not dif else f"diferentes: {dif}"))
    return out


# --------------------------------------------------------------- V3
@protegido("V3", "G_sul de referência")
def v3(D):
    out = []
    g = D["gsul"]
    jan = g["meta"]["janelas"]
    out.append(resultado("V3", "janela de produção Out–Abr = meses 10, 11, 12, 1, 2, 3, 4",
                         set(jan["Out–Abr"]) == JANELA_PRODUCAO and len(jan["Out–Abr"]) == 7,
                         "janela", f"artefacto: {sorted(jan['Out–Abr'])}"))
    gs = g["gsul_por_cidade_e_janela"]["Coimbra"]
    out.append(ancora("V3", "G_sul Coimbra, Out–Abr (produção)", gs["Out–Abr"], "96.54",
                      ("96.5", "§3.3, §4.4, Tabela 2")))
    out.append(ancora("V3", "G_sul Coimbra, Nov–Mar", gs["Nov–Mar"], "92.2",
                      ("92.2", "§3.3, §4.4, Tabela 2")))
    # Cruzamento entre dois artefactos: o G_sul do g_sul tem de sair da
    # irradiância mensal HV gravada na fonte completa, com a mesma janela.
    irr = D["fontes"]["climas"]["Coimbra"]["irradiancia_mensal_kWh_m2"]["verificada"]
    meses = jan["Out–Abr"]
    da_fonte = sum(irr[str(m)]["SV"] for m in meses) / len(meses)
    d = abs(da_fonte - gs["Out–Abr"])
    out.append(resultado("V3", "G_sul do artefacto g_sul = irradiância SV da fonte HV, mesma janela",
                         d < TOL_REGRESSAO, "integridade", f"fonte {da_fonte:.10f}; |dif| {d:.2e}"))
    obs = {(c["rb"], c["cidade"], c["janela"]) for c in g["celulas"]}
    esperado = {(rb, cid, j) for rb, cid in UNIVERSO for j in JANELAS_GSUL}
    out.append(resultado("V3", "g_sul: 128 observações únicas (32 células × 4 janelas)",
                         obs == esperado and len(g["celulas"]) == 128, "cobertura",
                         f"{len(g['celulas'])} registos, {len(obs)} únicos"))
    nm = [c["delta_pct"] for c in g["celulas"] if c["janela"] == "Nov–Mar"]
    out.append(ancora("V3", "propagação Nov–Mar em N_ic: mínimo", min(nm), "-3.2", ("-3.2", "§4.4")))
    out.append(ancora("V3", "propagação Nov–Mar em N_ic: máximo", max(nm), "4.4", ("4.4", "§4.4")))
    return out


# --------------------------------------------------------------- V4
@protegido("V4", "efeito de base")
def v4(D):
    A = por_celula(D["grelha"]["celulas"], FICHEIROS["grelha"])
    B = por_celula(D["grelha13"]["celulas"], FICHEIROS["grelha13"])
    ks = sorted(UNIVERSO)
    saz = [100 * (A[k]["nic_13790"] / B[k]["nic_13790_2013"] - 1) for k in ks]
    men = [100 * (A[k]["nh_52016"] / B[k]["nh_52016_2013"] - 1) for k in ks]
    return [
        ancora("V4", "efeito de base, sazonal, mediana", st.median(saz), "-0.8", ("-0.8", "§3.1")),
        ancora("V4", "efeito de base, sazonal, mínimo", min(saz), "-34.6", ("-34.6", "§3.1")),
        ancora("V4", "efeito de base, sazonal, máximo", max(saz), "28.5", ("28.5", "§3.1")),
        ancora("V4", "efeito de base, mensal, mediana", st.median(men), "5.4", ("5.4", "§3.1")),
        ancora("V4", "efeito de base, mensal, mínimo", min(men), "-27.2", ("-27.2", "§3.1")),
        ancora("V4", "efeito de base, mensal, máximo", max(men), "23.0", ("23.0", "§3.1")),
    ]


# --------------------------------------------------------------- V5 (informativo)
def _sem_acentos(s):
    return "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch))


def v5(D, a14_path):
    nome = "A13 mensal contra o braço mensal canónico do A14 (12 células)"
    if not a14_path:
        return [info("V5", nome, "não executado: grelha do A14 não indicada (--a14 ou --motor); "
                                 "não faz parte deste depósito")]
    if not os.path.exists(a14_path):
        return [info("V5", nome, f"não executado: {a14_path} não existe")]
    try:
        with open(a14_path, encoding="utf-8") as f:
            a14 = json.load(f)
        ref = {(c["rb"], _sem_acentos(c["cidade"])): c for c in a14["celulas"]
               if c.get("alfa", 0.4) == 0.4}
        F = _fonte(D)
        comp = []
        for rb in AMOSTRA_A14:
            for cid in CIDADES:
                k = (rb, _sem_acentos(cid))
                if k not in ref:
                    continue
                v = F[(rb, cid)]["necessidades"]["verificada"]
                for a13c, a14c in (("nh_52016", "nh_men"), ("nc_52016", "nc_men")):
                    comp.append((abs(v[a13c] - ref[k][a14c]), rb, cid, a13c, v[a13c], ref[k][a14c]))
        if not comp:
            return [info("V5", nome, "nenhuma célula comum")]
        d, rb, cid, campo, x13, x14 = max(comp)
        horas = sorted({str(c.get("hora_geometria")) for c in a14["celulas"]})
        return [info("V5", nome,
                     f"{len(comp) // 2} células, {len(comp)} valores; máximo {d:.4f} kWh/m²·a em "
                     f"{rb}/{cid} {campo} (A13 {x13:.4f}, A14 {x14:.4f}); A13 em hora verificada; "
                     f"A14 hora_geometria={horas}. Não conta, não faz falhar; este depósito não "
                     f"afirma identidade dos resultados mensais.")]
    except Exception as e:  # noqa: BLE001 — informativo: nunca faz falhar
        return [info("V5", nome, f"não executado: {e!r}")]


# --------------------------------------------------------------- V6
@protegido("V6", "sensibilidade α = 0,60")
def v6(D):
    s = D["alfa060"]
    A = list(por_celula(s["dgeg2025a"], "alfa060.dgeg2025a").values())
    B = list(por_celula(s["reg2013"], "alfa060.reg2013").values())
    dH = [100 * (c["nh_52016"] / c["nic_13790"] - 1) for c in A]
    dH13 = [100 * (c["nh_52016_2013"] / c["nic_13790_2013"] - 1) for c in B]
    dC = [100 * (c["nc_52016"] / c["nvc_13790"] - 1) for c in A]
    dC13 = [100 * (c["nc_52016_2013"] / c["nvc_13790_2013"] - 1) for c in B]
    G = list(por_celula(D["grelha"]["celulas"], FICHEIROS["grelha"]).values())
    G13 = list(por_celula(D["grelha13"]["celulas"], FICHEIROS["grelha13"]).values())
    dC40 = [100 * (c["nc_52016"] / c["nvc_13790"] - 1) for c in G]
    dC13_40 = [100 * (c["nc_52016_2013"] / c["nvc_13790_2013"] - 1) for c in G13]
    out = [
        resultado("V6", "configuração do ficheiro: alfa_parede = 0,60",
                  s["meta"]["config"]["alfa_parede"] == 0.6, "configuracao",
                  f"meta.config = {s['meta']['config']}"),
        ancora("V6", "α=0,60, DGEG2025-A: mediana do efeito de método (aquecimento)",
               st.median(dH), "18.70", ("18.7", "§4.4, Tabela 2")),
        ancora("V6", "α=0,60, REG-2013: mediana do efeito de método (aquecimento)",
               st.median(dH13), "13.0", ("13.0", "§4.4")),
    ]
    mudanca = max(abs(st.median(dC) - st.median(dC40)), abs(st.median(dC13) - st.median(dC13_40)))
    out.append(resultado("V6", "medianas do arrefecimento a menos de 2 pp das de α=0,40 (§4.4)",
                         mudanca < 2.0, "ancora",
                         f"DGEG {st.median(dC40):.2f} → {st.median(dC):.2f}; "
                         f"REG {st.median(dC13_40):.2f} → {st.median(dC13):.2f}; maior {mudanca:.2f} pp"))
    dec = D["decomp060"]["celulas"]
    menos = [c for c in dec if c["gamma_C_sazonal"] < 1]
    neg = [(c["rb"], c["cidade"]) for c in menos if c["dC"] < 0]
    out.append(resultado("V6", "α=0,60: nenhuma célula com γ_C < 1 diverge para baixo (§4.4)",
                         len(dec) == 32 and not neg, "ancora",
                         f"{len(menos)} células com γ_C < 1; negativas: {neg or 'nenhuma'}"))
    taxas = []
    for nome, chave in (("α=0,40", "decomp"), ("α=0,60", "decomp060")):
        cs = D[chave]["celulas"]
        bem = sum(1 for c in cs if c["gamma_C_sazonal"] >= 1 and c["dC"] < 0) + \
            sum(1 for c in cs if c["gamma_C_sazonal"] < 1 and c["dC"] > 0)
        taxas.append(f"{nome} {bem}/{len(cs)}")
    out.append(info("V6", "classificação pelo critério γ_C (hora verificada)",
                    "; ".join(taxas) + ". O estado α=0,04 (29/32, versão submetida) foi "
                    "calculado em hora de cabeçalho e não é recalculado aqui."))
    return out


# --------------------------------------------------------------- V7
@protegido("V7", "sensibilidades da Tabela 2")
def v7(D):
    out = []
    e = D["eq97"]["celulas"]
    tocadas = [c for c in e if c["meses_gamma_gt2"] > 0]
    out.append(resultado("V7", "Eq. (97): 55 das 64 avaliações mensais, 87 meses, 49 células com "
                               "deslocamento não nulo (§2.4)",
                         (len(e), len(tocadas), sum(c["meses_gamma_gt2"] for c in e),
                          sum(1 for c in e if c["deslocamento_pp"] != 0)) == (64, 55, 87, 49),
                         "ancora", f"{len(e)} avaliações; {len(tocadas)} tocadas; "
                                   f"{sum(c['meses_gamma_gt2'] for c in e)} meses; "
                                   f"{sum(1 for c in e if c['deslocamento_pp'] != 0)} não nulas"))
    for base, med, mn, h0, h1 in (("DGEG2025-A", "-0.52", "-2.6", "15.6", "15.0"),
                                  ("REG-2013", "-0.01", "-4.0", "11.0", "10.6")):
        c = [x for x in e if x["base"] == base]
        out.append(ancora("V7", f"Eq. (97), {base}: mediana do deslocamento (pp)",
                          st.median([x["deslocamento_pp"] for x in c]), med, (med, "§2.4")))
        out.append(ancora("V7", f"Eq. (97), {base}: maior deslocamento (pp)",
                          min(x["deslocamento_pp"] for x in c), mn, (mn, "§2.4")))
        out.append(ancora("V7", f"Eq. (97), {base}: mediana sem corte",
                          st.median([x["dH_sem_corte"] for x in c]), h0, (h0, "§2.4")))
        out.append(ancora("V7", f"Eq. (97), {base}: mediana com corte",
                          st.median([x["dH_com_corte"] for x in c]), h1, (h1, "§2.4")))
    troca = [(x["base"], x["rb"], x["cidade"]) for x in e if (x["dH_sem_corte"] > 0) != (x["dH_com_corte"] > 0)]
    out.append(resultado("V7", "Eq. (97): nenhuma célula muda de sinal (§2.4)", not troca, "ancora",
                         f"mudanças de sinal: {troca or 'nenhuma'}"))
    s = D["sombra"]["celulas"]
    f = [x["fator_nvc"] for x in s]
    gC = [x["fator_gamma_c"] for x in s]
    out.append(resultado("V7", "sombreamento: 64 avaliações e referência = produção", len(s) == 64 and all(
        abs(x["nvc_com_protecao"] - x["nvc_ref_producao"]) < 1e-9 for x in s), "integridade", f"{len(s)} avaliações"))
    out.append(ancora("V7", "sem sombreamento: factor de N_vc, mediana", st.median(f), "1.89", ("1.89", "Tabela 2")))
    out.append(ancora("V7", "sem sombreamento: factor de N_vc, mínimo", min(f), "1.25", ("1.25", "Tabela 2")))
    out.append(ancora("V7", "sem sombreamento: factor de N_vc, máximo", max(f), "3.46", ("3.46", "Tabela 2")))
    out.append(ancora("V7", "sem sombreamento: factor de γ_C, mediana", st.median(gC), "1.28", ("1.28", "Tabela 2")))
    h = D["hgr"]["celulas"]
    d = [x["deslocamento_max_pp"] for x in h]
    muda = [x for x in h if x["muda_sinal"]]
    out.append(ancora("V7", "H_gr ±22 %: mediana do deslocamento (pp)", st.median(d), "0.8",
                      ("0.8", "§4.4, Tabela 2")))
    out.append(ancora("V7", "H_gr ±22 %: maior deslocamento (pp)", max(d), "1.95", ("1.95", "§4.4, Tabela 2")))
    out.append(resultado("V7", "H_gr ±22 %: uma só mudança de sinal, a menos de 1 pp de zero (§4.4)",
                         len(muda) == 1 and abs(muda[0]["dH_base"]) < 1.0, "ancora",
                         f"{[(x['base'], x['rb'], x['cidade'], x['dH_base']) for x in muda]}"))
    i = D["isol"]["celulas"]
    for k, base, med, mn, mx in (("dgeg", "DGEG2025-A", "2.2", "1.0", "4.5"),
                                 ("2013", "REG-2013", "2.1", "0.9", "4.0")):
        v = [x[f"dH_{k}_diferenca"] for x in i]
        out.append(ancora("V7", f"isolamento do solo (b_tr = 0,8), {base}: mediana (pp)",
                          st.median(v), med, (med, "§3.3")))
        out.append(ancora("V7", f"isolamento do solo, {base}: mínimo", min(v), mn, (mn, "§3.3")))
        out.append(ancora("V7", f"isolamento do solo, {base}: máximo", max(v), mx, (mx, "§3.3")))
    v = [x[f"dH_{k}_diferenca"] for x in i for k in ("dgeg", "2013")]
    out.append(resultado("V7", "isolamento do solo: a mesma direcção nas 32 avaliações (§3.3)",
                         len(v) == 32 and all(x > 0 for x in v), "ancora", f"{sum(1 for x in v if x > 0)}/{len(v)} positivas"))
    return out


# --------------------------------------------------------------- motor (físicas)
def carregar_motor(raiz):
    """Importa o motor do autor a partir de `raiz`. Devolve (módulos, erro)."""
    raiz = os.path.abspath(raiz)
    src = os.path.join(raiz, "src")
    est = os.path.join(raiz, "studies", "a13_iso52016_mensal")
    for p in (os.path.join(src, "e4", "__init__.py"), os.path.join(est, "run_grelha_artigo13.py")):
        if not os.path.exists(p):
            return None, f"não encontrado: {p}"
    sys.path[:0] = [src, est]
    try:
        import e4
        import run_grelha_artigo13 as g
        from e4 import solar, geometria
        from e4.clima_horario_a14 import ler_epw_com_hora
    except Exception as e:  # noqa: BLE001
        return None, f"import do motor falhou: {e!r}"
    for mod, base in ((e4, src), (g, est)):
        if not os.path.normcase(os.path.abspath(mod.__file__)).startswith(os.path.normcase(base)):
            return None, f"{mod.__name__} veio de {mod.__file__}, não de {base}"
    return dict(g=g, solar=solar, geometria=geometria, ler=ler_epw_com_hora,
                raiz=raiz, versao=getattr(e4, "__version__", "?")), None


def _aplicar(M, cfg):
    """A configuração R1 NOS DOIS RAMOS, em runtime, como o produtor."""
    g, solar, geo = M["g"], M["solar"], M["geometria"]
    antes = dict(a52=g.A_SOL_PAREDE, d52=g.R_DESVAO_COB, hce=g.H_CE,
                 a13=solar.ALFA_PAREDE, d13=geo.R_DESVAO_COB)
    g.A_SOL_PAREDE = cfg["alfa_parede"]
    g.R_DESVAO_COB = cfg["desvao_cob"]
    g.H_CE = cfg["h_ce"]
    solar.ALFA_PAREDE = cfg["alfa_parede"]
    geo.R_DESVAO_COB = cfg["desvao_cob"]
    return antes


def _repor(M, antes):
    g, solar, geo = M["g"], M["solar"], M["geometria"]
    g.A_SOL_PAREDE, g.R_DESVAO_COB, g.H_CE = antes["a52"], antes["d52"], antes["hce"]
    solar.ALFA_PAREDE, geo.R_DESVAO_COB = antes["a13"], antes["d13"]


def _serie(M, cidade, hora):
    g = M["g"]
    epw = os.path.join(M["raiz"], "src", "e4", "fixtures", "clima", g._EPW[cidade] + ".epw")
    regs, loc = M["ler"](epw, hora)
    return (g.irradiancia_mensal_por_orientacao(regs, loc), g.horas_por_mes(regs),
            g.theta_ext_media_mensal(regs), g.theta_ext_anual_media(regs))


@protegido("F1", "paridade de envolvente")
def f1(M, quebrar=False):
    g, solar, geo = M["g"], M["solar"], M["geometria"]
    out = []
    antes = _aplicar(M, CONFIG_R1)
    try:
        if quebrar:                        # controlo negativo: um ramo só
            solar.ALFA_PAREDE = antes["a13"]
        pares = (("absortância da parede", g.A_SOL_PAREDE, solar.ALFA_PAREDE, 0.40),
                 ("absortância da cobertura", g.A_SOL_COBERTURA, solar.ALFA_COBERTURA, 0.50),
                 ("resistência do desvão", g.R_DESVAO_COB, geo.R_DESVAO_COB, 0.0))
        for nome, a52, a13, esp in pares:
            out.append(resultado("F1", f"{nome}: ramo mensal = ramo sazonal = {esp}",
                                 a52 == a13 == esp, "paridade", f"52016={a52}; 13790={a13}"))
        out.append(resultado("F1", "coeficientes próprios de cada ramo: h_ce=20,0 e h_re=4,14 "
                                   "(mensal); R_se=0,04 (sazonal)",
                             (g.H_CE, g.H_RE, solar.R_SE) == (20.0, 4.14, 0.04), "paridade",
                             f"h_ce={g.H_CE}; h_re={g.H_RE}; R_se={solar.R_SE}"))
    finally:
        _repor(M, antes)
    agora = dict(a52=g.A_SOL_PAREDE, d52=g.R_DESVAO_COB, hce=g.H_CE,
                 a13=solar.ALFA_PAREDE, d13=geo.R_DESVAO_COB)
    out.append(resultado("F1", "módulos partilhados repostos depois da sobreposição",
                         agora == antes, "reposicao", f"valores por omissão: {antes}"))
    return out


@protegido("F2", "RB6/Coimbra recalculada")
def f2(M, D):
    g = M["g"]
    ref = _fonte(D)[("RB6", "Coimbra")]
    out = []
    antes = _aplicar(M, CONFIG_R1)
    try:
        calc = {}
        for hora in ("verificada", "cabecalho"):
            s = _serie(M, "Coimbra", hora)
            nic, nvc = g.celula_13790("RB6", "Coimbra", g._clima_dgeg2025_a("Coimbra", s[0]))
            nh, nc, nh20 = g.celula_52016("RB6", s)
            calc[hora] = dict(nic_13790=nic, nvc_13790=nvc, nh_52016=nh, nc_52016=nc,
                              nh20_52016_cenario=nh20)
        nic13, nvc13 = g.celula_13790_2013("RB6", "Coimbra")
        nh13, nc13, nh20_13 = g.celula_52016_2013("RB6", "Coimbra")
    finally:
        _repor(M, antes)
    for hora in ("verificada", "cabecalho"):
        d = max(abs(calc[hora][c] - ref["necessidades"][hora][c]) for c in CAMPOS)
        out.append(resultado("F2", f"motor, leitor «{hora}» = fonte necessidades.{hora} (5 campos)",
                             d < TOL_REGRESSAO, "regressao", f"|dif| máximo {d:.2e}"))
    reg = dict(zip(CAMPOS_2013, (nic13, nvc13, nh13, nc13, nh20_13)))
    d = max(abs(reg[c] - ref["controlo_REG2013"][c]) for c in CAMPOS_2013)
    out.append(resultado("F2", "motor, REG-2013 = fonte controlo_REG2013 (5 campos)",
                         d < TOL_REGRESSAO, "regressao", f"|dif| máximo {d:.2e}"))
    d = abs(calc["verificada"]["nh_52016"] - calc["cabecalho"]["nh_52016"])
    out.append(resultado("F2", "controlo interno: o leitor de cabeçalho dá outro N_H",
                         d > 1e-6, "leitor", f"|N_H verificada − N_H cabeçalho| = {d:.6f}"))
    v = calc["verificada"]
    ing = (v["nh_52016"] / nic13 - 1) * 100
    out.append(ancora("F2", "cruzamento ingénuo recalculado", ing, "9.71", ("9.7", "§3.1")))
    out.append(ancora("F2", "rácio efeito DGEG / ingénuo recalculado",
                      (v["nh_52016"] / v["nic_13790"] - 1) * 100 / ing, "1.70"))
    return out


@protegido("F3", "G_sul recalculado")
def f3(M, D, janela=None):
    g = M["g"]
    meses = tuple(janela) if janela else tuple(g._MESES_FORA_JJAS)
    out = [resultado("F3", "janela do produtor (_MESES_FORA_JJAS) = Out–Abr",
                     set(meses) == JANELA_PRODUCAO and len(meses) == 7, "janela",
                     f"produtor: {sorted(meses)}")]
    irr = _serie(M, "Coimbra", "verificada")[0]
    gs = sum(irr[m]["SV"] for m in meses) / len(meses)
    ref = D["gsul"]["gsul_por_cidade_e_janela"]["Coimbra"]["Out–Abr"]
    out.append(resultado("F3", "G_sul Coimbra do EPW (hora verificada) = artefacto g_sul",
                         abs(gs - ref) < TOL_REGRESSAO, "regressao",
                         f"{gs:.10f}; |dif| {abs(gs - ref):.2e}"))
    out.append(ancora("F3", "G_sul Coimbra recalculado", gs, "96.54", ("96.5", "§3.3")))
    return out


# --------------------------------------------------------------- execução
VERIFICACOES_DADOS = (("V0", "Integridade das derivações", v0),
                      ("V1", "Agregação ponderada (§3.4)", v1),
                      ("V2", "Cruzamento ingénuo RB6/Coimbra (§3.1)", v2),
                      ("V3", "G_sul de referência, Coimbra (§3.3, §4.4)", v3),
                      ("V4", "Efeito de base REG-2013 → DGEG2025-A (§3.1)", v4))


def correr(D, faltas, motor, a14_path):
    todos = []

    def bloco(titulo, rs):
        print("\n" + "=" * 76)
        print(titulo)
        print("=" * 76)
        for r in rs:
            m = f" [razão: {r['motivo']}]" if r["motivo"] else ""
            print(f"  [{r['estado']}] {r['nome']}{m}" + (f" — {r['detalhe']}" if r["detalhe"] else ""))
        todos.extend(rs)

    print("verificar_revisao_a13.py — depósito A13 R1 (ENB-D-26-06604)")
    print(f"raiz do depósito: {RAIZ}")
    if faltas:
        bloco("Ficheiros de dados", [resultado("V0", f"presente: resultados/{n}", False, "ausente", "")
                                     for n in faltas])
        print("\nFicheiros em falta: as verificações que dependem deles não correm.")
    else:
        for vid, titulo, fn in VERIFICACOES_DADOS:
            bloco(f"{vid} — {titulo}", fn(D))
        bloco("V5 — A13 ↔ A14, braço mensal (INFORMATIVO)", v5(D, a14_path))
        bloco("V6 — Sensibilidade α = 0,60 (§4.4)", v6(D))
        bloco("V7 — Sensibilidades da Tabela 2 (§2.4, §3.3, §4.4)", v7(D))

    titulo_f = "F1–F3 — Verificações físicas (motor do autor)"
    if motor is None:
        bloco(titulo_f, [skip(f, "verificação física", "motor não indicado (--motor ou E4_MOTOR); "
                                                        "pacote privado, disponível a pedido")
                         for f in ("F1", "F2", "F3")])
    else:
        M, erro = motor
        if erro:
            bloco(titulo_f, [resultado(f, "motor utilizável", False, "motor", erro)
                             for f in ("F1", "F2", "F3")])
        elif faltas:
            bloco(titulo_f, [resultado("F2", "dados para a regressão", False, "ausente",
                                       ", ".join(faltas))])
        else:
            print(f"\nmotor: {M['raiz']} (e4 {M['versao']})")
            bloco("F1 — Paridade de envolvente na configuração R1", f1(M))
            bloco("F2 — RB6/Coimbra recalculada, leitor de hora explícito", f2(M, D))
            bloco("F3 — G_sul de Coimbra recalculado do EPW", f3(M, D))

    n = {e: sum(1 for r in todos if r["estado"] == e) for e in ("PASS", "FALHA", "SKIP", "INFO")}
    print("\n" + "=" * 76)
    print(f"RESULTADO: {n['PASS']} PASS · {n['FALHA']} FALHA · {n['SKIP']} SKIP · {n['INFO']} INFO")
    if n["FALHA"]:
        print("Falhas:")
        for r in todos:
            if r["estado"] == "FALHA":
                print(f"   • {r['vid']} {r['nome']} [razão: {r['motivo']}]")
    print("Código de saída:", 1 if n["FALHA"] else 0)
    print("=" * 76)
    return 1 if n["FALHA"] else 0


# --------------------------------------------------------------- controlos negativos
def _cel(lista, rb, cid):
    return next(c for c in lista if c["rb"] == rb and c["cidade"] == cid)


def _p_v0(D):
    _cel(D["fontes"]["celulas"], "RB6", "Coimbra")["necessidades"]["verificada"]["nh_52016"] += 0.01


def _p_v1(D):
    _cel(D["grelha"]["celulas"], "RB6", "Coimbra")["nh_52016"] *= 1.05


def _p_v2(D):
    n = _cel(D["fontes"]["celulas"], "RB6", "Coimbra")["necessidades"]
    n["verificada"] = copy.deepcopy(n["cabecalho"])


def _p_v2b(D):
    D["cruz"]["cruzamento_ingenuo"] = 11.19


def _p_v3(D):
    D["gsul"]["meta"]["janelas"]["Out–Abr"] = [11, 12, 1, 2, 3]


def _p_v3b(D):
    D["gsul"]["gsul_por_cidade_e_janela"]["Coimbra"]["Out–Abr"] += 0.01


def _p_v4(D):
    for c in D["grelha13"]["celulas"]:
        c["nic_13790_2013"] *= 0.98


def _p_v6(D):
    for c in D["alfa060"]["dgeg2025a"]:
        c["nh_52016"] *= 1.02


def _p_v7(D):
    for c in D["eq97"]["celulas"]:
        if c["base"] == "DGEG2025-A":
            c["deslocamento_pp"] *= 2


# id: (descrição, perturbação, verificação alvo, razão esperada)
CONTROLOS = {
    "V0": ("fonte HV RB6/Coimbra: N_H + 0,01", _p_v0, v0, "integridade"),
    "V1": ("grelha DGEG RB6/Coimbra: N_H × 1,05", _p_v1, v1, "ancora"),
    "V2": ("RB6/Coimbra: necessidades em hora de cabeçalho no lugar das verificadas", _p_v2, v2, "ancora"),
    "V2b": ("cruzamento depositado: 11,19 (o valor público anterior)", _p_v2b, v2, "integridade"),
    "V3": ("janela Out–Abr redefinida como Nov–Mar no artefacto", _p_v3, v3, "janela"),
    "V3b": ("G_sul Coimbra Out–Abr + 0,01 no artefacto g_sul", _p_v3b, v3, "integridade"),
    "V4": ("grelha REG: N_ic × 0,98 nas 32 células", _p_v4, v4, "ancora"),
    "V6": ("α=0,60 DGEG: N_H × 1,02 nas 32 células", _p_v6, v6, "ancora"),
    "V7": ("Eq. (97) DGEG: deslocamentos × 2", _p_v7, v7, "ancora"),
}


def _v5_sobre(D, a14):
    """V5 sobre um A14 já carregado e alterado em memória (só para o controlo)."""
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "a14.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(a14, f)
        return v5(D, p)


def controlos_negativos(D, faltas, motor, a14_path):
    if faltas:
        print("Ficheiros em falta:", ", ".join(faltas), "— controlos negativos não executáveis.")
        return 1
    print("Linha de base primeiro (dados por perturbar):")
    base = [r for _, _, fn in VERIFICACOES_DADOS for r in fn(D)] + v6(D) + v7(D)
    nf = sum(1 for r in base if r["estado"] == "FALHA")
    print(f"  {len(base)} resultados, {nf} FALHA")
    if nf:
        print("⛔ A linha de base falha: os controlos negativos não provariam nada. Parar.")
        return 1
    total = nao = 0
    print("\nControlos negativos (perturbação em memória; nada se escreve no disco):")
    for cid, (desc, pert, fn, razao) in CONTROLOS.items():
        P = copy.deepcopy(D)
        pert(P)
        mudou = json.dumps(P, sort_keys=True, ensure_ascii=False) != \
            json.dumps(D, sort_keys=True, ensure_ascii=False)
        falhas = [r for r in fn(P) if r["estado"] == "FALHA"]
        certas = [r for r in falhas if r["motivo"] == razao]
        ok = mudou and bool(certas)
        total += 1
        nao += 0 if ok else 1
        print(f"  [{'DETECTADO' if ok else 'NÃO DETECTADO'}] CN-{cid}: {desc}")
        print(f"      a perturbação mudou os dados: {mudou}; falhas: {len(falhas)}; "
              f"pela razão esperada «{razao}»: {len(certas)}"
              + (f" — {certas[0]['nome']}" if certas else
                 (f"; razões obtidas: {sorted({str(r['motivo']) for r in falhas})}" if falhas else "")))
    # O V5 só relata: uma perturbação enorme do A14 não pode dar FALHA.
    if a14_path and os.path.exists(a14_path):
        with open(a14_path, encoding="utf-8") as f:
            a14 = json.load(f)
        for c in a14["celulas"]:
            c["nh_men"] = c.get("nh_men", 0.0) + 100.0
        rs = _v5_sobre(D, a14)
        ok = all(r["estado"] == "INFO" for r in rs) and "não executado" not in rs[0]["detalhe"]
        total += 1
        nao += 0 if ok else 1
        print(f"  [{'DETECTADO' if ok else 'NÃO DETECTADO'}] CN-V5: A14 com N_H + 100 → o V5 continua "
              f"INFO e regista o desvio, sem FALHA")
    else:
        print("  [SKIP] CN-V5: grelha do A14 não indicada")
    # Código de saída, de ponta a ponta, em processos separados (sem motor).
    exe = [sys.executable, os.path.abspath(__file__)]
    env = {k: v for k, v in os.environ.items() if k not in ("E4_MOTOR", "A13_VERIF_PERTURBAR")}
    rc0 = subprocess.run(exe, env=env, capture_output=True).returncode
    env["A13_VERIF_PERTURBAR"] = "V1"
    rc1 = subprocess.run(exe, env=env, capture_output=True).returncode
    ok = rc0 == 0 and rc1 == 1
    total += 1
    nao += 0 if ok else 1
    print(f"  [{'DETECTADO' if ok else 'NÃO DETECTADO'}] CN-saída: processo sem perturbação → {rc0} "
          f"(esperado 0); com a perturbação do CN-V1 → {rc1} (esperado 1)")
    if motor is not None:
        M, erro = motor
        total += 1
        if erro:
            print(f"  [NÃO DETECTADO] CN-F: motor inutilizável ({erro})")
            nao += 1
        else:
            total += 1
            for cid, desc, rs, razao in (
                    ("F1", "só o ramo mensal recebe α=0,40", f1(M, quebrar=True), "paridade"),
                    ("F3", "janela Nov–Mar no lugar da do produtor", f3(M, D, janela=(11, 12, 1, 2, 3)),
                     "janela")):
                certas = [r for r in rs if r["estado"] == "FALHA" and r["motivo"] == razao]
                nao += 0 if certas else 1
                print(f"  [{'DETECTADO' if certas else 'NÃO DETECTADO'}] CN-{cid}: {desc} → "
                      f"pela razão «{razao}»: {len(certas)}")
            print("  [INFO] CN-F2: o controlo do leitor de cabeçalho corre dentro do F2 (razão «leitor»)")
    print("\n" + "=" * 76)
    print(f"CONTROLOS NEGATIVOS: {total - nao}/{total} detectados pela razão esperada")
    print("Código de saída:", 1 if nao else 0)
    print("=" * 76)
    return 1 if nao else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Verificação numérica do depósito A13 R1.")
    ap.add_argument("--motor", default=os.environ.get("E4_MOTOR"),
                    help="raiz do motor do autor (src/e4 + studies/a13_iso52016_mensal)")
    ap.add_argument("--a14", default=None, help="grelha canónica do A14, para o V5 (informativo)")
    ap.add_argument("--controlo-negativo", action="store_true",
                    help="um controlo negativo por verificação")
    a = ap.parse_args(argv)
    D, faltas = carregar_dados()
    motor = carregar_motor(a.motor) if a.motor else None
    a14 = a.a14
    if a14 is None and motor is not None and not motor[1]:
        a14 = os.path.join(motor[0]["raiz"], "studies", "a14_iso52016_horario", "resultados",
                           "grelha_a14_canonica.json")
    if a.controlo_negativo:
        return controlos_negativos(D, faltas, motor, a14)
    pert = os.environ.get("A13_VERIF_PERTURBAR")
    if pert:                                # só para o CN-saída
        print(f"⚠ perturbação em memória activa: CN-{pert} ({CONTROLOS[pert][0]})")
        CONTROLOS[pert][1](D)
    return correr(D, faltas, motor, a14)


if __name__ == "__main__":
    sys.exit(main())
