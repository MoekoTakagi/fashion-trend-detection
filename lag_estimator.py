"""
JP 波及タイミング推定モジュール。

主な公開関数:
  estimate_en_peak_dtw()  — DTW スライディングウィンドウで EN ピーク日を推定
  dtw_analog_match()      — EN 波形を LAG_PAIRS と DTW マッチングしてラグを返す
  add_months()            — Timestamp に月数を加算するユーティリティ
  cross_correlate_lag()   — クロスコリレーション（確定ペアの検証用）
"""

import numpy as np
import pandas as pd
from trend_utils import load_category, get_peak

# ─── 確定 LAG_PAIRS（クラスターA）────────────────────────────────────────────
LAG_PAIRS = [
    {
        'label':      'Y2K fashion → Y2Kファッション',
        'en_kw':      'Y2K fashion',
        'en_cat':     'styles_en',
        'en_period':  '2021_2026',
        'lag_months': 11,
        'jp_kw':      'Y2Kファッション',
        'jp_cat':     'styles_JP',
        'jp_period':  '2021_2026',
    },
    {
        'label':      'balletcore → バレエコア',
        'en_kw':      'balletcore',
        'en_cat':     'styles_en',
        'en_period':  '2021_2026',
        'lag_months': 14,
        'jp_kw':      'バレエコア',
        'jp_cat':     'styles_JP',
        'jp_period':  '2021_2026',
    },
    {
        'label':      'low rise jeans → ローライズ',
        'en_kw':      'low rise jeans',
        'en_cat':     'items_en',
        'en_period':  '2016_2021',
        'lag_months': 16,
        'jp_kw':      'ローライズ',
        'jp_cat':     'items_JP',
        'jp_period':  '2016_2021',
    },
    {
        'label':      'normcore → ノームコア',
        'en_kw':      'normcore',
        'en_cat':     'styles_en',
        'en_period':  '2016_2021',
        'lag_months': 14,
        'jp_kw':      'ノームコア',
        'jp_cat':     'styles_JP',
        'jp_period':  '2016_2021',
    },
]

AVG_LAG_MONTHS = round(sum(p['lag_months'] for p in LAG_PAIRS) / len(LAG_PAIRS), 1)

# ─── EN ピーク推定用テンプレート（採用 6 本）──────────────────────────────────
ADOPTED_TEMPLATES = [
    {'label': 'dark academia',  'kw': 'dark academia',  'cat': 'styles_en', 'period': '2016_2021'},
    {'label': 'biker shorts',   'kw': 'biker shorts',   'cat': 'items_en',  'period': '2016_2021'},
    {'label': 'cottagecore',    'kw': 'cottagecore',    'cat': 'styles_en', 'period': '2016_2021'},
    {'label': 'barrel jeans',   'kw': 'barrel jeans',   'cat': 'items_en',  'period': '2021_2026'},
    {'label': 'korean fashion', 'kw': 'korean fashion', 'cat': 'styles_en', 'period': '2016_2021'},
    {'label': 'barbiecore',     'kw': 'barbiecore',     'cat': 'styles_en', 'period': '2021_2026'},
]

# LAG_PAIRS（確定4ペア）＋ ADOPTED_TEMPLATES（追加6本）の統合テンプレートリスト
ALL_TEMPLATES: list[dict] = [
    {'label': p['en_kw'], 'kw': p['en_kw'], 'cat': p['en_cat'], 'period': p['en_period']}
    for p in LAG_PAIRS
] + ADOPTED_TEMPLATES


# ─── 内部ユーティリティ ───────────────────────────────────────────────────────

