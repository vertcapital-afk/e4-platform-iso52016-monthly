# NÚMEROS DA REVISÃO R1 — Artigo 13

Resumo de estatísticas calculadas dos dados depositados do R1 (Energy & Buildings, ENB-D-26-06604; manuscrito em revisão, não aceite nem publicado). **Não é uma verificação exaustiva do manuscrito**: a verificação, com âncoras e controlos negativos, é `scripts/verificar_revisao_a13.py`.

Gerado por `figures/numeros_revisao.py` a partir de `resultados/grelha_artigo13_REVISAO.json` (DGEG2025-A, hora solar verificada) e `resultados/grelha_artigo13_2013_REVISAO.json` (REG-2013, clima tabelado). **Não editar à mão**: regenerar com `py figures\numeros_revisao.py`.

Configuração R1: α_parede 0,40 e desvão 0 **nos dois ramos**, h_ce 20,0 no ramo mensal. Δ = método mensal (ISO 52016-1) face ao sazonal (ISO 13790), em percentagem do sazonal. Necessidades em kWh/m²·a.


## 1. Efeito de método — global (n = 32 por base)

| grandeza | mediana · IQR · [mín; máx] · negativas |
|---|---|
| Δ_H DGEG2025-A | med +15.6% · IQR [+9.6; +25.9] · [-5.6; +75.5] · neg 1/32 |
| Δ_H REG-2013 | med +11.0% · IQR [+1.1; +26.5] · [-12.1; +54.1] · neg 6/32 |
| Δ_C DGEG2025-A | med +2.7% · IQR [-14.3; +45.6] · [-29.4; +181.5] · neg 16/32 |
| Δ_C REG-2013 | med +6.5% · IQR [-9.8; +33.0] · [-23.4; +164.4] · neg 12/32 |

## 2. Necessidades medianas — o denominador visível

| grandeza | mediana |
|---|---|
| N_ic sazonal (DGEG2025-A) | 69.95 |
| N_H mensal (DGEG2025-A) | 83.48 |
| N_vc sazonal (DGEG2025-A) | 10.68 |
| N_C mensal (DGEG2025-A) | 14.95 |
| N_ic sazonal (REG-2013) | 83.97 |
| N_H mensal (REG-2013) | 85.12 |
| N_vc sazonal (REG-2013) | 11.06 |
| N_C mensal (REG-2013) | 14.54 |

## 3. Unifamiliares (RB1–RB4) e multifamiliares (RB5–RB8) — medianas

| grupo | Δ_H DGEG2025-A | Δ_H REG-2013 | Δ_C DGEG2025-A | Δ_C REG-2013 |
|---|---|---|---|---|
| unifamiliares | +11.9% | +5.1% | +10.3% | +19.4% |
| multifamiliares | +20.1% | +12.4% | -3.7% | +4.0% |

## 4. Agregado ponderado pelo parque

Pesos do parque (Census) de `figures/estatisticas.py`; cidades equiponderadas em cada arquétipo. O efeito é o rácio das necessidades ponderadas, não a média dos rácios.

| base / uso | sazonal | mensal | efeito |
|---|---|---|---|
| DGEG2025-A aquecimento | 102.53 | 113.23 | **+10.4%** |
| DGEG2025-A arrefecimento | 17.40 | 17.23 | **-1.0%** |
| REG-2013 aquecimento | 106.67 | 109.65 | **+2.8%** |
| REG-2013 arrefecimento | 19.10 | 19.01 | **-0.5%** |

Média ponderada dos rácios (aquecimento), para comparação: DGEG2025-A +17.54%, REG-2013 +9.82%.


## 5. Por cidade — medianas

| cidade | Δ_H DGEG2025-A | Δ_H REG-2013 | Δ_C DGEG2025-A | Δ_C REG-2013 |
|---|---|---|---|---|
| Coimbra | +22.3% | +18.5% | +1.9% | +15.9% |
| Bragança | +12.8% | +4.3% | +78.0% | +51.4% |
| Évora | +8.7% | +7.0% | -23.2% | -17.3% |
| Lisboa | +39.1% | +24.7% | +3.2% | +4.5% |

## 6. Efeito de base (REG-2013 → DGEG2025-A), mesmo método

| grandeza | mediana | [mín; máx] |
|---|---|---|
| aquecimento, sazonal | -0.8% | [-34.6; +28.5] |
| aquecimento, mensal | +5.4% | [-27.2; +23.0] |
| arrefecimento, sazonal | +0.0% | [-25.2; +33.2] |
| arrefecimento, mensal | -9.9% | [-25.4; +56.3] |

## 7. RB6/Coimbra — os quatro cantos e o cruzamento ingénuo

