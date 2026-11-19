# build_common_livd.py — 간질환 사망 원고 공통 부품(초안 읽기·인용·표·그림 설명·단어 수·고아 제목). 저널별 조립은 build_crhg_livd.py.
import os, re, json, subprocess
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt, Cm
from jkms_engine import JKMS
import content_livd as C
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_livd.json"), encoding="utf-8"))
DRAFT = os.path.join(MS, "draft", "01_manuscript.md")
_zf = os.path.join(OUT, "zenodo_doi.txt"); ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "[ZENODO DOI]"
TITLE = C.TITLE; ORCID = "0000-0002-1525-0091"
AFFIL = "Department of Biohealth Convergence Open Sharing System, Hongik University, Seoul, Republic of Korea"
ADDRESS = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
IRB = "This study was performed in line with the principles of the Declaration of Helsinki. The Institutional Review Board of Hongik University approved the study on November 4, 2025 (Approval No. 7002340-202511-HR-012) and its continuing review on November 3, 2026 (Approval No. 7002340-202611-HR-040)."
CONSENT = "The Institutional Review Board of Hongik University waived informed consent because only published aggregate statistics were used."
FUNDING = "No funding was received for conducting this study."
CONTRIB = "Seongdae Kim conceived and designed the study, acquired and analyzed the data, interpreted the results, drafted and revised the manuscript, and approved the final version as the sole author."
COI = "The author has no relevant financial or non-financial interests to disclose."
def data_statement(): return f"All source data are publicly available from the national statistics cited in the Methods. The processed analytic data are available from the author on reasonable request."
def code_statement(): return f"The analysis code and the scripts that generate every number, table and figure are archived on Zenodo (https://doi.org/{ZENODO}); during peer review the files are restricted and a private link has been provided to the editorial office, and they will be made public on publication."
def read_draft():
    md = open(DRAFT, encoding="utf-8").read(); md = re.sub(r"<!--.*?-->", "", md, flags=re.S); S = {}; cur = None
    for line in md.split("\n"):
        m = re.match(r"^## (.+)$", line)
        if m: cur = m.group(1).strip(); S[cur] = []; continue
        if cur is not None: S[cur].append(line)
    return {k: [p.strip() for p in "\n".join(v).split("\n\n") if p.strip()] for k, v in S.items()}
