# District differences in liver disease deaths across Korea, 2011-2024

Analysis code for the manuscript

> Kim S. *Why are liver disease deaths higher in some Korean districts than in others?* Manuscript under peer review.

Archived version: Zenodo, https://doi.org/10.5281/zenodo.24366641 (v1.0.0).

This repository is public under the MIT licence.

## Contents

This repository contains code only. The processed district-year data (master table, analytic panel, expected deaths, result tables, adjacency graph and boundary file) are not included; they are available from the author on reasonable request. All source statistics are public (see Data sources).

| Path | What it is |
|---|---|
| `01_스크립트/` | Analysis scripts (below) |
| `04_분석/LIVD/sets_LIVD_std3.json`, `sets_LIVD_s577.json`, `sets_LIVD_s2.json`, `sets_LIVD_s8.json`, `config_LIVD_std3.json`, `run_std3_chain.sh` | Covariates with expected directions, forced controls, negative controls, comparison outcomes and model settings (principal model `std3`; sensitivity versions with the queen contiguity graph, without the share aged 80 or older, with ten-group expected deaths, and with sex- and age-standardized expected deaths `ssx`) |
| `04_분석/LIVD/MS/` | Scripts that read the result tables and write every number, table and figure in the manuscript and the Supplementary Material, including `content_livd.py`, which generates the Methods and Results text (the draft source of the Introduction and Discussion is not included) |

Folder and some column names are in Korean because the source tables are Korean; each script has a header comment describing its inputs and outputs.

## Data sources

All inputs are public, aggregated statistics. No individual-level data are included.

- Deaths by underlying cause (liver diseases, ICD-10 K70-K76) by district of residence; comparison outcomes are deaths from chronic lower respiratory diseases (J40-J47) and Alzheimer disease (G30): Statistics Korea, cause-of-death statistics (KOSIS DT_1B34E13), 2011-2024.
- National deaths by cause and 5-year age group (to 85 years or older): Statistics Korea (KOSIS DT_1B34E01), fetched by `34_fetch_national_cause_age_deaths.py` (requires a personal KOSIS API key in `~/.kosis_key`; the key is not included).
- Population by 5-year age group: Ministry of the Interior and Safety, resident registration statistics. The 2023 age block of Changwon duplicated the 2022 block and was corrected (`population_override` in the sets files).
- Hepatitis C notifications by district, 2017-2024: Korea Disease Control and Prevention Agency notifiable infectious disease statistics.
- District covariates: Community Health Survey (high-risk drinking, smoking, walking, moderate-or-vigorous physical activity), National Health Insurance Service screening statistics (abdominal obesity, suspected diabetes), business licensing records (entertainment and singing bars), the public sports facility register, Korean Statistical Information Service local indicators, and a harmonized public district panel (internal medicine specialists, basic livelihood security recipients).

## Pipeline

Run from the repository root (set `ST_DATA_ROOT` and `ST_FBDZIP_CORRECTED` to the local copies of the public source files).

| Step | Script | Output |
|---|---|---|
| 0 | `34_fetch_national_cause_age_deaths.py`, `99m3_screen_mortality_prep.py`, `98_fit_forced.R`, `99m3_screen_mortality.py` | National cause-by-age deaths, screening panels and spatial screening of six causes of death |
| 1 | `99b_extra_canonical_pool.py`, `99c_extra_canonical_pool_livd.py` | Hepatitis C, bars, screening, specialist, assistance and negative-control indicators joined by district code |
| 2 | `39m_livd.py LIVD`, `39ms_livd.py` | Expected deaths by indirect standardization in eighteen 5-year age groups (ten groups and sex-by-age for sensitivity) |
| 3 | `80_build_disease_panel_v.py LIVD` (`ST_VER=std3`) | Analytic panel |
| 4 | `81_fit_inla.R LIVD` (`ST_VER=std3`, `ST_GRAPH=04_분석/LIVD/graph_593.graph`, `ST_THREADS=1`; see `04_분석/LIVD/run_std3_chain.sh`, which wraps R jobs in `rslot.sh`) | Principal model, set comparison, 200-subset multiverse, window models |
| 5 | `85_window_maps.R`, `86_yearly_maps_ehsa.py`, `86b_ehsa_modified_mk.py`, `87_window_grid.py` | Maps, yearly smoothed ratios and emerging hot spot analysis |
| 6 | `88g_sens_prep.py LIVD std3 CLRD,ALZ`, `88g_sens_suite.R` (`GROUP=1..6`), `88h_ppc_varpart.R`, `88k_struct_kh.R` (nb, struct, kh, review) with `kh_constraints.R`, `89g_sens_combine.py` | Sensitivity analyses, comparison outcomes, Knorr-Held models, review outputs |
| 6b | `88l_livd_prespec.R` | Sensitivity analyses defined with the covariate set (suspected liver disease, out-of-district care, self-reported obesity, monthly drinking, district type, physical activity alone) |
| 6c | `88r_reverse_check.R` (`REV=moderate_pa_rate`; `MBP=farm_share_z`) | Post hoc examination of the positive association of moderate-or-vigorous physical activity |
| 7 | `04_분석/LIVD/MS/build/` (`build_refs_livd.py`, `figs_livd.py`, `build_crhg_livd.py`, `esm_livd.py`, `cover_crhg_livd.py`, `run_all_livd.sh`) | Manuscript, the Supplementary Material, figures and checks |

The boundary file is found at `data/boundary/final.shp` by default; set `ST_SHP` to use another path.

## Software

R 4.6.0 with R-INLA 25.10.19, spdep and sf; Python 3.9 with pandas, geopandas, numpy, scipy, matplotlib and python-docx.

## License

Code: MIT (see `LICENSE`). The source statistics belong to their publishers and are not redistributed here.