def add_months(date: pd.Timestamp, months: float) -> pd.Timestamp:
    total = date.month - 1 + months
    return pd.Timestamp(year=date.year + int(total // 12), month=int(total % 12) + 1, day=1)


def _extract_wave(series: pd.Series, ref_date: pd.Timestamp, window_months: int = 24) -> np.ndarray:
    """ref_date 前 window_months ヶ月の波形をピーク値で正規化して返す。"""
    start = ref_date - pd.DateOffset(months=window_months)
    wave = series[(series.index >= start) & (series.index <= ref_date)].fillna(0).values
    peak = wave.max()
    return wave / peak if peak > 0 else wave


def _dtw_distance(s1: np.ndarray, s2: np.ndarray) -> float:
    """2系列間の DTW 距離を計算する。"""
    n, m = len(s1), len(s2)
    dtw = np.full((n + 1, m + 1), np.inf)
    dtw[0, 0] = 0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = abs(s1[i - 1] - s2[j - 1])
            dtw[i, j] = cost + min(dtw[i - 1, j], dtw[i, j - 1], dtw[i - 1, j - 1])
    return dtw[n, m]


# ─── 公開関数 ─────────────────────────────────────────────────────────────────

def cross_correlate_lag(
    en_series: pd.Series,
    jp_series: pd.Series,
    max_lag_months: int = 30,
) -> tuple[int, float, list[float]]:
    """
    クロスコリレーションで EN→JP ラグを推定する。確定ペアの検証用。

    Returns:
        best_lag_months : 相関が最大になるラグ（ヶ月）
        best_corr       : その時の相関係数
        corr_curve      : lag=0〜max_lag_months の相関係数リスト（可視化用）
    """
    common = en_series.index.intersection(jp_series.index)
    en = en_series.loc[common].fillna(0).values
    jp = jp_series.loc[common].fillna(0).values

    best_lag, best_corr = 0, -np.inf
    corr_curve = []
    for lag_months in range(0, max_lag_months + 1):
        lag_weeks = lag_months * 4
        if lag_weeks >= len(jp):
            corr_curve.append(np.nan)
            continue
        jp_shifted = jp[lag_weeks:]
        en_aligned = en[:len(jp_shifted)]
        if len(en_aligned) < 10:
            corr_curve.append(np.nan)
            continue
        corr = float(np.corrcoef(en_aligned, jp_shifted)[0, 1])
        corr_curve.append(corr)
        if corr > best_corr:
            best_corr, best_lag = corr, lag_months

    return best_lag, best_corr, corr_curve


def dtw_analog_match(
    en_series: pd.Series,
    en_peak_date: pd.Timestamp,
    window_months: int = 24,
) -> dict:
    """
    確定 LAG_PAIRS との DTW マッチングで最近傍ペアとラグを返す。

    Returns:
        best_template : 最近傍ペアのラベル
        lag_months    : そのペアのラグ（ヶ月）
        dtw_distance  : DTW 距離（小さいほど類似）
        all_distances : 全ペアの距離 dict（可視化用）
    """
    target_wave = _extract_wave(en_series, en_peak_date, window_months)
    best = {'best_template': 'avg（マッチなし）', 'lag_months': AVG_LAG_MONTHS, 'dtw_distance': np.inf}
    all_distances = {}

    for pair in LAG_PAIRS:
        ref_df = load_category(pair['en_cat'], pair['en_period'])
        if pair['en_kw'] not in ref_df.columns:
            continue
        ref_series = ref_df[pair['en_kw']]
        _, ref_peak_date = get_peak(ref_series)
        ref_wave = _extract_wave(ref_series, ref_peak_date, window_months)
        dist = _dtw_distance(target_wave, ref_wave)
        all_distances[pair['label']] = round(dist, 3)
        if dist < best['dtw_distance']:
            best = {
                'best_template': pair['label'],
                'lag_months':    pair['lag_months'],
                'dtw_distance':  dist,
            }

    best['all_distances'] = all_distances
    return best


def estimate_en_peak_dtw(
    target_series: pd.Series,
    data_end: pd.Timestamp,
    templates: list[dict],
) -> dict | None:
    """
    テンプレートとのDTWスライディングウィンドウマッチングで EN ピーク日を推定する。

    アプローチ:
      監視中キーワードの上昇波形（DATA_END まで）を正規化し、
      各テンプレートの完全系列上でスライドさせながら DTW 距離が最小の位置を探す。
      そのウィンドウ終端からテンプレートのピークまでの残り週数を EN ピーク推定に使う。

    Parameters:
        target_series : 監視中キーワードの EN 系列
        data_end      : データ終端日（= 現在地）
        templates     : [{'label', 'kw', 'cat', 'period'}, ...] のリスト

    Returns:
        en_peak_est   : 推定 EN ピーク日
        weeks_remaining: DATA_END からピークまでの推定週数
        best_template : 最近傍テンプレートのラベル
        dtw_distance  : そのときの DTW 距離
        all_results   : 全テンプレートの結果リスト（可視化用）
    """
    obs = target_series[target_series.index <= data_end].fillna(0)
    obs_vals = obs.values.astype(float)
    obs_peak = obs_vals.max()
    if obs_peak <= 0:
        return None
    obs_norm = obs_vals / obs_peak
    n = len(obs_norm)

    best = {'dtw_distance': np.inf}
    all_results = []

    for tmpl in templates:
        s = load_category(tmpl['cat'], tmpl['period'])
        if tmpl['kw'] not in s.columns:
            continue
        s = s[tmpl['kw']].fillna(0)
        s_vals = s.values.astype(float)
        s_peak_val = s_vals.max()
        if s_peak_val <= 0:
            continue
        s_norm = s_vals / s_peak_val
        s_peak_idx = int(np.argmax(s_vals))
        T = len(s_norm)

        # スライディングウィンドウ: ウィンドウがピーク手前に収まる範囲のみ検索
        upper = min(s_peak_idx - n + 1, T - n)
        if upper < 0:
            continue  # ターゲットがテンプレートより長い場合はスキップ
        best_pos, best_dist = 0, np.inf
        for start in range(0, upper + 1):
            window = s_norm[start:start + n]
            dist = _dtw_distance(obs_norm, window)
            if dist < best_dist:
                best_dist, best_pos = dist, start

        window_end_idx = best_pos + n - 1
        weeks_remaining = s_peak_idx - window_end_idx

        all_results.append({
            'label':           tmpl['label'],
            'dtw_distance':    round(best_dist, 3),
            'weeks_remaining': weeks_remaining,
            'window_start':    best_pos,
            'window_end':      window_end_idx,
            'template_series': s,
            'template_peak_idx': s_peak_idx,
        })

        if best_dist < best['dtw_distance']:
            best = {
                'dtw_distance':    best_dist,
                'best_template':   tmpl['label'],
                'weeks_remaining': weeks_remaining,
                **all_results[-1],
            }

    if best['dtw_distance'] == np.inf:
        return None

    weeks = max(int(best['weeks_remaining']), 1)
    en_peak_est = data_end + pd.Timedelta(weeks=weeks)

    return {
        'en_peak_est':     en_peak_est,
        'weeks_remaining': best['weeks_remaining'],
        'best_template':   best['best_template'],
        'dtw_distance':    best['dtw_distance'],
        'all_results':     all_results,
    }


