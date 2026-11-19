# -*- coding: utf-8 -*-
# figs_livd.py — 간질환 사망 투고용 그림. 폭 174 mm, 조합 600 dpi·선화 1200 dpi, RGB, TIFF 별도 파일 Figure1·Figure2.
#  EJCP: 그림은 본문에 넣지 않고 TIFF 따로, Arial/Helvetica, 폭 166 mm(두 단), 선화 ≥1200 dpi → 1200 dpi RGB TIFF LZW. 그림 안 설명문 없음, 한글 없음.
#  Fig 1 (a) 전 기간 잔차 공간 RR 지도 (b) 조율·연령표준화율 추이 · Fig 2 강건 4개 변수의 모형별 RR · SDC 그림 (a) EHSA (b) 세 창 핫·콜드스팟 횟수
import os, unicodedata, numpy as np, pandas as pd, geopandas as gpd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
from numbers_livd import load, ROB, SHP
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(os.path.dirname(HERE)); RS = os.path.join(B, "results_std3")
FIG = os.path.join(HERE, "figs"); OUTF = os.path.join(os.path.dirname(HERE), "out", "Figures"); os.makedirs(FIG, exist_ok=True); os.makedirs(OUTF, exist_ok=True)
MM = 1 / 25.4; W = 174 * MM; DPI = 600; LW = 0.3
plt.rcParams.update({"font.family": "Arial", "font.size": 8, "legend.fontsize": 8, "legend.title_fontsize": 8, "axes.linewidth": 0.5, "pdf.fonttype": 42})
NFC = lambda s: unicodedata.normalize("NFC", str(s)).strip()
N = load()
G = gpd.read_file(SHP); G["cd"] = G.sigungu_cd.astype(str); G["sido"] = G.cd.str[:2]; SIDO = G.dissolve("sido")   # 결합은 시군구 코드(cd)로만, 이름 결합 금지
XL = (G.total_bounds[0], G.total_bounds[2]); YL = (G.total_bounds[1], G.total_bounds[3])
rd = lambda f: pd.read_csv(os.path.join(RS, f), encoding="utf-8-sig", dtype={"sigungu_cd": str})
def letter(ax, ch, dx=0.0, dy=None):   # 패널 문자: 대문자·모든 패널 같은 크기·56pt 볼드(11/10 규칙), 그림 맨 위 줄에 고정(잘림·겹침 방지), x는 패널 왼쪽 끝
    f = ax.figure; b = ax.get_position(); f.text(max(0.005, b.x0 + dx * b.width), 0.995, ch.upper(), fontsize=56, fontweight="bold", va="top", ha="left")
def mapax(ax):   # 06 §6-C: 북침 = 슬림 채움 삼각형 Polygon + "N"(annotate 화살표 금지), 축척 = 0-50-100 km 흑백 2단
    from matplotlib.patches import Polygon, Rectangle
    SIDO.boundary.plot(ax=ax, color="#404040", linewidth=0.45); ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_axis_off(); ax.set_aspect("equal")
    x0, x1 = XL; y0, y1 = YL; W_ = x1 - x0; H_ = y1 - y0   # 좌표 단위 m
    bx, by, bh = x0 + 0.60 * W_, y0 + 0.04 * H_, 0.010 * H_
    ax.add_patch(Rectangle((bx, by), 50000, bh, facecolor="black", edgecolor="black", lw=0.5)); ax.add_patch(Rectangle((bx + 50000, by), 50000, bh, facecolor="white", edgecolor="black", lw=0.5))
    for k, t, ha in ((0, "0", "center"), (50000, "50", "center"), (100000, " 100 km", "left")): ax.text(bx + k, by + bh + 0.008 * H_, t, ha=ha, va="bottom", fontsize=8)
    nx, ny, nw, nh = x0 + 0.95 * W_, y0 + 0.62 * H_, 0.054 * W_, 0.21 * H_   # 11/8 저자 규칙: 방위표 3배, 울릉·독도와 겹치지 않게
    ax.add_patch(Polygon([[nx - nw / 2, ny], [nx, ny + nh], [nx + nw / 2, ny], [nx, ny + 0.25 * nh]], closed=True, facecolor="black", edgecolor="black", lw=0.4))
    ax.text(nx, ny + nh + 0.012 * H_, "N", ha="center", va="bottom", fontsize=24, fontweight="bold")
