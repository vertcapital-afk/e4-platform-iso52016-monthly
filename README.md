# e4-platform ISO 52016-1 monthly — Method Effect Assessment

This repository contains the complete factorial results, climate and
reference-building parameterisation, verification fixtures and evaluation
scripts supporting the study *"Separating the Method Effect from
Comparison-Protocol Confounds in the Migration from ISO 13790 to ISO 52016-1"*
(Tadeu, submitted to *Building and Environment*, 2026), a 64-cell factorial over
two calculation methods, two climate bases, eight Census-weighted Portuguese
reference buildings and four cities.

## What is here

```
resultados/     complete factorial results (64 evaluations) and all
                sensitivity experiments reported in the article
scripts/        production and verification scripts
figures/        figure-generation and statistics scripts
```

### Core results

| File | Contents |
|---|---|
| `grelha_artigo13_REVISAO.json` | 32 cells, DGEG2025-A climate base (Supplementary Table S1) |
| `grelha_artigo13_2013_REVISAO.json` | 32 cells, REG-2013 climate base (Supplementary Table S2) |
| `decomposicao_artigo13_REVISAO.json` | anatomical decomposition of §3.7: inferred season, inertia parameter α, gain-utilisation factors, sky-radiation share, γ_C |
| `NUMEROS_revisao_A13.md` | every statistic cited in the article, tabulated |

### Isolation experiments and sensitivities

| File | Article section |
|---|---|
| `isolamento_solo_artigo13_REVISAO.json` | §3.5, §4.5 — ground-coupling term isolated (b_tr = 0.8 substitution) |
| `sensibilidade_eq97_REVISAO.json` | §2.8 — ISO 52016-1 Eq. (97) cutoff |
| `sensibilidade_sombreamento_REVISAO.json` | §2.4 — summer movable shading |
| `sensibilidade_hgr22_REVISAO.json` | §4.7 — ±22% on the ground heat-transfer coefficient |
| `sensibilidade_alfa060_A13.json`, `decomposicao_artigo13_alfa060.json` | §4.7 — opaque solar absorptance at α = 0.60 |
| `cruzamento_ingenuo_rb6_coimbra_REVISAO.json` | §3.3, §4.2 — naive cross-comparison |

## Reproducing the article

Two verification scripts reproduce every number cited:

```
python verificar_artigo13.py       # 37/37 checks — production path and envelope parity
python verificar_revisao_a13.py    #  9/9 checks — statistics cited in §3.3, §3.8, §4.7
```

`verificar_artigo13.py` includes the **envelope-parity guard** described in §2.5:
it fails if opaque solar absorptance, roof resistance or external surface
coefficients are changed on one calculation axis without the other. This is the
automated check referred to in the article; correcting such a parameter on a
single axis would produce an apparent cooling method effect of +86.8% against a
measured +1.9% (§4.2).

## Calculation engine

The calculation engine itself (e4, Python), including the ISO 52016-1 monthly
kernel, the ISO 52010-1 solar transposition chain and the EN ISO 13370
ground-coupling module, is proprietary and is not included here. It is available
from the author on reasonable request.

## Verification oracles

The monthly kernel was verified against four reference cases distributed by the
EPB Center (a single-family dwelling in Strasbourg, a small office in Athens, and
BESTEST cases 600 and 940). Those reference cases are distributed under a
CC BY-NC-ND 4.0 licence and are **not redistributed here**; the fixtures in this
repository record only the derived quantities needed to reproduce the
verification, not the source workbooks.

## Climate data

The DGEG2025-A base derives from the national climate panel (SCE.CLIMA v2.3).
Production data correspond to the "replica" behaviour of the distributed
workbook, which contains the index-alignment defect documented in §2.9 of the
article; both modes are characterised there. The REG-2013 base is reconstructed
from the 2016 reference-meteorological-years tool, as described in §4.4.

## Related work

The hourly method of ISO 52016-1, applied to the same reference-building
portfolio under future climate scenarios, is the subject of a companion study in
preparation. Both studies share the same reference-building parameterisation and
the same envelope conventions; the monthly results here are directly comparable
with the monthly arm of that work.

The prospective techno-economic assessment of HVAC+PV system sets under future
climate and grid decarbonisation scenarios is available at
[`e4-platform-technoeconomic`](https://github.com/vertcapital-afk/e4-platform-technoeconomic).

## Licence

Scripts: MIT (see `LICENSE`).
Data: CC BY 4.0 (see `LICENSE-DATA`).

## Citation

Tadeu, S. F. (2026). *Separating the Method Effect from Comparison-Protocol
Confounds in the Migration from ISO 13790 to ISO 52016-1.* Submitted.
