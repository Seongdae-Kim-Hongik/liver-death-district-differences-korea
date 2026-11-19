# build_crhg_livd.py — 간질환 사망 Clinics and Research in Hepatology and Gastroenterology(Elsevier Masson) 원고 조립(2026-11-19).
#  규정(ScienceDirect Guide for authors, 11/19 크롬 열람): Original article ≤4,000단어(그림·표 범례 포함), 참고문헌 ≤100, 단일 익명(제목면은 원고 1쪽),
#  구조 초록 ≤250(적절한 소제목), 키워드 1-7, Highlights 3-5개 ≤85자(별도 편집 파일, 파일명에 highlights), 번호 인용 [n] 등장 순, 6명 초과 6명+et al., 끝쪽 축약(51-9),
#  학술지 약어 LTWA, DOI 링크. 경쟁이익 = declarations tool Word 파일 업로드, 연구비 표준 문장, CRediT, 감사의 글은 참고문헌 바로 앞,
#  생성형 AI 고지 = 참고문헌 앞 별도 절(정해진 제목·문장), 지도 = 'map lines delineate study areas…' 문구. 표는 편집 가능 텍스트·세로선 없음, 그림은 별도 파일.
import os, re
from build_common_livd import (C, N, REFS, read_draft, pandoc_cites, strip, KEYS, sent, TX, table1, table2, put_table, FIGCAP, ABBR, docx_bw_between, fix_orphans,
                               TITLE, ORCID, AFFIL, ADDRESS, IRB, CONSENT, OUT, ZENODO)
REPO = "Seongdae-Kim-Hongik/liver-death-district-differences-korea"
FUNDING = "This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors."
CREDIT = "Seongdae Kim: Conceptualization, Data curation, Formal analysis, Investigation, Methodology, Software, Validation, Visualization, Writing – original draft, Writing – review and editing."
COI = "The author declares no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper."
AI_HEAD = "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process"
AI_STATEMENT = ("During the preparation of this work the author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript. "
                "After using these tools, the author reviewed and edited the content as needed and takes full responsibility for the content of the published article.")
HIGHLIGHTS = ["Liver disease deaths were mapped across 229 Korean districts over 14 years",
              "Hepatitis C notifications marked districts with excess liver disease deaths",
              "Deprivation and smoking were also associated in all space-time models",
              "Survey high-risk drinking was not associated with district liver deaths",
              "High hepatitis C burden districts are candidates for case finding"]
assert 3 <= len(HIGHLIGHTS) <= 5 and all(len(h) <= 85 for h in HIGHLIGHTS), [len(h) for h in HIGHLIGHTS]
ABS_HEADS = {"Aims": "Background and aims"}

def data_statement():
    return ("All source data are publicly available aggregate national statistics, listed in the Methods. The processed district-year analytic data are available from the author on reasonable request. "
            f"The analysis code and the scripts that generate every number, table and figure are openly available on Zenodo (https://doi.org/{ZENODO}) and GitHub (https://github.com/{REPO}) under the MIT license.")

def pages_short(p):   # 51-59 -> 51-9 (가이드 예시)
    m = re.fullmatch(r"(\d+)-(\d+)", p or "")
    if not m: return p or ""
    a, b = m.groups()
    if len(a) == len(b):
        i = 0
        while i < len(a) - 1 and a[i] == b[i]: i += 1
        b = b[i:]
    return f"{a}-{b}"
def ref_crhg(k):   # Elsevier numbered(ICMJE): 6명 이하 전원, 7명 이상 6명+et al. 제목. 약어지 연도;권:쪽. https://doi.org/
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. {r['title']}. {r['year']}. {r['url']} [accessed {r['accessed']}]."
    au = [re.sub(r"^([A-Z][a-z]+) ([A-Z])([a-z])$", lambda m: f"{m.group(1)} {m.group(2)}{m.group(3).upper()}", x) for x in r["authors"]]
    a = ", ".join(au) if len(au) <= 6 else ", ".join(au[:6]) + ", et al"
    t = sent(r["title"].rstrip(".")); t = t + ("" if t.endswith(("?", "!")) else ".")
    s_ = f"{a}{'' if a.endswith('.') else '.'} {t} {r['journal'].replace('.', '')} {r['year']}"
    if r.get("vol"): s_ += f";{r['vol']}"
    if r.get("pages"): s_ += f":{pages_short(r['pages'])}"
    return s_ + (f". https://doi.org/{r['doi']}." if r.get("doi") else ".")

def abstract_paras(D):
    out = []
    for p in D["Abstract"]:
        m = re.match(r"^<b>([^<]+):</b>\s*(.*)$", p); h = ABS_HEADS.get(m.group(1), m.group(1)); out.append(f"<b>{h}:</b> {m.group(2)}")
    return out

def legend_words():   # 그림 범례 + 표 제목·주석(범례 포함 한도 계산용)
    t1, t2 = table1(dot=True), table2(dot=True)
    return sum(len(strip(x).split()) for x in (FIGCAP[1] + ".", FIGCAP[2] + ".", t1[0], t1[3], t2[0], t2[3])) + 4

