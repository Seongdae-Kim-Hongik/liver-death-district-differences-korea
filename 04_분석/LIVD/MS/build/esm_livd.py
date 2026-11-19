# esm_livd.py — 간질환 사망 보충자료 Supplementary Material(보충 방법·Table S1-S6·Figure S1-S2·STROBE). 수치는 결과 CSV에서만. 미국식 철자.
#  한 파일, 첫 쪽에 논문 제목·저널·저자·소속·교신 이메일.
import os, re, json, subprocess, pandas as pd
from docx.shared import Cm
import content_livd as C
from build_common_livd import LABEL, GROUPS, TX, TITLE as DTITLE, AFFIL, foot_row, read_draft
HERE = os.path.dirname(os.path.abspath(__file__)); MSD = os.path.dirname(HERE); OUT = os.path.join(MSD, "out"); B = os.path.dirname(MSD); RS = os.path.join(B, "results_std3")
N = C.N; ROB = C.ROB
st = lambda t: f"{t[0]:.3f} ({t[1]:.3f}-{t[2]:.3f})"
J = TX(cite="sup")
def TF(title, header, rows, foot="", fs=8):
    J.page_break(); J.table_fit(title, header, rows, "", fs_max=fs, title_bold=False)
    if foot: foot_row(J, foot, 8, 12)