def save(fig, k, dpi=DPI):   # 선화(forest plot, Fig 2)는 1200 dpi, 지도 혼합은 600 dpi
    p = os.path.join(FIG, f"LIVD_Fig{k}.png"); fig.savefig(p, dpi=dpi, facecolor="white"); plt.close(fig)   # 폭 166 mm 고정(bbox tight 쓰지 않음)
    im = Image.open(p).convert("RGB"); im.save(p, dpi=(dpi, dpi))
    if not str(k).startswith("S"): im.save(os.path.join(OUTF, f"Figure{k}.tif"), dpi=(dpi, dpi), compression="tiff_lzw")   # 보충 그림은 보충 PDF에만
    return im.size

# Fig 1
S6 = rd("S6_spatial_RR.csv"); assert len(S6) == 229
BR = [0, 0.8, 0.9, 0.95, 1, 1.05, 1.1, 1.2, 99]; LB = ["<0.80", "0.80-0.89", "0.90-0.94", "0.95-0.99", "1.00-1.04", "1.05-1.09", "1.10-1.19", "≥1.20"]
PAL = ["#2166AC", "#4393C3", "#92C5DE", "#D1E5F0", "#FDDBC7", "#F4A582", "#D6604D", "#B2182B"]
fig = plt.figure(figsize=(W, 5.0)); a0 = fig.add_axes([0.0, 0.15, 0.50, 0.62]); a1 = fig.add_axes([0.62, 0.27, 0.34, 0.46])
d = S6.set_index("sigungu_cd"); gg = G.copy(); gg["v"] = gg.cd.map(d.RR); gg["c"] = gg.cd.map(d["class"]); assert gg.v.notna().all()
gg.plot(ax=a0, column="v", cmap=ListedColormap(PAL), norm=BoundaryNorm(BR, len(PAL)), edgecolor="#a0a0a0", linewidth=LW); mapax(a0)
gg[gg.c == "coldspot"].boundary.plot(ax=a0, color="#2171B5", linewidth=0.6, linestyle=(0, (2.0, 1.2))); gg[gg.c == "hotspot"].boundary.plot(ax=a0, color="black", linewidth=0.6); letter(a0, "a")
h = [Patch(facecolor=c, edgecolor="#777777", linewidth=LW, label=l) for c, l in zip(PAL, LB)] + [Patch(facecolor="none", edgecolor="black", linewidth=0.8, label="Hot spot"), Patch(facecolor="none", edgecolor="#2171B5", linewidth=0.8, linestyle="--", label="Cold spot")]
a0.legend(handles=h, title="Residual spatial rate ratio", loc="upper center", bbox_to_anchor=(0.55, 0.0), ncol=4, frameon=False, columnspacing=0.8, handlelength=1.3)
yrs = sorted(N["asr"]); P = pd.read_csv(os.path.join(B, "panel_LIVD_std3.csv")); y = P.groupby("year")[["cases", "offset"]].sum(); cr = 1e5 * y.cases / y.offset
assert abs(cr[2011] - N["crude_2011"]) < 1e-6 and abs(cr[2024] - N["crude_2024"]) < 1e-6
a1.plot(yrs, [cr[t] for t in yrs], color="#404040", marker="o", ms=2.5, lw=0.9, label="Crude")
a1.plot(yrs, [N["asr"][t] for t in yrs], color="#b2182b", marker="s", ms=2.5, lw=0.9, label="Age-standardized")
assert max(max(cr), max(N["asr"].values())) < 18
a1.set_xticks([2011, 2014, 2017, 2020, 2024]); a1.set_ylim(0, 18); a1.set_ylabel("Deaths per 100,000"); a1.spines[["top", "right"]].set_visible(False); a1.legend(frameon=False, loc="lower left"); letter(a1, "b", dx=-0.22); a1.set_xlabel("Year")
s1 = save(fig, 1)

# SDC 그림
EH = rd("S11_ehsa.csv")
CATS = [f"{a} {b}" for b in ("hot", "cold") for a in ("New", "Consecutive", "Intensifying", "Persistent", "Diminishing", "Sporadic", "Oscillating", "Historical")] + ["No pattern"]
EPAL = {"New hot": "#fdd0a2", "Consecutive hot": "#fdae6b", "Intensifying hot": "#a50f15", "Persistent hot": "#de2d26", "Diminishing hot": "#fc9272", "Sporadic hot": "#fee0d2", "Oscillating hot": "#d6a5c9", "Historical hot": "#bcbddc",
        "New cold": "#c6dbef", "Consecutive cold": "#9ecae1", "Intensifying cold": "#08519c", "Persistent cold": "#3182bd", "Diminishing cold": "#6baed6", "Sporadic cold": "#deebf7", "Oscillating cold": "#a1d99b", "Historical cold": "#c7e9c0", "No pattern": "#f7f7f7"}