| base | N_ic sazonal | N_H mensal | Δ_H |
|---|---|---|---|
| REG-2013 | 125.46 | 138.10 | +10.1% |
| DGEG2025-A | 118.17 | 137.65 | +16.5% |

Cruzamento ingénuo N_H(DGEG2025-A) / N_ic(REG-2013): +9.7% (calculado das grelhas a 3 casas; o valor de precisão completa está em `resultados/cruzamento_ingenuo_rb6_coimbra_REVISAO.json`).


## 8. Por célula — base DGEG2025-A

| RB | cidade | N_ic | N_H | N_vc | N_C | Δ_H | Δ_C |
|---|---|---|---|---|---|---|---|
| RB1 | Coimbra | 154.41 | 173.77 | 13.075 | 14.707 | +12.5% | +12.5% |
| RB2 | Coimbra | 117.19 | 124.76 | 7.822 | 10.804 | +6.5% | +38.1% |
| RB3 | Coimbra | 47.69 | 60.01 | 6.507 | 6.901 | +25.8% | +6.1% |
| RB4 | Coimbra | 28.09 | 37.05 | 5.875 | 5.640 | +31.9% | -4.0% |
| RB5 | Coimbra | 141.09 | 167.53 | 24.502 | 23.970 | +18.7% | -2.2% |
| RB6 | Coimbra | 118.17 | 137.65 | 19.425 | 20.675 | +16.5% | +6.4% |
| RB7 | Coimbra | 45.60 | 59.73 | 10.362 | 9.817 | +31.0% | -5.3% |
| RB8 | Coimbra | 22.89 | 32.40 | 8.051 | 7.342 | +41.5% | -8.8% |
| RB1 | Bragança | 309.53 | 333.63 | 9.042 | 15.885 | +7.8% | +75.7% |
| RB2 | Bragança | 239.64 | 244.69 | 4.122 | 11.603 | +2.1% | +181.5% |
| RB3 | Bragança | 112.22 | 126.16 | 3.655 | 7.482 | +12.4% | +104.7% |
| RB4 | Bragança | 71.57 | 82.35 | 3.410 | 6.018 | +15.1% | +76.5% |
| RB5 | Bragança | 285.13 | 322.69 | 16.857 | 24.784 | +13.2% | +47.0% |
| RB6 | Bragança | 242.87 | 268.04 | 10.997 | 21.654 | +10.4% | +96.9% |
| RB7 | Bragança | 106.61 | 124.99 | 5.782 | 10.385 | +17.2% | +79.6% |
| RB8 | Bragança | 59.92 | 73.18 | 4.604 | 7.607 | +22.1% | +65.2% |
| RB1 | Évora | 141.68 | 143.05 | 43.670 | 32.478 | +1.0% | -25.6% |
| RB2 | Évora | 107.47 | 101.47 | 38.109 | 26.894 | -5.6% | -29.4% |
| RB3 | Évora | 42.75 | 46.74 | 26.265 | 18.808 | +9.3% | -28.4% |
| RB4 | Évora | 25.13 | 27.98 | 20.872 | 15.794 | +11.3% | -24.3% |
| RB5 | Évora | 128.78 | 139.15 | 61.290 | 48.878 | +8.1% | -20.3% |
| RB6 | Évora | 107.73 | 113.57 | 58.450 | 45.592 | +5.4% | -22.0% |
| RB7 | Évora | 41.16 | 47.79 | 30.875 | 24.538 | +16.1% | -20.5% |
| RB8 | Évora | 20.61 | 25.05 | 22.014 | 18.689 | +21.5% | -15.1% |
| RB1 | Lisboa | 76.97 | 88.09 | 12.940 | 15.187 | +14.4% | +17.4% |
| RB2 | Lisboa | 54.35 | 60.07 | 7.804 | 11.038 | +10.5% | +41.4% |
| RB3 | Lisboa | 15.96 | 24.29 | 6.548 | 7.083 | +52.3% | +8.2% |
| RB4 | Lisboa | 8.21 | 13.11 | 5.947 | 5.818 | +59.5% | -2.2% |
| RB5 | Lisboa | 68.33 | 84.61 | 22.910 | 22.780 | +23.8% | -0.6% |
| RB6 | Lisboa | 53.22 | 67.03 | 18.200 | 19.478 | +25.9% | +7.0% |
| RB7 | Lisboa | 15.71 | 25.12 | 9.621 | 8.971 | +59.9% | -6.8% |
| RB8 | Lisboa | 6.54 | 11.48 | 7.511 | 6.622 | +75.5% | -11.8% |

## 9. Por célula — base REG-2013