J.para("<b>Supplementary Material</b>")
J.para(f"Article title: {DTITLE}")
J.para("Journal: Clinics and Research in Hepatology and Gastroenterology")
J.para(f"Author: Seongdae Kim, {AFFIL}. Corresponding author e-mail: kimsd@hongik.ac.kr")
J.para("Contents: Supplementary Methods and additional results; Tables S1-S6 (Tables S3 and S5 in three parts, Table S4 in two parts); Figures S1-S2; STROBE checklist.")
_LK = C._LK; _MT = pd.read_csv(os.path.join(B, "panel_META_LIVD_std3.csv"), encoding="utf-8-sig").set_index("variable")
_imp = lambda v: int(_MT.loc[v, "n_imputed_interp"] + _MT.loc[v, "n_imputed_sgg_mean"] + _MT.loc[v, "n_imputed_year_mean"])
PREFILL = {"screening_diabetes_suspected_share": 19, "basic_livelihood_rate": 33}   # 99c에서 80 규칙으로 미리 채운 칸(용인·창원·천안 2011-12, 세종 2012-24 원표 공백)
assert int(_MT.loc["screening_abdominal_obesity_share", "obs_year_min"]) == 2013
gate = open(os.path.join(B, "data_gate_LIVD_std3_261108.txt"), encoding="utf-8").read(); nwarn = int(re.search(r"경고 (\d+)건", gate).group(1))
J.page_break(); J.head("Supplementary Methods and additional results", 2)
SM = [("Outcome.", "Annual deaths with a liver disease as the underlying cause (International Classification of Diseases, 10th revision, K70-K76) by district of residence came from the cause-of-death statistics of Statistics Korea (deaths by cause, sex and district). Deaths are attributed to the district of the registered address at death. Liver cancer (C22) and viral hepatitis (B15-B19) are separate causes in the 104-item list and were not included."),
      ("Expected deaths.", f"National liver disease deaths by 5-year age group (0-4 to 80-84 years and 85 years or older, both sexes combined) came from the national cause-of-death table by cause, sex and age. Deaths with unknown age ({int(N['age_unknown'])} in 14 years) were excluded from the age-specific rates. District age structures came from resident registration statistics. Expected deaths summed nationally to the observed national deaths each year. In the 2023 resident registration file, the age block of Changwon duplicated the 2022 block; the 2023 total was replaced with the official total (1,009,038). A coarser expected count with ten age groups (to 75 years or older) was used in one sensitivity analysis."),
      ("Covariates.", "Hepatitis C notifications by district of residence for 2017-2024 came from the notifiable infectious disease statistics of the Korea Disease Control and Prevention Agency; the rate per 100,000 person-years was computed over the eight years, log-transformed and held constant within each district for all years, because nationwide notification began in mid-2017 (no district had zero notifications). Entertainment and singing bars are businesses licensed as entertainment bars or singing bars (yuheung and danran jujeom) in operation at the end of each year, divided by the resident population. Abdominal obesity and suspected diabetes came from National Health Insurance Service screening statistics: abdominal obesity is the share of metabolic syndrome screening participants with a waist circumference of at least 90 cm in men or 85 cm in women (published from 2013), and suspected diabetes is the share of screening participants judged as suspected diabetes on measured fasting glucose, which excludes people already treated for diabetes. Community Health Survey indicators are district age-standardized estimates of high-risk drinking, current smoking, walking practice and moderate-or-vigorous physical activity (work, transport and leisure activity combined). Public sports facilities per 100,000 residents came from the national register of public sports facilities. Internal medicine specialists per 100,000 residents and the share of basic livelihood security recipients came from a harmonized public district panel. District-level data on chronic hepatitis B, alcohol consumption per capita, antiviral treatment, hepatology specialists and liver transplantation were not available."),
      ("Panel checks before modeling.", f"An automated gate run on the analytic panel reported {nwarn} flags (Table S2). Most flagged standardized columns whose yearly means were near 0 (a ratio artifact) or the post-2020 indicator (constant by design); the sex ratio is expressed as men per 100 women and may exceed 100. Missing years were interpolated within districts, then filled with district means, and, for districts never observed, with yearly national means; no covariate had 100 or more yearly-mean cells. Abdominal obesity was filled with district means for 2011-2012 and with yearly means for Sejong; suspected diabetes and suspected liver disease were filled for four districts with blank source cells (19 cells each); fiscal autonomy was filled with yearly means for the two Jeju districts (28 cells). In 11 cities with urban wards, 33 basic livelihood values for 2021-2023 were implausible because the ward-level records had not been combined: 31 fell below 20% and 2 (Changwon, 2022-2023) exceeded five times the city's mean of 2020 and 2024. They were set to missing and interpolated linearly within the district. The national median of high-risk drinking fell during 2020-2021 and that of abdominal obesity shifted around the 2018 screening reform; these national shifts are absorbed by the year effects."),
      ("Models.", f"Software: R 4.6.0 with R-INLA; Python 3.9 for data preparation and figures. The negative binomial likelihood was chosen because its widely applicable information criterion (WAIC) for the forced-controls model was lower than that of a Poisson likelihood ({_LK['nbinomial']:,.1f} vs {_LK['poisson']:,.1f}). Fixed effects had normal priors with mean 0 and precision 4 (intercept precision 0.001). The Besag-York-Mollié 2 district effect used penalized-complexity priors (P(σ>0.5)=0.01; P(φ<0.5)=2/3) on a 593-edge district adjacency graph with Jeju Island as a separate connected component (the intrinsic component was scaled and constrained to sum to zero within each connected component); the random-walk and independent year effects used penalized-complexity priors (P(σ>0.5)=0.01). Covariate subsets for the multiverse were drawn with a fixed seed, each characteristic entering with probability 0.5, excluding empty and duplicate subsets; all 200 fits converged. Knorr-Held interactions used Kronecker-product structures (type I: independent; II: random walk in time by independent districts; III: independent years by intrinsic conditional autoregressive districts; IV: random walk by intrinsic conditional autoregressive districts). The queen-contiguity sensitivity graph (577 edges) omits the 16 audited contact links of the principal graph. The Spatial+-type method regressed each standardized covariate on the 23 lowest-frequency eigenvectors of the graph Laplacian and re-standardized the residuals, so its rate ratios are per 1 standard deviation of the residualized covariate. Estimates from the 20 perturbations of filled values were pooled with Rubin's rules. Between- and within-district components were the district mean and the deviation from district and year means; the time-invariant hepatitis C rate has only a between-district component. District type was coded from the administrative suffix (urban ward of a metropolitan city, city, county). The share of farm-household residents used in the post hoc analysis came from the agricultural census series (urban wards of metropolitan cities set to 0)."),
      ]