WM = rd("S4b_window_spatialRR.csv")
nh = WM[WM["class"] == "hotspot"].groupby("sigungu_cd").size(); nc = WM[WM["class"] == "coldspot"].groupby("sigungu_cd").size()
assert int((nh == 3).sum()) == N["hot_all_windows"] and int((nc == 3).sum()) == N["cold_all_windows"]
fig, (a0, a1) = plt.subplots(1, 2, figsize=(W, 5.0)); fig.subplots_adjust(left=0.01, right=0.99, top=0.78, bottom=0.27, wspace=0.04)
gg = G.copy(); gg["c"] = gg.cd.map(EH.set_index("sigungu_cd").EHSA); assert gg.c.notna().all()
gg.plot(ax=a0, color=[EPAL[c] for c in gg.c], edgecolor="#a0a0a0", linewidth=LW); mapax(a0); letter(a0, "a")
cnt = EH.EHSA.value_counts(); pres = [c for c in CATS if c in cnt.index]
a0.legend(handles=[Patch(facecolor=EPAL[c], edgecolor="#777777", linewidth=LW, label=f"{c} ({cnt[c]})") for c in pres], title="Category (districts)", loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False, columnspacing=0.8, handlelength=1.2)
hh = gg.cd.map(nh).fillna(0).astype(int); cc = gg.cd.map(nc).fillna(0).astype(int)
gg["k"] = np.where((hh > 0) & (cc > 0), 9, hh - cc)
KP = {-3: "#2166AC", -2: "#67A9CF", -1: "#D1E5F0", 0: "#f7f7f7", 1: "#FDDBC7", 2: "#EF8A62", 3: "#B2182B", 9: "#c2a5cf"}
KL = {-3: "Cold spot in 3 windows", -2: "Cold spot in 2", -1: "Cold spot in 1", 0: "Neither", 1: "Hot spot in 1", 2: "Hot spot in 2", 3: "Hot spot in 3 windows", 9: "Hot or cold by window"}
gg.plot(ax=a1, color=[KP[k] for k in gg.k], edgecolor="#a0a0a0", linewidth=LW); mapax(a1); letter(a1, "b")
kc = gg.k.value_counts()
a1.legend(handles=[Patch(facecolor=KP[k], edgecolor="#777777", linewidth=LW, label=f"{KL[k]} ({kc.get(k, 0)})") for k in (3, 2, 1, 0, -1, -2, -3, 9) if kc.get(k, 0)], title="Windows 2011-2015, 2016-2019, 2020-2024", loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False, columnspacing=0.8, handlelength=1.2)
s2 = save(fig, "S1")

# Fig 2 — 강건 7개 변수의 모형·성분별 RR + 비교 결과(만성하기도질환·알츠하이머 사망)
LAB = {"hcv_notification_rate_log": "Hepatitis C\nnotification rate (log)", "alcohol_venues_per10k": "Entertainment and\nsinging bars", "screening_diabetes_suspected_share": "Screening diabetes\nsuspected", "current_smoking_rate": "Current smoking",
       "moderate_pa_rate": "Moderate-or-vigorous\nphysical activity", "public_sports_facilities_per_100k": "Public sports\nfacilities", "basic_livelihood_rate": "Basic livelihood\nsecurity recipients"}
ORD = ["hcv_notification_rate_log", "alcohol_venues_per10k", "screening_diabetes_suspected_share", "current_smoking_rate", "basic_livelihood_rate", "public_sports_facilities_per_100k", "moderate_pa_rate"]; assert set(ORD) == set(ROB)
BEST = min(("KH_typeI", "KH_typeII", "KH_typeIII", "KH_typeIV"), key=lambda a: N["s43_waic"][a]); assert BEST == "KH_typeII"
def _bw(v, part):
    if v == "hcv_notification_rate_log" and part == "within": return (np.nan, np.nan, np.nan)   # 시간 불변 지표: 지역 내 성분 없음
    return N["bw"][v + "__" + part][:3]