| RB | cidade | N_ic | N_H | N_vc | N_C | Δ_H | Δ_C |
|---|---|---|---|---|---|---|---|
| RB1 | Coimbra | 169.56 | 177.85 | 11.675 | 15.118 | +4.9% | +29.5% |
| RB2 | Coimbra | 127.46 | 126.56 | 6.279 | 10.675 | -0.7% | +70.0% |
| RB3 | Coimbra | 47.46 | 59.30 | 5.404 | 6.583 | +24.9% | +21.8% |
| RB4 | Coimbra | 27.26 | 36.05 | 4.937 | 5.214 | +32.2% | +5.6% |
| RB5 | Coimbra | 151.32 | 169.60 | 21.489 | 23.625 | +12.1% | +9.9% |
| RB6 | Coimbra | 125.46 | 138.10 | 15.833 | 19.824 | +10.1% | +25.2% |
| RB7 | Coimbra | 45.80 | 58.67 | 8.447 | 8.863 | +28.1% | +4.9% |
| RB8 | Coimbra | 22.26 | 31.18 | 6.636 | 6.340 | +40.1% | -4.5% |
| RB1 | Bragança | 316.66 | 309.65 | 7.537 | 11.977 | -2.2% | +58.9% |
| RB2 | Bragança | 244.62 | 227.27 | 3.094 | 8.181 | -7.1% | +164.4% |
| RB3 | Bragança | 111.92 | 117.87 | 2.865 | 4.952 | +5.3% | +72.8% |
| RB4 | Bragança | 70.75 | 76.99 | 2.746 | 3.850 | +8.8% | +40.2% |
| RB5 | Bragança | 288.75 | 298.31 | 14.572 | 19.067 | +3.3% | +30.8% |
| RB6 | Bragança | 245.70 | 247.87 | 8.747 | 15.725 | +0.9% | +79.8% |
| RB7 | Bragança | 106.18 | 115.48 | 4.797 | 6.904 | +8.8% | +43.9% |
| RB8 | Bragança | 59.00 | 67.51 | 3.949 | 4.890 | +14.4% | +23.8% |
| RB1 | Évora | 134.28 | 125.12 | 53.394 | 43.521 | -6.8% | -18.5% |
| RB2 | Évora | 99.92 | 87.82 | 46.332 | 35.500 | -12.1% | -23.4% |
| RB3 | Évora | 35.16 | 39.40 | 31.443 | 24.536 | +12.1% | -22.0% |
| RB4 | Évora | 19.73 | 23.08 | 24.704 | 20.097 | +17.0% | -18.6% |
| RB5 | Évora | 118.92 | 121.14 | 70.250 | 60.936 | +1.9% | -13.3% |
| RB6 | Évora | 97.56 | 98.13 | 66.352 | 55.661 | +0.6% | -16.1% |
| RB7 | Évora | 34.06 | 40.10 | 35.482 | 30.119 | +17.7% | -15.1% |
| RB8 | Évora | 16.04 | 20.38 | 25.244 | 22.523 | +27.0% | -10.8% |
| RB1 | Lisboa | 105.19 | 108.09 | 16.125 | 18.876 | +2.8% | +17.1% |
| RB2 | Lisboa | 75.93 | 74.82 | 10.439 | 13.953 | -1.5% | +33.7% |
| RB3 | Lisboa | 23.36 | 31.91 | 8.491 | 8.991 | +36.6% | +5.9% |
| RB4 | Lisboa | 12.44 | 18.00 | 7.484 | 7.362 | +44.7% | -1.6% |
| RB5 | Lisboa | 92.01 | 102.97 | 28.227 | 29.085 | +11.9% | +3.0% |
| RB6 | Lisboa | 73.09 | 82.41 | 23.465 | 25.130 | +12.8% | +7.1% |
| RB7 | Lisboa | 22.86 | 32.06 | 12.402 | 11.884 | +40.3% | -4.2% |
| RB8 | Lisboa | 10.00 | 15.42 | 9.457 | 8.810 | +54.1% | -6.8% |

## 10. Denominadores pequenos — absolutos ao lado

As cinco células de menor N_vc sazonal na base DGEG2025-A, onde as percentagens enganam:

| cidade | RB | N_vc sazonal | N_C mensal | Δ absoluto | Δ % |
|---|---|---|---|---|---|
| Bragança | RB4 | 3.41 | 6.02 | +2.61 | +76.5% |
| Bragança | RB3 | 3.65 | 7.48 | +3.83 | +104.7% |
| Bragança | RB2 | 4.12 | 11.60 | +7.48 | +181.5% |
| Bragança | RB8 | 4.60 | 7.61 | +3.00 | +65.2% |
| Bragança | RB7 | 5.78 | 10.38 | +4.60 | +79.6% |
