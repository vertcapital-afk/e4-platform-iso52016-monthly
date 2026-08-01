# -*- coding: utf-8 -*-
"""
Verificacao Artigo 13 (kernel ISO 52016-1 mensal) — Windows-friendly.

Uso (a partir de C:\\e4-platform\\motor):
    py verificar_artigo13.py

PROPOSITO: correr SEMPRE depois de sincronizar ficheiros de uma sessao para
o repositorio. Deteta em segundos a classe de falha de 10-11/07/2026
(consumidores novos + fornecedor antigo): verifica se cada modulo tem as
funcoes que os outros esperam, se as fixtures existem, e se as ancoras
numericas validadas se mantem. Qualquer FALHA identifica o ficheiro
desatualizado pelo nome.

Nao substitui a suite (py -m pytest tests\\) — e o triagem rapido pos-sync.
"""
import os
import sys

# Caminhos relativos à RAIZ DO REPOSITÓRIO (reorganização de 28/07/2026).
# Antes: RAIZ = pasta do script, + "e4". Hoje o pacote é src/e4 e o script
# vive em studies/a13_iso52016_mensal/ — era esta a causa das 19 falhas.
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "src", "e4"))   # imports directos
sys.path.insert(0, os.path.join(RAIZ, "src"))         # import e4.*
sys.path.insert(0, AQUI)                              # run_grelha_artigo13

FALHAS = []


N_OK = 0


def check(nome, ok, detalhe=""):
    estado = "OK   " if ok else "FALHA"
    print("  [{}] {}{}".format(estado, nome, (" — " + detalhe) if detalhe else ""))
    global N_OK
    if ok:
        N_OK += 1
    else:
        FALHAS.append(nome)


print("=" * 64)
print("1) Interfaces entre modulos (a falha de 10-11/07 era aqui)")
print("=" * 64)

try:
    import clima_epw
    for fn in ("ler_epw", "ler_location_epw", "theta_ext_media_mensal",
               "theta_ext_anual_media", "dia_do_ano",
               "posicao_e_irradiancia_hora",
               "irradiancia_mensal_por_orientacao"):
        check("clima_epw.{}".format(fn), hasattr(clima_epw, fn),
              "" if hasattr(clima_epw, fn) else
              "clima_epw.py DESATUALIZADO — copiar a versao da sessao")
except Exception as e:
    check("import clima_epw", False, repr(e))

try:
    import iso52016_mensal
    for fn in ("EntradaMensal", "ElementoEnvolvente", "Q_sol_liquido_mensal",
               "calcular_mes_aquecimento", "calcular_mes_arrefecimento"):
        check("iso52016_mensal.{}".format(fn), hasattr(iso52016_mensal, fn))
except Exception as e:
    check("import iso52016_mensal", False, repr(e))

try:
    from pontes import h_ptl
    check("pontes.h_ptl", True)
except Exception as e:
    check("pontes.h_ptl", False, repr(e))

print()
print("=" * 64)
print("2) Fixtures no lugar (tests/fixtures/...)")
print("=" * 64)

FIX = os.path.join(RAIZ, "tests", "fixtures")
for rel in (
    "fixtures_democalc_52016_mensal_v300.json",
    "fixtures_democalc_52016_mensal_athens_soff.json",
    "fixtures_democalc_52016_mensal_bestest940_drycold.json",
    "fixtures_democalc_52016_mensal_bestest600_drycold.json",
    os.path.join("solar", "drycold_denver_iso52010_oficial.csv"),
    os.path.join("clima", "Coimbra_255m.epw"),
    os.path.join("clima", "Bragan\u00e7a_907m.epw"),
    os.path.join("clima", "\u00c9vora_296m.epw"),
    os.path.join("clima", "Lisboa_114m.epw"),
):
    check(rel, os.path.exists(os.path.join(FIX, rel)))