def build(bw=0, aw=0, lw=0):
    D = read_draft(); J = TX(cite="bracket")
    J.para(f"<b>{TITLE}</b>")
    J.para("Seongdae Kim<sup>a</sup>", before=6)
    J.para(f"<sup>a</sup>{AFFIL.replace('Seoul, Republic of Korea', '94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea')}")
    J.para(f"<b>Corresponding author:</b> Seongdae Kim, {ADDRESS}. E-mail: kimsd@hongik.ac.kr. ORCID: {ORCID}", before=6)
    J.para(f"<b>Word count:</b> {bw + lw:,} words including figure and table legends (main text {bw:,}; legends and table notes {lw}); abstract {aw} words. <b>Tables and figures:</b> 2 tables and 2 figures. <b>References:</b> {len(KEYS)}.", before=6)
    J.page_break(); J.head("Abstract", 1)
    for p in abstract_paras(D): J.para(p)
    J.para(f"<b>Keywords:</b> {C.KEYWORDS}", before=6)
    J.head("Abbreviations", 1); J.para(ABBR)
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in D["Introduction"]: J.para(pandoc_cites(p), indent=True)
    J.head("Methods", 1)
    for h, p in C.METHODS: J.head(h, 2); J.para(pandoc_cites(p), indent=True)
    J.head("Results", 1)
    for h, p in C.RESULTS:
        if h: J.head(h, 2)
        J.para(pandoc_cites(p), indent=True)
    J.head("Discussion", 1)
    for p in D["Discussion"]:
        if p.startswith("### "): J.head(p[4:].strip(), 2); continue
        J.para(pandoc_cites(p), indent=True)
    J.counting = False
    for h, t in (("Ethics statement", IRB + " " + CONSENT), ("Funding", FUNDING), ("Declaration of competing interest", COI),
                 ("CRediT authorship contribution statement", CREDIT), ("Data availability", data_statement()), (AI_HEAD, AI_STATEMENT), ("Acknowledgements", "None.")):
        J.head(h, 1); J.para(t)
    assert sorted(J.cites) == KEYS, (set(J.cites) ^ set(KEYS))
    J.page_break(); J.head("References", 1); J.raw = True; rl = []
    for i, k in enumerate(J.cites, 1): s_ = f"[{i}] " + ref_crhg(k); rl.append(s_); J.para(s_)
    J.raw = False
    J.page_break(); put_table(J, table1(dot=True))
    J.page_break(); put_table(J, table2(dot=True))
    J.page_break(); J.head("Figure legends", 1)
    for k in (1, 2): J.para(f"<b>Figure {k}.</b> {FIGCAP[k]}.", before=6)
    return J, rl, D

def highlights():
    K = TX(cite="bracket"); K.para("<b>Highlights</b>")
    for h in HIGHLIGHTS: K.para("• " + h)
    K.doc_title = "Highlights"; K.save(os.path.join(OUT, "Highlights_CRHG_LIVD.docx"))

def declaration():
    from docx import Document
    from docx.shared import Pt
    d = Document(); st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11)
    d.add_paragraph().add_run("Declaration of interests").bold = True
    d.add_paragraph(f"Manuscript title: {TITLE}")
    d.add_paragraph("☒ The author declares no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.")
    d.add_paragraph("☐ The author declares the following financial interests/personal relationships which may be considered as potential competing interests: none.")
    d.add_paragraph("Seongdae Kim, PhD, Hongik University, Seoul, Republic of Korea")
    d.core_properties.author = "Seongdae Kim"; d.core_properties.last_modified_by = "Seongdae Kim"; d.core_properties.title = "Declaration of interests"; d.core_properties.comments = ""
    d.save(os.path.join(OUT, "Declaration_of_Interests_CRHG_LIVD.docx"))

if __name__ == "__main__":
    p = os.path.join(OUT, "Manuscript_CRHG_LIVD.docx"); D = read_draft()
    aw = len(strip(" ".join(abstract_paras(D))).split()); assert aw <= 250, aw
    assert len(KEYS) <= 100 and 1 <= len(C.KEYWORDS.split(";")) <= 7
    lw = legend_words()
    J, rl, D = build(); J.doc_title = "Manuscript"; J.save(p); bw = docx_bw_between(p, "Introduction", "Ethics statement"); assert bw + lw <= 4000, (bw, lw)
    J, rl, D = build(bw, aw, lw); J.doc_title = "Manuscript"; J.save(p); assert docx_bw_between(p, "Introduction", "Ethics statement") == bw
    heads = {"Abstract", "Abbreviations", "Introduction", "Methods", "Results", "Discussion", "References", "Ethics statement", "Funding", "Declaration of competing interest",
             "CRediT authorship contribution statement", "Data availability", AI_HEAD, "Acknowledgements", "Figure legends"}
    heads |= {x[4:].strip() for x in D["Discussion"] if x.startswith("### ")} | {h for h, _ in C.METHODS + C.RESULTS if h}
    fix_orphans(p, heads)
    highlights(); declaration()
    open(os.path.join(OUT, "wordcount_crhg.txt"), "w").write(f"body_words={bw} legend_words={lw} total_words={bw+lw} abstract_words={aw} refs={len(rl)}\n")
    print("CRHG built", bw, lw, bw + lw, aw, len(rl))
