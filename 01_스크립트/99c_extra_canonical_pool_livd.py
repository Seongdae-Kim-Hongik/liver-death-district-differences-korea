#!/usr/bin/env python3
# 99c — 간질환 사망(LIVD, K70-K76) 가설 풀용 추가 열(2026-11-08). 99b·99c_*는 건드리지 않고 같은 결합 규칙(코드표, 이름 결합 금지, 군위군 37310 별칭)만 복제.
#  정본 통합자료(통합자료_261030):
#   im_specialists_per100k   = 내과 전문의 수 ÷ 정본 인구 × 10만 — 간질환 진료 역량(소화기내과 포함, 세부 전공 지표 없음)
#   basic_livelihood_rate    = 국민기초생활보장 수급자 비율(%) — 박탈(창원 2021-23 입력 오류 3칸 보간, 99c_strk와 같은 처리)
#   alcohol_venues_per10k    = (유흥주점 + 단란주점) 영업 중 업소 ÷ 인구 × 1만 — 주류 접근성(인허가 자료)
#   breakfast_eating_rate    = 아침식사율(%) — 음성대조
#  KDCA 법정감염병(age_final.parquet, 시군구×연도×성×연령):
#   hcv_notif_rate_log       = log(2017-2024 C형간염 신고 누계 ÷ 같은 기간 인구 합 × 10만) — 시군구 C형간염 부담(전수 신고 2017.6부터) → 시간 불변 지표로 전 연도에 둔다
#  MASTER 건강검진(chk):
#   dm_suspect_share         = 질환의심 당뇨병 ÷ 검진 수검 × 100 — 측정 혈당 기반(이미 치료 중인 유질환자 제외)
#   liver_suspect_share      = 질환의심 간장질환 ÷ 검진 수검 × 100 — 민감도 전용(간 손상 = 결과 경로의 중간 단계)
#  산출: 02_패널/EXT_canonical_pool_LIVD_261108.csv
import os, unicodedata
import numpy as np, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ZR = os.environ.get("ST_FBDZIP_ROOT", os.path.join(os.path.expandvars("$ST_DATA_ROOT"), "기타/R_Studio/FBD_DATA_ZIP"))
ZD = os.environ.get("ST_CANON", os.path.join(ZR, "통합자료_261030"))
C = pd.read_csv(os.path.join(ZD, "01_공변량_229x2011_2024.csv"), encoding="utf-8-sig", dtype={"sigungu_cd": str})
K = pd.read_csv(os.path.join(ZD, "00_시군구_229_대응표.csv"), encoding="utf-8-sig", dtype={"sigungu_cd": str}); assert K.sigungu_cd.is_unique and len(K) == 229
K.loc[K.sigungu_cd == "37310", "region"] = "대구시군위군"
C = C.drop(columns=["region"]).merge(K[["sigungu_cd", "region"]], on="sigungu_cd", how="left", validate="many_to_one"); assert C.region.notna().all()
pop = C["pop"].astype(float); assert pop.gt(0).all()
bars = C.lic_entertainment_bars_open.astype(float) + C.lic_singing_bars_open.astype(float)
out = pd.DataFrame({"year": C.year, "sigungu_cd": C.sigungu_cd, "fbd_region": C.region.map(NFC),
                    "im_specialists_per100k": C.internal_medicine_specialists.astype(float) / pop * 1e5,
                    "basic_livelihood_rate": C.basic_livelihood_recipient_rate.astype(float),
                    "alcohol_venues_per10k": bars / pop * 1e4,
                    "breakfast_eating_rate": C.breakfast_eating_rate.astype(float)})
