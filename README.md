# e4-platform ISO 52016-1 monthly — Method Effect Assessment

This repository contains the factorial results, intermediate quantities,
sensitivity results and evaluation and figure scripts supporting the study
*"Separating the Method Effect from Comparison-Protocol Confounds in the
Migration from ISO 13790 to ISO 52016-1"* (Tadeu, submitted, 2026). This is
the state for revision R1 at Energy & Buildings, manuscript ENB-D-26-06604.
The study has not been accepted or published.

The study is a factorial of 64 building–city–climate-base cells, each
evaluated by two methods (128 method evaluations). It spans two calculation
methods, two climate bases, eight Census-weighted Portuguese reference
buildings and four cities. The proprietary calculation engine, the source
climate files and the EPB source workbooks are not included.

Section, table and figure numbers below refer to the R1 manuscript.

## Versions

- **R1** (this state): data and scripts supporting revision R1.
- **Before R1**: tag `public-before-R1-ENB-D-26-06604` (commit
  `9d80a6e9cd7414283b95ef3893ef60f0db7ae0ec`). This tag archives the public
  repository snapshot associated with ENB-D-26-06604 before the R1 update. It
  archives the public deposit, not the full journal submission package.

## Time basis

R1 DGEG2025-A results use the verified solar-time interpretation of the EPW
data (`hora="verificada"`) in both calculation methods. REG-2013 uses
tabulated climate and is unchanged. Header-time results are historical
controls and are labelled separately: they are the `cabecalho` entries of
`resultados/fontes_HV/`, and the earlier files are at the tag above.

## What is here

```
resultados/                 factorial results, intermediate quantities and sensitivity results (R1)
resultados/fontes_HV/       full-precision sources, both time conventions, labelled
figures/                    figure producers, statistics and summary scripts
figures/submissao_R1/       the figures cited in R1 (PNG and PDF)
figures/saida_revisao/      generation intermediates, original numbering
scripts/                    verification, production and sensitivity scripts
scripts/sensibilidades_hv/  verified-solar-time helpers for the author's engine (see LEIA-ME.md)
```

### Core results

| File (`resultados/`) | Contents |
|---|---|
| `grelha_artigo13_REVISAO.json` | 32 cells, DGEG2025-A, verified solar time, both methods, 3 decimals |
| `grelha_artigo13_2013_REVISAO.json` | 32 cells, REG-2013, both methods, 3 decimals |
| `decomposicao_artigo13_REVISAO.json` | R1 anatomical decomposition, DGEG2025-A: inferred season, inertia, utilisation factors, sky radiation and gain–loss ratios |
| `decomposicao_artigo13_2013_REVISAO.json` | the same decomposition for REG-2013 (unchanged; this base does not read the EPW) |
| `fontes_HV/RESULTADO_A13_COMPLETO.json` | full-precision needs of the 32 DGEG2025-A cells in both time conventions (`verificada`, used in R1; `cabecalho`, historical control), the REG-2013 control and the monthly irradiation by orientation |
| `fontes_HV/INTERMEDIARIOS_A13_COMPLETO.json` | full-precision intermediate quantities (anatomy), both time conventions |
| `cruzamento_ingenuo_rb6_coimbra_REVISAO.json` | naive cross-comparison, RB6/Coimbra (§3.1), from the full-precision sources, with no rounding before the ratios |
| `estatisticas_R1.txt` | output of `figures/estatisticas.py --revisao` |
| `NUMEROS_revisao_A13.md` | a summary of statistics computed from the deposited data; it is not a claim of exhaustive verification of the manuscript |
| `ORIGEM_R1.json` | provenance: hashes of the sources, scripts and derived files |

The three grid and decomposition files are derived from `fontes_HV/` by
`scripts/preparar_figuras_r1.py`. The values link to the full-precision
sources, and `scripts/verificar_revisao_a13.py` (V0) checks the derivation.

### Isolation experiments and sensitivities

The Eq. (97), shading, ground-coupling and α = 0.60 files contain the R1
experiments in verified solar time; REG-2013 controls are retained. See
`scripts/sensibilidades_hv/LEIA-ME.md` for configuration, provenance and
reproduction dependencies.