def pandoc_cites(t): return re.sub(r"\s*\[(@[^\]]+)\]", lambda m: " {{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
def strip(t): return re.sub(r"\{\{[^}]+\}\}|<[^>]+>", "", re.sub(r"\s*\[@[^\]]+\]", "", t))
def all_keys():
    src = open(os.path.join(HERE, "content_livd.py"), encoding="utf-8").read() + open(DRAFT, encoding="utf-8").read()
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S); src = re.sub(r"(?m)^\s*#.*$", "", src)
    return sorted(k for k in {k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")} if re.fullmatch(r"(web:)?[a-z][a-z0-9]*", k))
KEYS = all_keys()

KEEP = {"South", "Republic", "Korea", "Korean", "Bayesian", "United", "States", "US", "U.S.", "Gaussian", "Laplace", "Poisson", "Japan", "Japanese", "Taiwan", "China", "Chinese", "England", "Australia", "Brazilian", "Canada", "Canadian", "Pennsylvania", "Georgia",
        "Alabama", "North", "Carolina", "Asia-Pacific", "Asia", "Pacific", "Nilsson's", "E-Value", "Haddon", "Shanghai", "Iran", "Latin", "America", "UK", "Canada", "British", "Columbia", "Nonmetropolitan", "STROBE", "Statement", "Kanagawa", "Tokyo", "DC"}
def sent(t):   # 참고문헌 제목 문장형 통일(13호 ALZ sent 복제): 첫 단어·고유명사·약어 유지
    w = t.split(" "); caps = sum(1 for x in w[1:] if x[:1].isupper())
    if len(w) < 4 or caps < 0.5 * (len(w) - 1): return t
    out = [w[0]]
    for x in w[1:]:
        core = x.strip("(),:;.?")
        keep = core in KEEP or core.isupper() or any(c.isdigit() for c in core) or out[-1].endswith((":", "?")) or (core.split("-")[0] in KEEP)
        if not keep: x = x[:1].lower() + x[1:]
        x = "-".join([x.split("-")[0]] + [y if (y in KEEP or y.isupper()) else y[:1].lower() + y[1:] for y in x.split("-")[1:]])
        out.append(x)
    t2 = " ".join(out)
    for ph in ("Global Burden of Disease Study", "Community Health Survey", "E-value", "Nilsson's Power Model"): t2 = re.sub(re.escape(ph), ph, t2, flags=re.I)
    return t2.replace("E-Value", "E-value")
def ref(k):   # Vancouver: 저자 6명 이하 전원, 7명 이상 6명+et al. 제목. 약어 학술지. 연도;권:쪽. https://doi.org/
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. {r['title']}. {r['year']}. {r['url']}. Accessed {r['accessed']}."
    au = r["authors"]; a = ", ".join(au) if len(au) <= 6 else ", ".join(au[:6]) + ", et al."
    t = sent(r["title"].rstrip(".")); t = t + ("" if t.endswith(("?", "!")) else ".")
    a = re.sub(r"\b([A-Z][a-z]+) ([A-Z][a-z])$", lambda m: m.group(1) + " " + m.group(2).upper(), a) if False else a
    a = ", ".join(re.sub(r"^([A-Z][a-z]+) ([A-Z])([a-z])$", lambda m: f"{m.group(1)} {m.group(2)}{m.group(3).upper()}", x) for x in a.split(", "))   # PubMed 대문자 이름 title() 부작용("Moran Pa") 교정
    s_ = f"{a}{'' if a.endswith('.') else '.'} {t} {r['journal']}. {r['year']}"
    if r.get("vol"): s_ += f";{r['vol']}"
    if r.get("pages"): s_ += f":{r['pages']}"
    return s_ + (f". https://doi.org/{r['doi']}" if r.get("doi") else "")

class TX(JKMS):
    raw = False
    def save(self, path):   # 줄번호 유지, 머리·바닥글 문단은 줄번호 제외(10호 MHPA 방식)
        for s_ in self.doc.sections:
            for part in (s_.header, s_.footer, s_.first_page_header, s_.first_page_footer):
                for p in part.paragraphs:
                    pPr = p._p.get_or_add_pPr()
                    if pPr.find(qn("w:suppressLineNumbers")) is None: pPr.append(OxmlElement("w:suppressLineNumbers"))
        return super().save(path)
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw:
            text = re.sub(r"(^|[\s(])-(?=\d)", "\\1\u2212", text)   # brit = 항등(미국식), 음수는 U+2212
        return super()._emit(p, text, sz, bold, italic)

TAB1_COV = [("pop80_share", "Population aged 80 years or older, %"), ("urban_population_share", "Urban population share, %"),
            ("hcv_notification_rate_log", "Hepatitis C notifications, log per 100,000 person-years<sup>c</sup>"), ("alcohol_venues_per10k", "Entertainment and singing bars per 10,000"),
            ("high_risk_drinking_rate", "High-risk drinking, %"), ("screening_abdominal_obesity_share", "Abdominal obesity at screening, %"), ("screening_diabetes_suspected_share", "Suspected diabetes at screening, %"),
            ("current_smoking_rate", "Current smoking, %"), ("walking_practice_rate", "Walking practice, %"), ("moderate_pa_rate", "Moderate-or-vigorous physical activity, %"),
            ("public_sports_facilities_per_100k", "Public sports facilities per 100,000"), ("im_specialists_per_100k", "Internal medicine specialists per 100,000"), ("basic_livelihood_rate", "Basic livelihood recipients, %")]
def table1(dot=False):
    T = N["T1"]; cols = ["W1_2011-15", "W2_2016-19", "W3_2020-24", "2011-2024"]
    rows = [["__H__", "Deaths"],
            ["  District-years, n"] + [f"{T[c]['n']:,}" for c in cols],
            ["  Deaths, n"] + [f"{T[c]['cases']:,}" for c in cols],
            ["  Person-years, million"] + [f"{T[c]['py']/1e6:.1f}" for c in cols],
            ["  Crude rate per 100,000"] + [f"{T[c]['crude']:.1f}" for c in cols],
            ["  Age-standardized rate per 100,000<sup>a</sup>"] + [f"{T[c]['asr']:.1f}" for c in cols],
            ["  District SMR, median<sup>b</sup>"] + [f"{T[c]['sir_med']:.2f}" for c in cols],
            ["  District SMR, 10th-90th percentile<sup>b</sup>"] + [f"{T[c]['sir_p10']:.2f}-{T[c]['sir_p90']:.2f}" for c in cols],
            ["__H__", "District characteristics, mean (standard deviation)"]]
    for v, lab in TAB1_COV:
        mx = max(abs(T[c]['cov'][v][0]) for c in cols); dp = 0 if mx >= 100 else (2 if mx < 5 else 1)
        rows.append([f"  {lab}"] + [f"{T[c]['cov'][v][0]:,.{dp}f} ({T[c]['cov'][v][1]:,.{dp}f})" for c in cols])
    foot = (f"<sup>a</sup>Direct standardization to the 2015 national population in seventeen 5-year age groups and an open-ended group aged 85 years or older; window values are means of annual rates ({N['asr_2011']:.1f} in 2011 and {N['asr_2024']:.1f} in 2024). "
            "<sup>b</sup>Observed over indirectly age-standardized expected deaths summed over the window. "
            "<sup>c</sup>Notifications over 2017-2024, constant within district. Liver diseases, International Classification of Diseases, 10th revision, K70-K76. SMR, standardized mortality ratio.")
    return (("Table 1. " if dot else "Table 1 ") + "Liver disease deaths and district characteristics by calendar window, 3,206 district-years in Korea, 2011-2024", ["Characteristic", "2011-2015", "2016-2019", "2020-2024", "2011-2024"], rows, foot)

GROUPS = [("Hepatitis C and alcohol", ["hcv_notification_rate_log", "alcohol_venues_per10k", "high_risk_drinking_rate"]),
          ("Metabolic dysfunction and smoking", ["screening_abdominal_obesity_share", "screening_diabetes_suspected_share", "current_smoking_rate"]),
          ("Physical activity", ["walking_practice_rate", "moderate_pa_rate", "public_sports_facilities_per_100k"]),
          ("Care capacity and deprivation", ["im_specialists_per_100k", "basic_livelihood_rate"]),
          ("Forced controls", ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"])]
LABEL = {"hcv_notification_rate_log": "Hepatitis C notifications (log)", "alcohol_venues_per10k": "Entertainment and singing bars", "high_risk_drinking_rate": "High-risk drinking",
         "screening_abdominal_obesity_share": "Abdominal obesity at screening", "screening_diabetes_suspected_share": "Suspected diabetes at screening", "current_smoking_rate": "Current smoking",
         "walking_practice_rate": "Walking practice", "moderate_pa_rate": "Moderate-or-vigorous physical activity", "public_sports_facilities_per_100k": "Public sports facilities",
         "im_specialists_per_100k": "Internal medicine specialists", "basic_livelihood_rate": "Basic livelihood recipients", "urban_population_share": "Urban population share",
         "physicians_per_1000": "Physicians per 1,000", "sex_ratio": "Sex ratio", "fiscal_independence": "Fiscal autonomy", "pop80_share": "Population aged 80 years or older"}
BEST_KH = C.BEST
from decimal import Decimal, ROUND_HALF_UP
_pct = lambda f: str(int(Decimal(str(round(100 * f, 6))).quantize(Decimal("1"), rounding=ROUND_HALF_UP)))
def table2(dot=False):
    rows = []; assert sum(len(v) for g, v in GROUPS[:-1]) == N["n_hyp"] and set(LABEL) == set(N["main"])
    for g, vs in GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            m = N["main"][v]; mv = N["mv"].get(v); k = N["s43"][(BEST_KH, v)]
            rows.append([f"  {LABEL[v]}", f"{m['IRR']:.3f} ({m['lo']:.3f}-{m['hi']:.3f})", _pct(mv["cred_frac"]) if mv else "–", f"{k[0]:.3f} ({k[1]:.3f}-{k[2]:.3f})"])
    foot = (f"RR, rate ratio per 1 standard deviation; CrI, credible interval. Principal model, negative binomial with a Besag-York-Mollié 2 district effect and random-walk and independent year effects (n={N['n_rows']:,} district-years); all 11 district characteristics and five forced controls are shown. Bounds shown as 1.000 were classified from unrounded values. "
            f"<sup>a</sup>Share of the 200 covariate-subset fits containing the characteristic in which the CrI excluded 1; –, forced into every fit. "
            f"<sup>b</sup>Principal model plus a Knorr-Held type II space-time interaction (district-specific trends), which had the lowest WAIC of the four interaction types, with WAIC {abs(C.dW(BEST_KH)):,.0f} lower than the principal model.")
    return (("Table 2. " if dot else "Table 2 ") + "District characteristics and age-standardized liver disease mortality in Korea, 2011-2024, in the principal and type II space-time interaction models", ["Characteristic", "Principal RR\n(95% CrI)", "Subsets\ncredible, %<sup>a</sup>", "Type II RR\n(95% CrI)<sup>b</sup>"], rows, foot)

FIGCAP = {
 1: "Residual geography and national trend of liver disease mortality in Korea, 2011-2024. (A) Residual spatial rate ratio by district, the exponentiated posterior mean of the Besag-York-Mollié 2 district effect from the principal model, that is, the district mortality ratio not explained by the covariates. Solid outlines, hot spots (posterior probability of a residual spatial rate ratio above 1 greater than 0.95); dashed outlines, cold spots (probability below 0.05). Map lines delineate study areas and do not necessarily depict accepted national boundaries. (B) Crude and directly age-standardized (2015 population) liver disease death rates per 100,000",
 2: "Rate ratios per 1 standard deviation with 95% credible intervals for the seven subset-stable characteristics, Korea, 2011-2024, from the principal model; principal model with Knorr-Held type II and type IV space-time interactions; principal model with fixed effects for district type (urban ward, city, county); between-district (district mean) and within-district (two-way-centered deviation) components; and the same model fitted to deaths from chronic lower respiratory diseases (CLRD) and Alzheimer disease as comparison outcomes. The hepatitis C notification rate is constant within districts and has no within-district component",
}
ABBR = "BYM2, Besag-York-Mollié 2; CLRD, chronic lower respiratory diseases; CrI, credible interval; RR, rate ratio; SD, standard deviation; SMR, standardized mortality ratio; WAIC, widely applicable information criterion."
def foot_row(J, text, sz=9, ls=15):
    from docx.enum.text import WD_LINE_SPACING
    t = J.doc.tables[-1]; r = t.add_row(); m = r.cells[0].merge(r.cells[-1]); m.text = ""; p = m.paragraphs[0]
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(ls); p.paragraph_format.space_before = Pt(4)
    c = J.counting; J.counting = False; J._emit(p, text, sz); J.counting = c
def put_table(J, t, fs=9):
    c = J.counting; J.counting = False; J.table_fit(t[0], t[1], t[2], "", fs_max=fs, title_bold=False); foot_row(J, t[3], 8); J.counting = c
def put_fig(J, k, width_cm=16.0):
    from docx.enum.text import WD_BREAK
    p = J.doc.add_paragraph(); p.add_run().add_break(WD_BREAK.PAGE); p.add_run().add_picture(os.path.join(HERE, "figs", f"LIVD_Fig{k}.png"), width=Cm(width_cm))   # 쪽 나눔을 그림 문단 안 run으로(page_break는 다음 문단에 붙음)
    J.para(f"<b>Figure {k}.</b> {FIGCAP[k]}.", before=6)

def docx_bw_between(path, start, end):   # 본문 단어 수: start 제목(없으면 약어 목록 다음 쪽 첫 문단) ~ end 제목 직전, 표·그림 제외
    from docx import Document
    ps = [x.text for x in Document(path).paragraphs]
    i = ps.index(start.strip()) if start else ps.index("Abbreviations") + 2
    j = ps.index(end.strip())
    return len("\n".join(ps[i:j]).split())
def fix_orphans(path, heads, max_iter=8):
    from docx import Document
    for _ in range(max_iter):
        pdf = path.replace(".docx", ".pdf")
        subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_livd_ms", "--convert-to", "pdf", "--outdir", os.path.dirname(path), path], check=True, capture_output=True)
        pages = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout.split("\f"); orphan = None
        for pg in pages:
            ls = [re.sub(r"^\d+\s+", "", l.strip()) for l in pg.split("\n") if l.strip()]; ls = [l for l in ls if not re.fullmatch(r"\d+", l)]
            if ls and ls[-1] in heads: orphan = ls[-1]; break
        if orphan is None: return
        d = Document(path)
        for p in d.paragraphs:
            if p.text.strip() == orphan:
                r = OxmlElement("w:r"); br = OxmlElement("w:br"); br.set(qn("w:type"), "page"); r.append(br); p._p.insert(1 if p._p.pPr is not None else 0, r); break
        d.save(path); print("orphan fixed:", orphan)

