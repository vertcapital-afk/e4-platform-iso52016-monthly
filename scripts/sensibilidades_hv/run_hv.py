# -*- coding: utf-8 -*-
"""
run_hv.py — corre um produtor do motor do autor com a leitura do EPW em hora
solar verificada (hv_patch.py). Artigo 13, revisão R1.

Uso, dentro da CÓPIA de trabalho descrita em hv_patch.py e LEIA-ME.md:
    py run_hv.py src/e4/sensibilidade_eq97_REVISAO.py
O isolamento do solo precisa também de PYTHONPATH=src/e4.

Os produtores pertencem ao motor (pacote privado, disponível a pedido) e gravam
os resultados ao lado de si: por isso só numa cópia. Este ficheiro, sozinho, não
reproduz nenhuma experiência num clone do depósito. Lógica igual à usada em
03/11/2026; no depósito acrescentaram-se este cabeçalho e a mensagem de uso.
"""
import sys, runpy, time
if len(sys.argv) < 2:
    print("Uso: py run_hv.py CAMINHO/DO/PRODUTOR.py   (dentro da cópia de trabalho; ver LEIA-ME.md)")
    raise SystemExit(2)
import hv_patch  # aplica a leitura em hora verificada
t=time.time()
runpy.run_path(sys.argv[1], run_name="__main__")
print(f"[run_hv] {sys.argv[1]} em {time.time()-t:.0f}s")