for h, t in SM: J.para(f"<b>{h}</b> {t}")
_tc = N["type_class"]; _eh = N["ehsa"]
J.para("<b>Additional results.</b> " + f"Kendall's W of annual rankings was {N['kendall_W']:.2f} over 2011-2024 ({N['kendall_W_1119']:.2f} in 2011-2019 and {N['kendall_W_2024']:.2f} in 2020-2024). Emerging hot spot analysis of smoothed ratios classified {_eh['Persistent hot']} districts as persistent hot spots, {_eh['New hot']} as new hot spots, {_eh['Sporadic hot']} as sporadic hot spots and {_eh['Persistent cold']} as persistent cold spots (Seoul Gangnam, Seocho and Songpa and Gwacheon) (Figure S1). "
       f"Cold spots comprised {_tc['coldspot']['ward']} urban wards, {_tc['coldspot']['city']} cities and {_tc['coldspot']['county']} counties. With a stricter posterior probability threshold of 0.975, {N['hot_strict'][0.975][0]} hot and {N['hot_strict'][0.975][1]} cold spots remained. Spearman correlations of window-specific residual rate ratios were {N['win_rr_rho'][1]:.2f} (2011-2015 vs 2016-2019), {N['win_rr_rho'][2]:.2f} (2016-2019 vs 2020-2024) and {N['win_rr_rho'][0]:.2f} (2011-2015 vs 2020-2024). "
       f"The fixed covariates accounted for {100*N['varpart']['fixed_covariates']['share_of_linear_predictor_var']:.0f}% of the variance of the linear predictor and the structured district effect for {100*N['varpart']['spatial_structured']['share_of_linear_predictor_var']:.0f}%. A parsimonious model with the seven subset-stable characteristics and the forced controls had WAIC {N['s50_moran']['parsimonious']['WAIC']:,.1f} and the same seven credible associations. In a model adding an indicator for 2020-2024, the indicator was {st(N['covid_main'])} relative to 2011-2019; because expected deaths were rescaled to the national total each year, it reflects relative rather than national change.")
# ── Table S1 ──
DIR = {"hcv_notification_rate_log": "+", "alcohol_venues_per10k": "+", "high_risk_drinking_rate": "+", "screening_abdominal_obesity_share": "+", "screening_diabetes_suspected_share": "+", "current_smoking_rate": "+",
       "walking_practice_rate": "−", "moderate_pa_rate": "−", "public_sports_facilities_per_100k": "−", "im_specialists_per_100k": "−", "basic_livelihood_rate": "+"}   # sets_LIVD_std3.json expected_direction
_sj = json.load(open(os.path.join(B, "sets_LIVD_std3.json"))); _ed = _sj["expected_direction"]
assert all(_ed[c].startswith(DIR[_MT.loc[_MT.source_column == c].index[0]].replace("−", "-")) for c in _ed), "기대 방향 불일치"
SRC = {"kchs": "Survey", "chk": "Screening", "eloc": "KOSIS", "fac": "Registry"}
EXT = {"ext__pop80_share": "Registry", "ext__basic_livelihood_rate": "Panel", "ext__im_specialists_per100k": "Panel", "ext__hcv_notif_rate_log": "KDCA", "ext__alcohol_venues_per10k": "Licensing", "ext__dm_suspect_share": "Screening"}
UNIT = {"hcv_notification_rate_log": "log per 100,000", "alcohol_venues_per10k": "per 10,000", "high_risk_drinking_rate": "%", "screening_abdominal_obesity_share": "%", "screening_diabetes_suspected_share": "%",
        "current_smoking_rate": "%", "walking_practice_rate": "%", "moderate_pa_rate": "%", "public_sports_facilities_per_100k": "per 100,000", "im_specialists_per_100k": "per 100,000", "basic_livelihood_rate": "%",
        "urban_population_share": "%", "physicians_per_1000": "per 1,000", "sex_ratio": "ratio", "fiscal_independence": "%", "pop80_share": "%"}
YRS = {"hcv_notification_rate_log": "2017-2024"}
rows = []
for g, vs in GROUPS:
    rows.append(["__H__", g])
    for v in vs:
        m = _MT.loc[v]; sc = str(m.source_column); src = EXT.get(sc, SRC.get(sc.split("__")[0], sc.split("__")[0]))
        rows.append([f"  {LABEL[v]}", UNIT[v], src, YRS.get(v, f"{int(m.obs_year_min)}-{int(m.obs_year_max)}"), ("Forced" if m.role == "forced" else DIR[v]), f"{_imp(v) + PREFILL.get(v, 0):,}"])
