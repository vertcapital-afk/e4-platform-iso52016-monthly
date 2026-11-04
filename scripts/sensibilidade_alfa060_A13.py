# -*- coding: utf-8 -*-
"""
sensibilidade_alfa060_A13.py — sensibilidade α_parede = 0,60 do Artigo 13,
revisão R1 (§4.4 e Tabela 2 do manuscrito).

⚠️ Precisa do motor do autor (pacote privado, disponível a pedido). Num clone
limpo deste depósito não corre: sai com o código 2. Os resultados depositados
(resultados/sensibilidade_alfa060_A13.json e
resultados/decomposicao_artigo13_alfa060.json) verificam-se sem motor com
scripts/verificar_revisao_a13.py (V6).

Origem (S1 da auditoria de 01/08/2026): o A14 declara sensibilidade a
α_parede = 0,60; o A13 só declarava 0,40, e é no A13 que o α mais mexe (a
segmentação por γ_C muda de lado por causa dele). Grelha de 32 células × 2
bases com 0,60/0,50 NOS DOIS RAMOS (mesma sobreposição em runtime, com
try/finally, do revisao_a13_producao.py), mais a segmentação γ_C sob 0,60
(e4.decomposicao_artigo13, do motor).

R1 (04/11/2026), diferenças face à versão publicada com a submissão:
    · leitura do EPW em hora solar verificada, explícita (a mesma função do
      revisao_a13_producao.py);
    · a asserção contra a grelha da versão JBE (em hora de cabeçalho, fora deste
      depósito) é substituída por duas regressões: α = 0,40 contra
      resultados/fontes_HV/ e α = 0,60 contra os ficheiros depositados;
    · escreve só em --saida.

Uso (Windows: «py»):
    py scripts\\sensibilidade_alfa060_A13.py --motor C:\\motor --saida C:\\pasta_nova
    py scripts\\sensibilidade_alfa060_A13.py --motor C:\\motor --celula RB6 Coimbra
        uma célula: α = 0,60 nas duas bases e a anatomia, contra os ficheiros
        depositados; não grava nada.

Código de saída: 0 regressões reproduzidas; 1 alguma falhou (nada se grava);
2 motor, argumentos ou pasta de saída inválidos.
"""
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import revisao_a13_producao as p   # noqa: E402  (motor, leitor HV, sobreposição, regressão)

CFG60 = dict(alfa_parede=0.60, desvao_cob=0.0, h_ce=20.0)
RES = os.path.join(p.DEPOSITO, "resultados")


def _ler(nome):
    with open(os.path.join(RES, nome), encoding="utf-8") as f:
        return json.load(f)


def _iguais(calc, dep, campos, arred):
    """Diferenças entre o calculado e o depositado (3 casas, exacto)."""
    ref = {(c["rb"], c["cidade"]): c for c in dep}
    difs = []
    for c in calc:
        r = ref[(c["rb"], c["cidade"])]
        for k in campos:
            x = round(c[k], 3) if arred else c[k]
            if x != r[k]:
                difs.append(f"{c['rb']}/{c['cidade']} {k}: {x} vs depositado {r[k]}")
    return difs


def anatomia(M, cfg, hora, celula=None):
    """Segmentação γ_C (e4.decomposicao_artigo13) com a configuração e o leitor."""
    import e4.decomposicao_artigo13 as d
    g = M["g"]
    antes = p._aplicar(M, cfg)
    g._ler_epw_cidade = p.leitor(M, hora)
    try:
        if celula:
            return [d.anatomia(celula[0], celula[1], "DGEG2025-A")]
        return d.correr("DGEG2025-A")
    finally:
        p._repor(M, antes)


