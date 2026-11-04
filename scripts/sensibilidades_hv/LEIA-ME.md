# A13 R1 — sensibilidades em hora solar verificada

Revisão R1 do Artigo 13 (Energy & Buildings, ENB-D-26-06604; manuscrito em revisão, não aceite nem publicado).

## O que está depositado

Os resultados das sensibilidades do R1 estão em `resultados/`, com os mesmos nomes da versão pública anterior:

| Ficheiro | Experiência | Avaliações |
|---|---|---|
| `sensibilidade_eq97_REVISAO.json` | corte da Eq. (97) da ISO 52016-1 (γ_H > 2,0) | 64 (32 por base) |
| `sensibilidade_sombreamento_REVISAO.json` | sem sombreamento móvel de Verão | 64 |
| `sensibilidade_hgr22_REVISAO.json` | H_gr ± 22 % | 32 (16 células unifamiliares × 2 bases) |
| `isolamento_solo_artigo13_REVISAO.json` | termo de solo da ISO 13370 contra b_tr = 0,8 no eixo mensal | 16 células × 2 bases |
| `sensibilidade_alfa060_A13.json` e `decomposicao_artigo13_alfa060.json` | α_parede = 0,60 nos dois ramos | 32 × 2 bases; 32 anatomias |
| `sensibilidade_gsul_janela_HV.json` | janela do G_sul de referência (eixo sazonal) | 32 células × 4 janelas = 128 |

Na base DGEG2025-A, todos foram calculados com a irradiância do EPW lida em **hora solar verificada**. A REG-2013 usa o clima tabelado e não depende da base de tempo. As versões em hora de cabeçalho destes ficheiros ficam na tag `public-before-R1-ENB-D-26-06604`.

## Método

- `hv_patch.py` substitui só `run_grelha_artigo13._ler_epw_cidade` pela leitura `ler_epw_com_hora(..., "verificada")`. A cadeia de irradiância, horas e temperaturas é a mesma.
- **Regressão:** as 32 células DGEG2025-A reproduzem `resultados/fontes_HV/RESULTADO_A13_COMPLETO.json` a 1e-9.
- **Controlo negativo:** com o leitor de cabeçalho, nenhuma das 32 células reproduz.
- Os produtores das quatro primeiras experiências pertencem ao motor (`src/e4/sensibilidade_eq97_REVISAO.py`, `sensibilidade_sombreamento_REVISAO.py`, `sensibilidade_hgr22_REVISAO.py`, `isolamento_solo_artigo13_REVISAO.py`) e não estão neste depósito. Correram numa cópia de trabalho do motor, com `run_hv.py`. Nessa cópia, a referência interna de cada produtor (`grelha_artigo13_REVISAO.json`) foi substituída pela grelha em hora verificada, para que a regressão de cada script conferisse contra a mesma base.
- Os produtores da α = 0,60 e do G_sul estão depositados: `scripts/sensibilidade_alfa060_A13.py` e `scripts/sensibilidade_gsul_janela_HV.py`.

## Resultados (hora verificada, recontados nos ficheiros depositados)

`scripts/verificar_revisao_a13.py` reconfere estes números (V3, V6 e V7).

| Experiência | Resultado | No manuscrito |
|---|---|---|
| Eq. (97) | Toca 55 das 64 avaliações mensais (87 meses), e 49 células mudam a 0,01 pp. Deslocamento mediano −0,52 pp (DGEG2025-A) e −0,01 pp (REG-2013), no máximo −2,6 e −4,0. Medianas de +15,6 % para +15,0 % e de +11,0 % para +10,6 %. Nenhuma célula muda de sinal. | §2.4 |
| Sombreamento | Sem protecção, N_vc × 1,89 (1,25 a 3,46) e γ_C × 1,28 | Tabela 2 |
| H_gr ± 22 % | Deslocamento mediano 0,84 pp, máximo 1,95 pp. Uma mudança de sinal: REG-2013, RB2/Coimbra, com divergência de base −0,7 % | §4.4, Tabela 2 |
| Isolamento do solo | Desvio para o positivo, com mediana de 2,2 pp (1,0 a 4,5) na DGEG2025-A e de 2,1 pp (0,9 a 4,0) na REG-2013. Mesma direcção nas 32 avaliações | §3.3 |
| α = 0,60 | Mediana do efeito de método no aquecimento: +18,70 % (DGEG2025-A) e +12,95 % (REG-2013). Medianas do arrefecimento a menos de 2 pp das de α = 0,40. Nenhuma célula com γ_C < 1 diverge para baixo. Classificação pelo γ_C: 26/32 (30/32 a α = 0,40) | §4.4, Tabela 2 |
| G_sul (Coimbra) | Out–Abr (produção) 96,54, Nov–Mar 92,20, Out–Mar 96,09, Nov–Abr 93,37 kWh/m²·mês. Com Nov–Mar, N_ic varia entre −3,23 % e +4,42 % (mediana 0,00 %). Sobe em Coimbra e Bragança e desce em Évora e Lisboa | §3.3, §4.4, Tabela 2 |

Ficam como diagnósticos históricos, declarados no texto e não revalidados em hora verificada:
- o exemplo +86,8 % contra +1,9 % (quebra de paridade, na convenção de tempo da versão submetida);
- o exemplo da altitude (+21 % contra +8,2 %, numa iteração anterior).

## Reproduzir (precisa do motor do autor, disponível a pedido)

1. Fazer uma **cópia de trabalho**, nunca o repositório do motor, porque os produtores gravam os resultados ao lado de si. `hv_patch.py` recusa uma pasta com `.git`. A cópia fica assim:
   ```
   PASTA/src/e4/...
   PASTA/studies/a13_iso52016_mensal/...
   PASTA/hv_patch.py e PASTA/run_hv.py           (desta pasta)
   PASTA/RESULTADO_A13_COMPLETO.json             (de resultados/fontes_HV/)
   ```
2. Dentro de `PASTA`, correr `py hv_patch.py`. Espera-se `regressao HV: 32/32 celulas a 1e-9` e `CN (cabecalho deve falhar): detectado`.
3. Correr cada produtor com `py run_hv.py src/e4/<produtor>.py`. O isolamento do solo precisa também de `PYTHONPATH=src/e4`.

A α = 0,60 e o G_sul não precisam desta cópia manual:
- `scripts/sensibilidade_alfa060_A13.py --motor ... --saida ...` lê o motor sem lhe escrever.
- `scripts/sensibilidade_gsul_janela_HV.py --motor ... --saida ...` faz a sua própria cópia de trabalho dentro de `--saida`.