TF("Table S1 Source, unit, observed years, expected direction and filled cells for each district characteristic, Korea, 2011-2024", ["Characteristic", "Unit", "Source", "Years", "Direction", "Filled cells"], rows,
   "Survey, Community Health Survey (district age-standardized rates); screening, National Health Insurance Service health screening statistics; KOSIS, Korean Statistical Information Service local indicators; KDCA, Korea Disease Control and Prevention Agency notifiable disease statistics (time-invariant); licensing, local business licensing records; registry, resident registration or public sports facility register; panel, harmonized public district panel; ratio, men per 100 women; forced, in every model. Filled cells of 3,206 district-years (interpolation, district means or yearly means). Direction, expected direction of association with liver disease mortality.")
# ── Table S2: 자료 점검 ──
cnt = lambda tag: len(re.findall(r"\[" + re.escape(tag) + r"\]", gate)); two = re.findall(r"\[연도 간 평균 2배 이상 차이\] (\S+):", gate)
ext = json.load(open(os.path.join(RS, "S41_extreme_flags.json"))); impc = json.load(open(os.path.join(RS, "S41_imputed_cells.json")))
rows = [["Year with all districts zero or missing", "≥98% of districts", "1 (post-2020 indicator)", "None (by design)"],
        ["Constant within a year", "1 value in a year", "1 (same indicator)", "None (by design)"],
        ["Year explains most variance", "Year R² ≥ 0.80", "1 (same indicator)", "None (by design)"],
        ["Yearly means differ twofold or more", "Max/min yearly mean ≥ 2", f"{len(two)} (mostly standardized, mean near 0)", "Checked against sources; retained"],
        ["Ratio-type column above 100", "Maximum > 100", f"{cnt('비율형인데 100 초과')} (sex ratio, men per 100 women)", "Retained (definition)"],
        ["Extreme district-years", ">5 IQR beyond quartiles", f"{sum(ext.values())} cells in {sum(1 for v in ext.values() if v)} covariates", "Refilled in one alternative specification"],
        ["Missing district-years", "No observation", f"{sum(impc.values()):,} cells across {len(impc)} covariates", "Filled within districts; perturbation check"],
        ["Blank screening source cells", "No observation", "19 cells in 4 districts", "Filled with district or yearly means"],
        ["Implausible values", "Off neighbors", "33 (basic livelihood, 11 cities with urban wards, 2021-2023)", "Set to missing and interpolated"],
        ["Duplicated population block", "Repeats 2022", "1 district-year (Changwon, 2023)", "Replaced with official total"],
        ["Yearly-mean filling", "≥100 yearly-mean cells", "0 covariates", "None needed"]]
assert nwarn == 3 + len(two) + cnt("비율형인데 100 초과"), (nwarn, len(two))
TF("Table S2 Panel checks before modeling, with rules, thresholds, flags and actions, Korea, 2011-2024", ["Check", "Threshold", "Flags in this panel", "Action"], rows, "Checks were run on the analytic panel of 3,206 district-years. The missing district-years row counts cells filled during panel construction; the 19 blank screening cells and the three implausible values were handled before panel construction, so Table S1 shows all filled cells. IQR, interquartile range.", fs=8)
# ── Table S3: 사양 ──
NAMES = [("principal", "Principal model"), ("KH_typeI", "Knorr-Held type I"), ("KH_typeII", "Knorr-Held type II"), ("KH_typeIII", "Knorr-Held type III"), ("KH_typeIV", "Knorr-Held type IV"),
         ("icar_besag", "ICAR district effect"), ("iid_only", "IID district effect"), ("no_spatial", "No district effect"), ("knn3", "3 nearest neighbors"), ("knn4", "4 nearest neighbors"), ("knn5", "5 nearest neighbors"),
         ("B3_smooth_forced", "Smoothed sex ratio"), ("C1_poisson_lognormal", "Poisson, observation effect"), ("C2_rw2_year", "RW2 year effect"), ("C3_ar1_year", "AR1 year effect"), ("C4_sido_year_iid", "Province-by-year effect"), ("D1_spatial_plus", "Spatial+-type adjustment"),
         ("E0_nolag_from2012", "No lag, from 2012"), ("E1_lag1", "Lag 1 year"), ("E0_nolag_from2013", "No lag, from 2013"), ("E2_lag2", "Lag 2 years"), ("F3_extreme_R7", "Extreme values refilled"), ("G1_kchs_ma3", "Survey 3-year averages"), ("H4_odd_years", "Odd years only"), ("H4_even_years", "Even years only"),
         ("s8", "Ten age groups in E"), ("ssx", "Sex- and age-standardized E"), ("s2", "Share aged 80+ omitted"), ("s577", "Queen graph, 577 edges"), ("parsimonious", "Parsimonious model"),
         ("H1_nco_CLRD", "CLRD deaths (comparison)"), ("H1_nco_ALZ", "Alzheimer deaths (comparison)")]
