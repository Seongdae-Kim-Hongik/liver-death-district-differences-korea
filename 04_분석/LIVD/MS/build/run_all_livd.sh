#!/bin/bash
# run_all_livd.sh — 간질환 사망 CRHG 전체 빌드(2026-11-19). 그림은 기존 figs 산출물 재사용.
set -e; cd "$(dirname "$0")"
python3 figs_livd.py 2>&1 | grep -v Warning
python3 build_crhg_livd.py
python3 esm_livd.py
python3 cover_crhg_livd.py ${COVER_DRAFT:+--draft}
python3 sanitize_docx.py --no-anon ../out/Manuscript_CRHG_LIVD.docx ../out/Supplementary_Material_CRHG_LIVD.docx ../out/Cover_Letter_CRHG_LIVD.docx ../out/Highlights_CRHG_LIVD.docx ../out/Declaration_of_Interests_CRHG_LIVD.docx
for f in ../out/Supplementary_Material_CRHG_LIVD.docx ../out/Manuscript_CRHG_LIVD.docx; do /opt/homebrew/bin/soffice --headless -env:UserInstallation=file:///tmp/lo_livd_pdf --convert-to pdf --outdir ../out "$f" >/dev/null 2>&1; done