def main(argv=None):
    a = p.argumentos(argv, "Sensibilidade α = 0,60 do A13 R1 (precisa do motor do autor).")
    M = p.carregar_motor(a.motor)
    if a.saida:
        erro = p.pasta_saida_valida(a.saida, M)
        if erro:
            print("⛔", erro)
            return 2
    cel = tuple(a.celula) if a.celula else None
    print(f"motor: {M['raiz']} · hora: {a.hora}")

    # 1) α = 0,40 tem de reproduzir a fonte HV (é a linha de base da comparação)
    a40, b40 = p.corrida(M, p.REVISAO, a.hora, cel)
    n, difs = p.regressao(a40, b40, a.hora, completa=not cel)
    if difs:
        print(f"⛔ REGRESSÃO α=0,40: {len(difs)}/{n} valores diferem da fonte HV. Nada gravado.")
        for x in difs[:10]:
            print("   ", x)
        return 1
    print(f"[OK] regressão α=0,40: {n}/{n} valores iguais à fonte HV")

    # 2) α = 0,60 tem de reproduzir o que está depositado
    a60, b60 = p.corrida(M, CFG60, a.hora, cel)
    dec60 = anatomia(M, CFG60, a.hora, cel)
    dep = _ler("sensibilidade_alfa060_A13.json")
    difs = _iguais(a60, dep["dgeg2025a"], p.CAMPOS, arred=bool(cel)) + \
        _iguais(b60, dep["reg2013"], p.CAMPOS_2013, arred=bool(cel))
    dep_dec = _ler("decomposicao_artigo13_alfa060.json")["celulas"]
    ref_dec = {(c["rb"], c["cidade"]): c for c in dep_dec}
    difs += [f"anatomia {c['rb']}/{c['cidade']}" for c in dec60 if c != ref_dec[(c["rb"], c["cidade"])]]
    if a.hora == "verificada" and difs:
        print(f"⛔ REGRESSÃO α=0,60: {len(difs)} diferenças face aos ficheiros depositados. Nada gravado.")
        for x in difs[:10]:
            print("   ", x)
        return 1
    if a.hora == "verificada":
        print(f"[OK] regressão α=0,60: {len(a60) + len(b60)} células e {len(dec60)} anatomias "
              f"iguais às depositadas")
    else:
        print(f"[INFO] hora {a.hora}: os ficheiros depositados são em hora verificada; "
              f"{len(difs)} diferenças, como esperado")

    gte1 = [c for c in dec60 if c["gamma_C_sazonal"] >= 1]
    lt1 = [c for c in dec60 if c["gamma_C_sazonal"] < 1]
    bem = sum(1 for c in gte1 if c["dC"] < 0) + sum(1 for c in lt1 if c["dC"] > 0)
    print(f"segmentação γ_C sob α=0,60 (DGEG2025-A): γ_C≥1 n={len(gte1)}, γ_C<1 n={len(lt1)}; "
          f"bem classificadas {bem}/{len(dec60)}")
    if cel:
        return 0

    print("\nEFEITO DE MÉTODO — 32 células por base")
    print(f"{'base / α':24s}{'ΔH med':>9s}{'neg':>5s}{'ΔC med':>10s}{'neg':>5s}{'ΔH pond':>10s}{'ΔC pond':>10s}")
    for base, dados, sfx in (("DGEG2025-A", (a40, a60), ""), ("REG-2013", (b40, b60), "_2013")):
        for tag, cs in (("α=0,40", dados[0]), ("α=0,60", dados[1])):
            mh, nh, mc, nc, ph, pc = p.quadro(cs, sfx, M["peso"])
            print(f"{base + ' ' + tag:24s}{mh:+8.2f}%{nh:5d}{mc:+9.2f}%{nc:5d}{ph:+9.2f}%{pc:+9.2f}%")

    os.makedirs(a.saida, exist_ok=True)
    meta = {"experiencia": "sensibilidade alfa=0,60 -- fecha a assimetria com o A14 (S1)",
            "config": dict(CFG60), "paridade": "aplicada NOS DOIS RAMOS", "hora": a.hora,
            "origem": "scripts/sensibilidade_alfa060_A13.py do depósito R1, com o motor do autor"}
    with open(os.path.join(a.saida, "sensibilidade_alfa060_A13.json"), "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "dgeg2025a": a60, "reg2013": b60}, f, ensure_ascii=False, indent=1)
    with open(os.path.join(a.saida, "decomposicao_artigo13_alfa060.json"), "w", encoding="utf-8") as f:
        json.dump({"meta": {"config": "alfa=0,60", "hora": a.hora}, "celulas": dec60}, f,
                  ensure_ascii=False, indent=1)
    print(f"\nGravado em {a.saida}: sensibilidade_alfa060_A13.json e decomposicao_artigo13_alfa060.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