SS = {**N["s43"], **N["s41"]}; WA = {**N["s43_waic"], **N["s41_waic"]}
for v in ("s577", "s2", "s8", "ssx"): SS.update({(v, c): t for c, t in N["sens_main"][v].items()}); WA[v] = float(pd.read_csv(os.path.join(B, f"results_{v}", "S3_main_fit.csv")).WAIC.iloc[0])
SS.update({("parsimonious", c): (r["IRR"], r["lo"], r["hi"], r["cred"]) for c, r in N["s50_pars"].items()}); WA["parsimonious"] = N["s50_moran"]["parsimonious"]["WAIC"]; WA["principal"] = N["waic_main"]
SS.update({("principal", c): (r["IRR"], r["lo"], r["hi"], r["cred"]) for c, r in N["main"].items()})
def cell(a, v): t = SS.get((a, v)); return "–" if t is None else st(t)
HN = {C.HCV: "Hepatitis C", C.BAR: "Bars", C.DMS: "Suspected diabetes", C.SMK: "Smoking", C.BLS: "Basic livelihood", C.FAC: "Sports facilities", C.MPA: "Moderate-or-vigorous activity"}
ALT14 = set(N["alt14"]); assert len(ALT14) == 14 and ALT14 <= {a for a, _ in NAMES}, sorted(ALT14 - {a for a, _ in NAMES})
FOOT3 = "Values are rate ratios (95% credible intervals) per 1 standard deviation; –, not in the model or not computed. For the Spatial+-type model, rate ratios are per 1 standard deviation of the residualized covariate and are not directly comparable in magnitude with principal-model estimates. <sup>a</sup>One of the 14 alternative specifications counted in the main text. CLRD, chronic lower respiratory diseases; ICAR, intrinsic conditional autoregressive; IID, independent and identically distributed; RW2, second-order random walk; AR1, first-order autoregressive; WAIC, widely applicable information criterion. WAIC is not comparable for the Poisson model with an observation-level effect (whose latent effect absorbs overdispersion) or across outcomes."
MOR = {"principal": "principal", "parsimonious": "parsimonious", "no_spatial": "no_spatial", "iid_only": "iid_district", "icar_besag": "icar_district", "KH_typeI": "typeI_interaction"}
for part, cols in (("A", [C.HCV, C.BAR]), ("B", [C.DMS, C.SMK, C.BLS]), ("C", [C.FAC, C.MPA])):
    rows = [[lab + ("<sup>a</sup>" if a in ALT14 else "")] + ([f"{WA[a]:,.0f}" if a in WA and not a.startswith("H1_") else "–", f"{N['s50_moran'][MOR[a]]['resid_moran_I']:.3f}" if a in MOR else "–"] if part == "A" else []) + [cell(a, v) for v in cols] for a, lab in NAMES]
    TF(f"Table S3{part.lower()} Rate ratios per 1 standard deviation across alternative specifications and comparison outcomes, Korea, 2011-2024 (part {part})", ["Specification"] + (["WAIC", "Residual Moran's I"] if part == "A" else []) + [HN[v] for v in cols], rows, FOOT3 + (" Residual Moran's I was computed on district means of Pearson residuals for the listed models." if part == "A" else ""))
# ── Table S4: 권역 ──
REG = [("Capital", "Capital region"), ("Chungcheong", "Chungcheong"), ("Honam", "Honam"), ("Yeongnam", "Yeongnam"), ("Gangwon_Jeju", "Gangwon-Jeju")]
_rs = pd.read_csv(os.path.join(RS, "S50_region_slopes.csv")); _nd = _rs.groupby("region").n_district_years.first().to_dict()
RV = [v for v in [C.HCV, C.BAR, C.DMS, C.SMK, C.BLS, C.FAC, C.MPA] if (v, "Capital") in N["s50_region"]]; assert len(RV) == 7, RV
for part, vs in (("A", RV[:4]), ("B", RV[4:])):
    rows = [[lab, f"{_nd[r]:,}"] + [st(N["s50_region"][(v, r)]) for v in vs] for r, lab in REG]
    rows.append(["ΔWAIC vs common", ""] + [f"{N['s50_region_dwaic'][v]:+.1f}" for v in vs])
    TF(f"Table S4{part.lower()} Region-specific rate ratios per 1 standard deviation for the subset-stable characteristics, Korea, 2011-2024 (part {part})", ["Region", "District-years"] + [HN[v] for v in vs], rows,
       "Principal model with each characteristic interacted with five regions (capital region: Seoul, Incheon, Gyeonggi; Chungcheong: Daejeon, Sejong, North and South Chungcheong; Honam: Gwangju, North and South Jeolla; Yeongnam: Busan, Daegu, Ulsan, North and South Gyeongsang; Gangwon-Jeju). ΔWAIC, difference in WAIC from the common-slope model (negative favors region-specific slopes).")