| File (`resultados/`) | Experiment | Manuscript |
|---|---|---|
| `sensibilidade_eq97_REVISAO.json` | ISO 52016-1 Eq. (97) cutoff, 64 monthly evaluations | §2.4 |
| `sensibilidade_sombreamento_REVISAO.json` | summer movable shading removed, 64 evaluations | Table 2 |
| `sensibilidade_hgr22_REVISAO.json` | ±22% on the ground heat-transfer coefficient, single-family cells | §4.4, Table 2 |
| `isolamento_solo_artigo13_REVISAO.json` | ground-coupling term isolated (b_tr = 0.8 substitution), 16 cells × 2 bases | §3.3 |
| `sensibilidade_alfa060_A13.json`, `decomposicao_artigo13_alfa060.json` | opaque solar absorptance α = 0.60 for walls, both axes | §4.4, Table 2 |
| `sensibilidade_gsul_janela_HV.json` | reference south irradiation window, seasonal method | §3.3, §4.4, Table 2 |

`sensibilidade_gsul_janela_HV.json` holds 32 cells × four seasonal windows
(128 observations), DGEG2025-A, seasonal method only. For Coimbra it gives
96.5 kWh/m²·month for October–April (production) and 92.2 for
November–March. Relative to production, November–March changes N_ic by a
median of 0.00%, with a minimum of −3.23% and a maximum of +4.42%.

The producers of the α = 0.60 and irradiation-window experiments are
deposited (`scripts/sensibilidade_alfa060_A13.py`,
`scripts/sensibilidade_gsul_janela_HV.py`). The producers of the Eq. (97),
shading, ground-term and ground-isolation experiments are part of the
proprietary engine and are available from the author on request, together
with it. The helpers in `scripts/sensibilidades_hv/` document how those
producers were run in verified solar time. On their own, they do not
reproduce those experiments in a clone of this repository.

### Figures

The figures cited in R1 are `figures/submissao_R1/Fig1`–`Fig10` (PNG and
PDF). `Graphical_abstract` is separate. The files in `figures/saida_revisao/`
use the original numbering and are generation intermediates.

| Original number | R1 number | Content (producer name) |
|---|---|---|
| 5 | 1 | Parity scatter |
| 2 | 2 | Method effect conditional |
| 3 | 3 | Heatmap ΔH |
| 7 | 4 | Base effect by method |
| 4 | 5 | Confound cascade |
| 8 | 6 | γ_C separator |
| 1 | 7 | Cooling threshold |
| 9 | 8 | Anatomy |
| 10 | 9 | Utilisation map |
| 6 | 10 | Setpoint scenario |

The R1 figures were rendered with matplotlib 3.11.0. Other versions give the
same content with small differences in rendering.

## Reproducing

The scripts do three things. They check the deposited data numerically, they
run physics checks, and they produce the data. The physics checks and the
production scripts require the author's engine and fixtures, which are
available on reasonable request. The statistics and figure scripts use only
the deposited JSON.

From the repository root (Python ≥ 3.10; the checks use only the standard
library; the figures need numpy and matplotlib; on Windows use `py`):

```
python scripts/verificar_revisao_a13.py                      # numerical checks of the deposited data
python scripts/verificar_revisao_a13.py --controlo-negativo  # one negative control per check
python scripts/preparar_figuras_r1.py                        # derived JSON = fontes_HV (no writing)
python figures/estatisticas.py --revisao                     # same output as resultados/estatisticas_R1.txt
python figures/gerar_figuras.py --revisao
python figures/gerar_figuras_8_9.py --revisao
python figures/gerar_figuras_fix_e_10.py --revisao
python scripts/numerar_figuras_r1.py                         # figures/saida_revisao -> figures/submissao_R1
python figures/numeros_revisao.py                            # regenerates resultados/NUMEROS_revisao_A13.md
```

With the author's engine (`PATH` is its root, containing `src/e4/` and
`studies/a13_iso52016_mensal/`; `NEWFOLDER` must lie outside the engine and
outside this repository):

```
python scripts/verificar_revisao_a13.py --motor PATH                # adds physics checks F1-F3 and the informative V5
python scripts/verificar_artigo13.py --motor PATH                   # historical environment triage
python scripts/revisao_a13_producao.py --motor PATH --saida NEWFOLDER
python scripts/sensibilidade_alfa060_A13.py --motor PATH --saida NEWFOLDER
python scripts/sensibilidade_gsul_janela_HV.py --motor PATH --saida NEWFOLDER
```

