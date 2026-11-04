# -*- coding: utf-8 -*-
"""preparar_figuras_r1.py — A13 R1: deriva das fontes de precisão completa os três JSON
que as figuras e as estatísticas lêem, em hora solar verificada.

Entradas: resultados/fontes_HV/RESULTADO_A13_COMPLETO.json e
          resultados/fontes_HV/INTERMEDIARIOS_A13_COMPLETO.json
Saídas:   resultados/grelha_artigo13_REVISAO.json        (DGEG2025-A, hora verificada, 3 casas)
          resultados/grelha_artigo13_2013_REVISAO.json   (REG-2013, clima tabelado, 3 casas)
          resultados/decomposicao_artigo13_REVISAO.json  (anatomias em hora verificada)

Não corre nenhum motor: só arredonda e reorganiza os dados de precisão completa.
Por omissão só CONFERE: deriva em memória e compara com os ficheiros depositados
(código 0 se iguais, 1 se não). Com --escrever, grava as três saídas.

Uso (Windows: «py»):  py scripts\\preparar_figuras_r1.py [--escrever]
Depois, para as figuras: ver o README (três produtores com --revisao e
scripts/numerar_figuras_r1.py).

Adaptado de revisao/preparar_figuras_r1.py do repositório do autor (03/11/2026).
No depósito: caminhos relativos à raiz do depósito; modo de conferência por
omissão; já não copia os produtores de figuras nem escreve a origem, que está
registada em resultados/ORIGEM_R1.json.
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ / "resultados" / "fontes_HV"
RES = RAIZ / "resultados"


def derivar():
    f = json.loads((BASE / "RESULTADO_A13_COMPLETO.json").read_text("utf-8"))
    i = json.loads((BASE / "INTERMEDIARIOS_A13_COMPLETO.json").read_text("utf-8"))
    rows = [dict(rb=c["rb"], cidade=c["cidade"], **{k: round(v, 3) for k, v in c["necessidades"]["verificada"].items()}) for c in f["celulas"]]
    reg = [dict(rb=c["rb"], cidade=c["cidade"], **{k: round(v, 3) for k, v in c["controlo_REG2013"].items()}) for c in f["celulas"]]
    dec = [c["anatomia"] for c in i["celulas"] if c["hora"] == "verificada"]
    assert len(rows) == 32 and len(reg) == 32 and len(dec) == 32, (len(rows), len(reg), len(dec))
    meta = {"hora": "verificada", "origem": "corridas do Sol de 30/10 (tema 1); nao e corrida nova"}
    return {name: {"meta": meta, "celulas": data} for name, data in
            [("grelha_artigo13_REVISAO", rows), ("grelha_artigo13_2013_REVISAO", reg),
             ("decomposicao_artigo13_REVISAO", dec)]}


def main(argv=None):
    escrever = "--escrever" in (sys.argv[1:] if argv is None else argv)
    saidas = derivar()
    if escrever:
        for name, doc in saidas.items():
            (RES / (name + ".json")).write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", "utf-8")
        print("Gravado: 32 células DGEG em hora verificada, 32 REG, 32 anatomias em", RES)
        return 0
    difs = []
    for name, doc in saidas.items():
        p = RES / (name + ".json")
        dep = json.loads(p.read_text("utf-8")) if p.exists() else None
        ok = dep == doc
        print(f"  [{'IGUAL' if ok else 'DIFERENTE'}] resultados/{name}.json")
        if not ok:
            difs.append(name)
    print("Conferência:", "os três ficheiros depositados são a derivação das fontes" if not difs
          else f"{len(difs)} diferente(s): {difs}")
    return 1 if difs else 0


if __name__ == "__main__":
    sys.exit(main())