# ── Table S5: 사전지정 민감도(88l) ──
S45 = N["s45"]
AN = [("A_liver_suspect", "Suspected liver disease added", "screening_liver_disease_suspected_share"), ("B_outside_care", "Outside care added", "outside_care_share"),
      ("C_obesity_selfreport", "Self-reported obesity", "obesity_rate"), ("D_monthly_drinking", "Monthly drinking added", "monthly_drinking_rate"), ("E_district_type", "District type", "type_gu")]
P7 = [C.HCV, C.BAR, C.DMS, C.SMK, C.BLS, C.FAC, C.MPA]
mainrow = lambda vs: ["Principal model", f"{N['waic_main']:,.0f}"] + [st((N['main'][v]['IRR'], N['main'][v]['lo'], N['main'][v]['hi'])) for v in vs]
FT5 = "Rate ratios per 1 standard deviation (95% credible intervals). Rows: screening share with suspected liver disease added; out-of-district outpatient share added; measured abdominal obesity replaced by self-reported obesity; monthly drinking added; fixed effects for district type."
rows = [mainrow(P7[:2]) + ["–"]] + [[lab, f"{N['s45_waic'][a]:,.0f}"] + [st(S45[(a, v)]) for v in P7[:2]] + [st(S45[(a, ex)])] for a, lab, ex in AN]
TF("Table S5a Sensitivity analyses defined with the covariate set, Korea, 2011-2024 (part A)", ["Analysis", "WAIC", "Hepatitis C", "Bars", "Added or replaced term"], rows, FT5 + " For district type, the added-term column compares urban wards with cities.")
rows = [mainrow(P7[2:5])] + [[lab, f"{N['s45_waic'][a]:,.0f}"] + [st(S45[(a, v)]) for v in P7[2:5]] for a, lab, ex in AN]
TF("Table S5b Sensitivity analyses defined with the covariate set, Korea, 2011-2024 (part B)", ["Analysis", "WAIC", "Suspected diabetes", "Smoking", "Basic livelihood"], rows, FT5)
rows = [mainrow(P7[5:])] + [[lab, f"{N['s45_waic'][a]:,.0f}"] + [st(S45[(a, v)]) for v in P7[5:]] for a, lab, ex in AN]
rows.append(["Physical activity alone", f"{N['s45_waic']['F_pa_alone']:,.0f}", st(S45[("F_pa_alone", C.FAC)]), st(S45[("F_pa_alone", C.MPA)])])
TF("Table S5c Sensitivity analyses defined with the covariate set, Korea, 2011-2024 (part C)", ["Analysis", "WAIC", "Sports facilities", "Moderate-or-vigorous activity"], rows,
   FT5 + f" Physical activity alone: walking, moderate-or-vigorous physical activity and public sports facilities with the forced controls only (walking {st(S45[('F_pa_alone', C.WALK)])}).")
# ── Table S6: 역방향 사후 검정(88r) ──
S44 = N["s44"]
rows = [["Principal model", st((N['main'][C.MPA]['IRR'], N['main'][C.MPA]['lo'], N['main'][C.MPA]['hi'])), "–"],
        ["Between-district component", st(N["bw"][C.MPA + "__between"]), "–"], ["Within-district component", st(N["bw"][C.MPA + "__within"]), "–"],
        ["Farm-household share added", st(S44[("R3_measured_added", C.MPA)]), st(S44[("R3_measured_added", "farm_share_z")])],
        ["Alone with forced controls", st(S44[("R4_single_moderate_pa_rate", C.MPA)]), "–"],
        ["Walking and facilities removed", st(S44[("R5_drop_pa", C.MPA)]), "–"],
        ["Lag 2 years", st(S41 := N["s41"][("E2_lag2", C.MPA)]), "–"], ["Knorr-Held type IV", st(N["s43"][("KH_typeIV", C.MPA)]), "–"]]