MOD = [("Principal model", lambda v: (N["main"][v]["IRR"], N["main"][v]["lo"], N["main"][v]["hi"]), "#000000", "o"),
       ("Knorr-Held type II", lambda v: N["s43"][(BEST, v)][:3], "#B2182B", "D"),
       ("Knorr-Held type IV", lambda v: N["s43"][("KH_typeIV", v)][:3], "#F4A582", "d"),
       ("District type fixed effects", lambda v: N["s45"][("E_district_type", v)][:3], "#542788", "X"),
       ("Between-district component", lambda v: _bw(v, "between"), "#2166AC", "s"),
       ("Within-district component", lambda v: _bw(v, "within"), "#67A9CF", "v"),
       ("CLRD deaths (comparison)", lambda v: N["s41"][("H1_nco_CLRD", v)][:3], "#E08214", "P"),
       ("Alzheimer deaths (comparison)", lambda v: N["s41"][("H1_nco_ALZ", v)][:3], "#7f7f7f", "^")]
vals = [f(v) for v in ORD for _, f, _, _ in MOD]; lo_all = np.nanmin([x[1] for x in vals]); hi_all = np.nanmax([x[2] for x in vals])
fig, ax = plt.subplots(figsize=(W, 6.4)); fig.subplots_adjust(left=0.21, right=0.98, top=0.99, bottom=0.20)
off = np.linspace(-0.36, 0.36, len(MOD))
for i, v in enumerate(ORD):
    for (lab, f, col, mk), o in zip(MOD, off):
        e, lo, hi = f(v)
        if np.isnan(e): continue
        ax.plot([lo, hi], [i + o] * 2, color=col, lw=0.8); ax.plot(e, i + o, marker=mk, color=col, ms=3.4, mew=0, ls="none")
ax.axvline(1, color="#404040", lw=0.5, ls=":"); ax.set_yticks(range(len(ORD))); ax.set_yticklabels([LAB[v] for v in ORD]); ax.invert_yaxis()
ax.set_xscale("log"); xt = [0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3]; assert xt[0] <= lo_all and hi_all <= xt[-1], (lo_all, hi_all)
ax.set_xlim(xt[0], xt[-1]); ax.set_xticks(xt); ax.set_xticklabels([f"{x:.2f}" for x in xt]); ax.minorticks_off()
ax.set_xlabel("Rate ratio per 1 standard deviation (95% credible interval, log scale)"); ax.spines[["top", "right"]].set_visible(False)
ax.legend(handles=[Line2D([0], [0], color=c, marker=m, lw=0.8, ms=3.4, mew=0, label=l) for l, _, c, m in MOD], loc="upper center", bbox_to_anchor=(0.40, -0.085), ncol=3, frameon=False, fontsize=8)
s3 = save(fig, 2, dpi=1200)
# Fig S2 — 시군구 유형(구·시·군) 지도(17 C9, 시군구 코드 결합)
S6t = S6.set_index("sigungu_cd"); gt = G.copy(); gt["r"] = gt.cd.map(S6t.fbd_region); assert gt.r.notna().all()
gt["t"] = gt.r.map(lambda r: "Urban ward" if r.endswith("구") else ("County" if r.endswith("군") else "City"))
TP = {"Urban ward": "#B03A6E", "City": "#2B6CB0", "County": "#9ED9A0"}  ; tc = gt.t.value_counts(); assert tc.sum() == 229
fig, ax = plt.subplots(figsize=(W * 0.6, 4.2)); fig.subplots_adjust(left=0.01, right=0.99, top=0.97, bottom=0.17)
gt.plot(ax=ax, color=[TP[t] for t in gt.t], edgecolor="#808080", linewidth=LW); mapax(ax)
ax.legend(handles=[Patch(facecolor=TP[t], edgecolor="#777777", linewidth=LW, label=f"{t} ({tc[t]})") for t in ("Urban ward", "City", "County")], title="District type (districts)", loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False)
s4 = save(fig, "S2")
for k, s, dp in zip((1, "S1", 2, "S2"), (s1, s2, s3, s4), (DPI, DPI, 1200, DPI)): print(f"Fig{k}: {s[0]}x{s[1]} px = {s[0]/dp*25.4:.0f} x {s[1]/dp*25.4:.0f} mm")
