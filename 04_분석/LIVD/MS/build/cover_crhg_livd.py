# cover_crhg_livd.py — 간질환 사망 CRHG 커버레터. AI 고지는 원고 참고문헌 앞 절과 커버레터. 미국식, 1쪽, 단독 저자 비인칭.
import os, re, sys, datetime, subprocess
from docx import Document
from docx.shared import Pt, Cm
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import content_livd as C
from build_common_livd import TITLE as DTITLE, ZENODO, ADDRESS
brit = lambda t: t
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "out"); DRAFT = "--draft" in sys.argv
N = C.N; W = dict(l.split("=") for l in open(os.path.join(OUT, "wordcount_crhg.txt")).read().split()); M = N["main"]
assert all(M[v]["cred"] for v in C.CRED6) and not M[C.ALC]["cred"] and not M[C.BAR]["cred"] and not any(C.NCO(o, C.HCV)[3] for o in ("CLRD", "ALZ"))
_d = datetime.date.today(); cl = [f"{_d:%B} {_d.day}, {_d.year}", "The Editors", "Clinics and Research in Hepatology and Gastroenterology", "",
      "Dear Editor,",
      f"Please find enclosed the manuscript entitled \"{DTITLE}\" by Seongdae Kim, for consideration as an Original Article (Clinical-Liver section) in Clinics and Research in Hepatology and Gastroenterology.",
      f"Using complete national death registration for all {N['n_districts']} Korean districts over 14 years and Bayesian spatiotemporal models, this study describes the geography of liver disease mortality (ICD-10 K70-K76) and asks which district characteristics mark districts with excess deaths. The age-standardized rate fell until 2019 and did not decline further thereafter. District hepatitis C notification rates and deprivation, and less consistently smoking, were associated with excess mortality in all four space-time interaction models, whereas survey high-risk drinking was not associated and bar density only imprecisely. Hepatitis C notifications were not associated with two comparison causes of death. Associations with negative-control exposures indicate that residual confounding is likely and are reported as such.",
      "The findings are relevant to hepatology practice and planning: hepatitis C is curable, yet testing and treatment uptake in Korea lag behind elimination targets, and the districts where diagnosed hepatitis C burden and liver deaths coincide are candidates for case finding and linkage to antiviral treatment. The study used only published aggregate statistics with approval of the Institutional Review Board of Hongik University (7002340-202611-HR-040, continuing review of 7002340-202511-HR-012).",
      "The author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript. This manuscript reports unpublished work, is not under consideration for publication in whole or in part elsewhere and, if accepted, will not be published elsewhere in the same form, in English or any other language, without the consent of the Editors. The sole author meets the authorship criteria of the journal and agrees with the content of the manuscript.",
      f"The manuscript contains {int(W['total_words']):,} words including figure and table legends, with a structured abstract of {int(W['abstract_words'])} words, two tables, two figures and {W['refs']} references. Highlights and the Supplementary Material (supplementary methods, tables, figures and the STROBE checklist) are provided as separate files.",
      f"The analysis code is openly available on Zenodo (https://doi.org/{ZENODO}) under the MIT license.",
      "Thank you for considering this manuscript.", "", "Sincerely,", "",
      "Seongdae Kim, PhD (corresponding author)", ADDRESS, "Email: kimsd@hongik.ac.kr"]
d = Document(); st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11); st.paragraph_format.space_after = Pt(4); st.paragraph_format.line_spacing = 1.0
for s in d.sections: s.page_width, s.page_height = Cm(21), Cm(29.7); s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Cm(2.54)
LINK = ""
NOLINK = "--nolink" in sys.argv   # 11/6 9호: 심사 토큰을 확장 보안 필터 때문에 받을 수 없어, 저자 지시("계속 진행하라")로 요청 시 제공 문구 사용
assert DRAFT or "[ZENODO" not in ZENODO, "Zenodo DOI 없음(투고 전 게이트)"
def _add_link(p, url, text):
    rid = p.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), rid); r = OxmlElement("w:r"); rp = OxmlElement("w:rPr")
    c = OxmlElement("w:color"); c.set(qn("w:val"), "0563C1"); u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rp.append(c); rp.append(u); r.append(rp)
    tt = OxmlElement("w:t"); tt.text = text; r.append(tt); h.append(r); p._p.append(h)
gap = False
for t in cl:
    if t == "": gap = True; continue
    t = brit(t)
    if NOLINK and "[[LINK]]" in t: t = t.replace("editors and reviewers can open the record and download the code without an account through this private link: [[LINK]] ", "a private review link that gives editors and reviewers access without an account will be sent to the editorial office on request. ")
    if "[[LINK]]" in t:
        a, b = t.split("[[LINK]]"); p = d.add_paragraph(a)
        if LINK: _add_link(p, LINK, "Zenodo private review link")
        else: p.add_run("[REVIEW LINK]")
        p.add_run("." + b)
    else: p = d.add_paragraph(t)
    if gap: p.paragraph_format.space_before = Pt(10); gap = False
d.core_properties.author = "Seongdae Kim"; d.core_properties.last_modified_by = "Seongdae Kim"; d.core_properties.title = "Cover Letter"; d.core_properties.comments = ""
fp = os.path.join(OUT, "Cover_Letter_CRHG_LIVD.docx"); d.save(fp)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_livd_cl_crhg", "--convert-to", "pdf", "--outdir", OUT, fp], capture_output=True)
txt = subprocess.run(["pdftotext", fp.replace(".docx", ".pdf"), "-"], capture_output=True, text=True).stdout
assert not re.search(r"\b(we|our|us|I)\b", txt) and "—" not in txt and re.search(r"7002340-202611-?\s*HR-040", txt) and not re.search(r"(?i)funding|competing|overlap|previously submitted", txt), "문체·IRB·금지 항목"
pages = subprocess.run(["pdfinfo", fp.replace(".docx", ".pdf")], capture_output=True, text=True).stdout.split("Pages:")[1].split()[0]
assert pages == "1", pages; print("cover pages", pages, "draft" if DRAFT else "")