TF("Table S6 Post hoc examination of the positive association of moderate-or-vigorous physical activity, Korea, 2011-2024", ["Model", "Moderate-or-vigorous activity", "Farm-household share"], rows,
   "Rate ratios per 1 standard deviation (95% credible intervals). These analyses were done after the results were seen. Farm-household share, share of residents in farm households (urban wards set to 0), standardized.")
# ── Fig. S1-S2 ──
J.page_break(); _pp = J.para(""); _pp.add_run().add_picture(os.path.join(HERE, "figs", "LIVD_FigS1.png"), width=Cm(16))
J.para("<b>Figure S1.</b> Persistence of the district pattern of liver disease mortality, Korea, 2011-2024. (A) Emerging hot spot analysis (Getis-Ord Gi* with Mann-Kendall trend) of empirical Bayes-smoothed standardized mortality ratios; numbers of districts in parentheses. (B) Number of calendar windows (2011-2015, 2016-2019, 2020-2024) in which each district was a residual hot or cold spot. Map lines delineate study areas and do not necessarily depict accepted national boundaries")
J.page_break(); _pp = J.para(""); _pp.add_run().add_picture(os.path.join(HERE, "figs", "LIVD_FigS2.png"), width=Cm(10))
J.para("<b>Figure S2.</b> District types used in the district-type sensitivity analysis, Korea, 2024 boundaries. Urban wards of metropolitan cities, cities and counties; numbers of districts in parentheses. Map lines delineate study areas and do not necessarily depict accepted national boundaries")
# ── STROBE ──
DS = [x[4:].strip() for x in read_draft()["Discussion"] if x.startswith("### ")]; MH = [h for h, _ in C.METHODS]; RH = [h for h, _ in C.RESULTS if h]
CK = [("Title and abstract", "1", "Title page; Abstract"), ("Background/rationale", "2", "Introduction"), ("Objectives", "3", "Introduction, final paragraph"), ("Study design", "4", f"Methods, {MH[0]}"), ("Setting", "5", f"Methods, {MH[0]}"),
      ("Participants", "6", f"Methods, {MH[0]} (district populations; ecological)"), ("Variables", "7", f"Methods, {MH[1]} and {MH[2]}; Table S1"), ("Data sources/measurement", "8", "Methods; Supplementary Methods; Table S2"),
      ("Bias", "9", f"Methods, {MH[3]}; Tables S3, S5 and S6"), ("Study size", "10", f"Methods, {MH[0]} (all 229 districts)"), ("Quantitative variables", "11", f"Methods, {MH[2]}"),
      ("Statistical methods", "12", f"Methods, {MH[3]}"), ("Participants (flow)", "13", "Not applicable (aggregate district data; no exclusions)"), ("Descriptive data", "14", f"Results, {RH[0]}; Table 1"), ("Outcome data", "15", f"Results, {RH[0]} and {RH[1]}; Figures 1 and S1"),
      ("Main results", "16", f"Results, {RH[2]}; Table 2; Figure 2"), ("Other analyses", "17", f"Results, {RH[3]}; Tables S3-S6; Figure S2"),
      ("Key results", "18", f"Discussion, {DS[0]}"), ("Limitations", "19", "Discussion, Limitations"), ("Interpretation", "20", "Discussion"), ("Generalizability", "21", "Discussion, Implications and Limitations"),
      ("Funding", "22", "Statements and Declarations")]
assert "Limitations" in DS and "Implications" in DS
J.page_break()
J.table_fit("STROBE checklist for this ecological study", ["Item", "No.", "Where reported"], [[a, b, c] for a, b, c in CK], "", fs_max=8, title_bold=False)
foot_row(J, "STROBE, Strengthening the Reporting of Observational Studies in Epidemiology.", 8, 12)
ps = os.path.join(OUT, "Supplementary_Material_CRHG_LIVD.docx"); J.doc_title = "Supplementary Material"; J.save(ps)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_livd_esm", "--convert-to", "pdf", "--outdir", OUT, ps], check=True, capture_output=True)
print("saved", os.path.basename(ps))
