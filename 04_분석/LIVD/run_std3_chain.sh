#!/bin/bash
# LIVD (liver disease deaths, K70-K76) principal chain
#  모든 Rscript는 rslot.sh로 감싸고 이 세션 동시 R 작업 ≤4.
set -x
S="${ST_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"; cd "$S"
RC="${ST_FBDZIP_CORRECTED:?set ST_FBDZIP_CORRECTED}"; RS="$S/01_스크립트/rslot.sh"
GR="$S/04_분석/LIVD/graph_593.graph"; T=LIVD; D=261108; NW=4; NMV=200
ST_FBDZIP="$RC" python3 01_스크립트/39m_livd.py $T || exit 1
ST_VER=std3 python3 01_스크립트/80_build_disease_panel_v.py $T || exit 1
ST_FBDZIP="$RC" ST_E2_PANEL_SUF=_std3 python3 01_스크립트/39m_livd.py $T || exit 1
ST_VER=std3 python3 01_스크립트/80_build_disease_panel_v.py $T || exit 1
python3 ../논문_마스터자료/00_분석전_데이터게이트/data_gate.py 04_분석/$T/panel_${T}_std3.csv --region fbd_region > 04_분석/$T/data_gate_${T}_std3_$D.txt 2>&1
echo "GATE rc=$?"
for V in s577 s2 s8; do ST_VER=$V python3 01_스크립트/80_build_disease_panel_v.py $T || exit 1; done
export ST_VER=std3 ST_THREADS=1 ST_GRAPH="$GR"
(cd 01_스크립트 && ST_MV_STOP=1 $RS Rscript 81_fit_inla.R $T) > 04_분석/$T/run_std3_81a.log 2>&1 || exit 1
STEP=$(( NMV / NW ))
for k in $(seq 0 $((NW-1))); do a=$(( k*STEP+1 )); b=$(( (k+1)*STEP )); (cd 01_스크립트 && ST_MV_RANGE=$a-$b $RS Rscript 81_fit_inla.R $T) > 04_분석/$T/run_std3_81_mv_$a.log 2>&1 & sleep 20; done
wait
(cd 01_스크립트 && $RS Rscript 81_fit_inla.R $T) > 04_분석/$T/run_std3_81b.log 2>&1 || exit 1
# 사전지정 주모형 민감도 3개(그래프 577·80+ 없음·10구간 E) — 81b 뒤 병렬 3
for V in s577 s2 s8; do (cd 01_스크립트 && ST_VER=$V ST_THREADS=1 ST_MV_N=2 ST_GRAPH=$([ $V = s577 ] || echo "$GR") $RS Rscript 81_fit_inla.R $T) > 04_분석/$T/run_sens3_$V.log 2>&1 & sleep 20; done
python3 01_스크립트/82_core_report.py $T $D > 04_분석/$T/run_std3_82.log 2>&1
python3 01_스크립트/83_check_report.py $T $D >> 04_분석/$T/run_std3_82.log 2>&1
wait
echo "CHAIN done"
python3 01_스크립트/87_window_grid.py $T std3; (cd 01_스크립트 && TAG=$T ST_VER=std3 $RS Rscript 85_window_maps.R $T std3); python3 01_스크립트/86_yearly_maps_ehsa.py $T std3
python3 01_스크립트/88g_sens_prep.py $T std3 CLRD,ALZ || exit 1
cd 01_스크립트; export TAG=$T NCO=CLRD,ALZ
L=../04_분석/$T
JOBS=(); for G in 1 2 3 4 5 6; do JOBS+=("GROUP=$G $RS Rscript 88g_sens_suite.R > $L/run_std3_88g_$G.log 2>&1"); done
JOBS+=("$RS Rscript 88h_ppc_varpart.R > $L/run_std3_88h.log 2>&1")
for G in nb struct kh review; do JOBS+=("$RS Rscript 88k_struct_kh.R $G > $L/run_std3_88k_$G.log 2>&1"); done
printf '%s\n' "${JOBS[@]}" | xargs -P 4 -I{} bash -c '{}'
if grep -q 'KH_typeII FAILED' $L/run_std3_88k_kh.log; then mv $L/results_std3/S43_part_KH_typeII.csv $L/results_std3/S43_part_KH_typeII_failed_init.csv.bak; KH_INIT=0 $RS Rscript 88k_struct_kh.R kh > $L/run_std3_88k_kh_init0.log 2>&1; fi
cd ..; TAG=$T ST_VER=std3 python3 01_스크립트/89g_sens_combine.py $T std3 > 04_분석/$T/run_std3_89g.log 2>&1
echo "ALL rc=$?"; grep -l "FAILED" 04_분석/$T/run_std3_88*.log; true