out = out[(out.year >= 2011) & (out.year <= 2024)].copy()
bad = (out.fbd_region == NFC("경상남도창원시")) & out.year.isin([2021, 2022, 2023])
assert bad.sum() == 3; print("[99c-livd] 창원 2021-23 수급률 원값", out.loc[bad, "basic_livelihood_rate"].round(2).tolist(), "→ 결측 후 보간")
out.loc[bad, "basic_livelihood_rate"] = np.nan
# ── C형간염 신고율(KDCA, 코드 결합) ──
A = pd.read_parquet(os.path.join(ZR, "Foodborn Disease 5", "질병관리청데이터_v2026", "age_final.parquet"), columns=["sigungu_cd", "year", "disease", "cases"])
A = A[(A.disease == "C형간염") & A.year.between(2017, 2024)]; A["sigungu_cd"] = A.sigungu_cd.astype(str)
hc = A.groupby("sigungu_cd").cases.sum()
pp = out[out.year.between(2017, 2024)].groupby("sigungu_cd").year.apply(lambda g: float(C.loc[g.index, "pop"].astype(float).sum()))
assert set(hc.index) <= set(pp.index), set(hc.index) - set(pp.index)
rate = (hc.reindex(pp.index).fillna(0) / pp * 1e5)
print(f"[99c-livd] C형간염 2017-24 신고 {int(hc.sum()):,}건, 시군구 연 10만 명당 중앙값 {rate.median():.1f} (P10 {rate.quantile(.1):.1f}, P90 {rate.quantile(.9):.1f}), 0건 {int((rate==0).sum())}곳")
assert (rate > 0).all(), "0건 시군구 → log 불가"
out["hcv_notif_rate_log"] = out.sigungu_cd.map(np.log(rate))
# ── 검진 비율(MASTER chk, fbd_region 결합 — 같은 체육 패널 키) ──
M = pd.read_parquet(os.path.join(ROOT, "02_패널", "MASTER_시군구_연도_wide.parquet"), columns=["year", "fbd_region", "chk__검진수검", "chk__질환의심_고혈압당뇨_당뇨병", "chk__질환의심_간장질환"])
M["fbd_region"] = M.fbd_region.map(NFC); M = M[M.year.between(2011, 2024)]
M["dm_suspect_share"] = 100 * M["chk__질환의심_고혈압당뇨_당뇨병"] / M["chk__검진수검"]
M["liver_suspect_share"] = 100 * M["chk__질환의심_간장질환"] / M["chk__검진수검"]
out = out.merge(M[["year", "fbd_region", "dm_suspect_share", "liver_suspect_share"]], on=["year", "fbd_region"], how="left", validate="one_to_one")
assert out.groupby("fbd_region").year.nunique().eq(14).all() and out.fbd_region.nunique() == 229 and not out.duplicated(["year", "fbd_region"]).any()
out = out.sort_values(["fbd_region", "year"])
for c in ["basic_livelihood_rate", "im_specialists_per100k", "alcohol_venues_per10k", "breakfast_eating_rate", "dm_suspect_share", "liver_suspect_share"]:
    n0 = int(out[c].isna().sum()); out[c] = out.groupby("fbd_region")[c].transform(lambda s: s.interpolate(method="linear", limit_area="inside"))
    n1 = int(out[c].isna().sum())
    if n1:   # 80의 extra_columns는 결측을 받지 않음 → 80과 같은 규칙(시군구 평균 → 연도 전국 평균)으로 미리 채움
        print(f"[99c-livd]   {c} 남은 결측 지역·연도:", out[out[c].isna()][["fbd_region", "year"]].values.tolist())
        out[c] = out[c].fillna(out.groupby("fbd_region")[c].transform("mean")).fillna(out.groupby("year")[c].transform("mean"))
    print(f"[99c-livd] {c}: 결측 {n0} → 안쪽 보간 후 {n1} → 채움 후 {int(out[c].isna().sum())}")
for c in ["im_specialists_per100k", "alcohol_venues_per10k", "dm_suspect_share", "liver_suspect_share"]:
    print(f"[99c-livd] {c} 연도 중앙값", out.groupby("year")[c].median().round(2).to_dict())
P = pd.read_csv(os.path.join(ROOT, "04_분석", "LIVD", "panel_LIVD.csv"), encoding="utf-8-sig", usecols=["year", "fbd_region"]); P["fbd_region"] = P.fbd_region.map(NFC)
assert set(P.fbd_region) == set(out.fbd_region), "체육 패널 지역과 불일치"
fp = os.path.join(ROOT, "02_패널", "EXT_canonical_pool_LIVD_261108.csv"); out.drop(columns=["sigungu_cd"]).to_csv(fp, index=False, encoding="utf-8-sig")
print(f"[99c-livd] 저장 {fp} {out.shape}; 결측 {out.isna().sum().to_dict()}")