`verificar_revisao_a13.py` exits with a non-zero code on any failure. A check
that needs the engine reports SKIP when the engine is not given; SKIP is not a
pass. Each numerical anchor is the published value, and a check passes when
the recomputed value, rounded to the anchor's digits, equals it.
`verificar_artigo13.py` is the environment triage of the author's private
package, kept with its original scope. It does not check R1 numbers, and
without the engine it exits with code 2.

Execution log of this state (4 November 2026, Python 3.10, Linux):

| Command | Result |
|---|---|
| `verificar_revisao_a13.py` | 57 PASS · 0 FAIL · 3 SKIP (physics, no engine) · 2 INFO; exit code 0 |
| `verificar_revisao_a13.py --controlo-negativo` | 10/10 negative controls detected for the expected reason; exit code 0 |
| `verificar_revisao_a13.py --motor PATH` | 71 PASS · 0 FAIL · 0 SKIP · 2 INFO; exit code 0 |
| `verificar_revisao_a13.py --motor PATH --controlo-negativo` | 13/13 negative controls detected for the expected reason; exit code 0 |
| `verificar_artigo13.py --motor PATH` | 37/37 PASS; exit code 0 (without the engine: not executed, exit code 2) |

The check counts announced with the submitted version (37/37 and 9/9) belong
to that version and do not stand in for this log.

## Envelope parity

The study requires identical envelope inputs on the two calculation axes.
With the engine, `verificar_artigo13.py` compares three things between the
axes: the opaque solar absorptance of walls, the opaque solar absorptance of
roofs and the attic resistance. `verificar_revisao_a13.py` (F1) checks the
same three under the R1 configuration. It also checks the surface
coefficients that each axis applies with its own convention (h_ce = 20.0 and
h_re = 4.14 W/m²K on the monthly axis; R_se = 0.04 m²K/W on the seasonal
axis). Finally, it checks that the shared modules are restored after the
runtime overlay.

The +86.8% versus +1.9% example is a historical diagnostic under the time
convention of the submitted version; it has not been revalidated under
verified solar time.

## Calculation engine

The calculation engine itself (e4, Python), including the ISO 52016-1 monthly
kernel, the ISO 52010-1 solar transposition chain and the EN ISO 13370
ground-coupling module, is proprietary and is not included here. It is
available from the author on reasonable request.

## Verification oracles

The engine was checked against four reference cases distributed by the EPB
Center (a single-family dwelling in Strasbourg, a small office in Athens, and
BESTEST cases 600 and 940). The reference cases are distributed by the EPB
Center under a CC BY-NC-ND 4.0 licence and are not redistributed here.
Re-running these physics checks requires the author's engine and the
reference cases from the EPB Center.

## Climate data

The DGEG2025-A base derives from the national climate panel (SCE.CLIMA v2.3)
and from the EPW hourly series, and the source files are not included.
Production data correspond to the "replica" behaviour of the distributed
workbook, which contains the index-alignment defect documented in §2.2 of the
article. The REG-2013 base is reconstructed from the 2016
reference-meteorological-years tool, as described in §2.2.

## Related work

The hourly method of ISO 52016-1, applied to the same reference-building
portfolio under future climate scenarios, is the subject of a companion study
in preparation. The studies share a reference-building framework. Numerical
comparisons between the studies require matched configuration and time
conventions. This deposit does not assert identity of the monthly outputs.

The prospective techno-economic assessment of HVAC+PV system sets under
future climate and grid decarbonisation scenarios is available at
[`e4-platform-technoeconomic`](https://github.com/vertcapital-afk/e4-platform-technoeconomic).

## Licence

Scripts: MIT (see `LICENSE`).
Data: CC BY 4.0 (see `LICENSE-DATA`).

## Citation

Tadeu, S. F. (2026). *Separating the Method Effect from Comparison-Protocol
Confounds in the Migration from ISO 13790 to ISO 52016-1.* Manuscript under
revision, Energy & Buildings, ENB-D-26-06604.