# Os pilotos leem e4/fixtures/clima — symlink ou copia de tests/fixtures/clima
clima_pilotos = os.path.join(RAIZ, "src", "e4", "fixtures", "clima", "Coimbra_255m.epw")
check("e4/fixtures/clima (pilotos)", os.path.exists(clima_pilotos),
      "" if os.path.exists(clima_pilotos) else
      "criar symlink/copia de tests/fixtures/clima para e4/fixtures/clima")

print()
print("=" * 64)
print("3) Ancoras numericas (validadas 10-11/07/2026)")
print("=" * 64)

try:
    ptl = h_ptl(familia="MFH", area_util=70.0, n_pisos=1, pe_direito=2.6,
                vaos_por_orientacao={"N": 7.7, "S": 7.7, "W": 7.7},
                referencia=False)
    check("h_ptl(RB6) = 47,73 W/K", abs(ptl - 47.7293) < 0.001,
          "obtido {:.4f}".format(ptl))
except Exception as e:
    check("h_ptl(RB6)", False, repr(e))

try:
    import math
    import csv
    caminho = os.path.join(FIX, "solar", "drycold_denver_iso52010_oficial.csv")
    if os.path.exists(caminho):
        # Amostra do oraculo Denver: 200 primeiras horas com sol, superficie
        # s1 (az=+90, tilt=90) — erro mediano deve ser ~0 (bins de Perez a
        # parte, dai a mediana e nao o maximo).
        erros = []
        with open(caminho, encoding="utf-8") as f:
            for ln in csv.DictReader(f):
                g_dir, g_dif = float(ln["G_dir"]), float(ln["G_dif"])
                if g_dir + g_dif < 0.1:
                    continue
                _, idir, idif = clima_epw.posicao_e_irradiancia_hora(
                    math.radians(39.76), math.radians(-104.86), -7.0, 0.5,
                    math.radians(90.0), math.radians(90.0),
                    float(ln["n_hour"]), int(ln["n_day"]), g_dir, g_dif, 0.2)
                erros.append(abs(idir + idif - float(ln["I_tot_s1"])))
                if len(erros) >= 200:
                    break
        erros.sort()
        mediana = erros[len(erros) // 2]
        # Limiar de TRIAGEM: um erro de transcricao das equacoes daria
        # dezenas de W/m2; o residuo Excel-vs-double e ~0,02. A validacao
        # fina (mediana anual = 0 exato) esta em tests/test_clima_epw_solar.py.
        check("oraculo Denver (amostra, triagem)", mediana < 1.0,
              "mediana {:.4f} W/m2".format(mediana))
    else:
        check("oraculo Denver", False, "fixture em falta (ver seccao 2)")
except Exception as e:
    check("oraculo Denver", False, repr(e))

try:
    # Ancora de regressao do projeto: irradiancia mensal de Coimbra —
    # coerencia fisica minima (Sul domina verticais em Janeiro), a ligacao
    # completa aos N_H/N_C do Handoff 04/05 fica para os pilotos/pytest.
    cam = os.path.join(FIX, "clima", "Coimbra_255m.epw")
    regs = clima_epw.ler_epw(cam)
    loc = clima_epw.ler_location_epw(cam)
    irr = clima_epw.irradiancia_mensal_por_orientacao(regs, loc)
    jan = irr[1]
    check("Coimbra: SV domina verticais em Janeiro",
          jan["SV"] > max(jan["EV"], jan["WV"], jan["NV"]),
          "SV={:.1f} EV={:.1f} WV={:.1f} NV={:.1f} kWh/m2".format(
              jan["SV"], jan["EV"], jan["WV"], jan["NV"]))
except Exception as e:
    check("irradiancia Coimbra", False, repr(e))

print()
print("=" * 64)
print("4) Cobertura do fatorial (comparacao_rb6_metodos_v2 / grelha)")
print("=" * 64)

try:
    sys.path.insert(0, RAIZ)
    from e4 import comparacao_rb6_metodos_v2 as c2
    for fn in ("construir_dgeg2025_a", "correr"):
        check("comparacao_rb6_metodos_v2.{}".format(fn), hasattr(c2, fn))
except Exception as e:
    check("import comparacao_rb6_metodos_v2", False, repr(e))

try:
    import run_grelha_artigo13 as grelha
    for fn in ("celula_13790", "celula_52016", "validar_rb6_coimbra", "correr_grelha"):
        check("run_grelha_artigo13.{}".format(fn), hasattr(grelha, fn))
    ok = grelha.validar_rb6_coimbra()
    check("grelha: RB6/Coimbra reproduz o Handoff 07 §2", ok,
          "" if ok else "ver print acima — nao correr a grelha completa")
except Exception as e:
    check("run_grelha_artigo13", False, repr(e))

print()
print("=" * 64)
print("5) PARIDADE DE ENVOLVENTE entre os dois ramos (invariante do artigo)")
print("=" * 64)
# O Artigo 13 afirma isolar o efeito de METODO. Isso so e verdade se a
# envolvente for identica nos dois ramos. A absortancia solar dos opacos e
# o desvao da cobertura vivem em SITIOS DIFERENTES para cada ramo:
#   ramo 52016  -> run_grelha_artigo13.A_SOL_PAREDE / .R_DESVAO_COB
#   ramo 13790  -> e4.solar.ALFA_PAREDE / e4.geometria.R_DESVAO_COB
# Corrigir um sem o outro produz um "efeito de metodo" que e, na verdade,
# uma quebra de paridade -- exactamente o confundimento que o artigo denuncia.
try:
    import run_grelha_artigo13 as _g13
    from e4 import solar as _sol, geometria as _geo
    check("alfa_parede em paridade (52016 == 13790)",
          abs(_g13.A_SOL_PAREDE - _sol.ALFA_PAREDE) < 1e-12,
          "52016={} 13790={}".format(_g13.A_SOL_PAREDE, _sol.ALFA_PAREDE))
    check("alfa_cobertura em paridade (52016 == 13790)",
          abs(_g13.A_SOL_COBERTURA - _sol.ALFA_COBERTURA) < 1e-12,
          "52016={} 13790={}".format(_g13.A_SOL_COBERTURA, _sol.ALFA_COBERTURA))
    check("desvao da cobertura em paridade (52016 == 13790)",
          abs(_g13.R_DESVAO_COB - _geo.R_DESVAO_COB) < 1e-12,
          "52016={} 13790={}".format(_g13.R_DESVAO_COB, _geo.R_DESVAO_COB))
except Exception as e:
    check("paridade de envolvente verificavel", False, repr(e))


try:
    from iso13370_solo import uf_sog
    # Oraculo DemoCalc Strasbourg (Input_GrFl/Calc_GrFl) -- [P-hgr-sfh]
    u = uf_sog(area=91.8, perimetro=38.0, rf=5.2181095842, w=0.35, lam=2.0, rse=0.04)
    check("iso13370_solo.uf_sog(Strasbourg) = 0,15297 W/m2.K",
          abs(u - 0.1529724371) < 1e-6, "obtido {:.7f}".format(u))
except Exception as e:
    check("iso13370_solo.uf_sog", False, repr(e))

print()
print("=" * 64)
if FALHAS:
    print("RESULTADO: {} FALHA(S) — ficheiros a sincronizar: ver acima.".format(len(FALHAS)))
    sys.exit(1)
print("RESULTADO: {}/{} PASS — tudo OK. Confirmar com: py -m pytest tests\\"
      .format(N_OK, N_OK))
print("Ancoras completas dos pilotos (Handoff 05 seccao 3):")
print("  py e4\\piloto_rb6_v2.py  -> Coimbra 122,79/11,70 (sem PTL)")
print("  py e4\\piloto_rb6_v3.py  -> Coimbra 143,56/10,93 (com PTL, Htr=403,15)")
