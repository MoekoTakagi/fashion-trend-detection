"""
synonym_groups.py の全グループについて、
EN × JP の全キーワード × 全期間のピーク値・rolling平均最大値を計算し、
MIN_PEAK の妥当性検証およびペア候補スクリーニングに使用する。

出力:
  screen_pairs.csv  — 全キーワードの判定結果
  コンソール        — ステータス別・概念別にテーブル表示
"""
import pandas as pd
from trend_utils import load_category, get_peak, PERIODS, CATEGORIES, get_mean_last52
from synonym_groups import SYNONYM_GROUPS, STATUS_LABELS

MIN_PEAK       = 10
MIN_LAST52     = 5
ROLLING_WINDOW = 8  # 週

# ── 公開ヘルパー ──────────────────────────────────────────────────────────────

_concept_to_group: dict = {g['concept']: g for g in SYNONYM_GROUPS}


def get_best_jp_keyword(concept: str) -> str | None:
    """SYNONYM_GROUPS の jp_ja から mean_last52 最大の JP キーワードを返す。"""
    g = _concept_to_group.get(concept)
    if not g or not g.get('jp_ja'):
        return None
    scores = [(kw, get_mean_last52(kw, geo='jp')) for kw in g['jp_ja'] if kw]
    return max(scores, key=lambda x: x[1])[0] if scores else None


def get_monitoring_keywords(excluded_keywords: set | None = None) -> pd.DataFrame:
    """
    monitoring ステータスの EN キーワードを絞り込んで返す。

    フィルタ条件:
      - status=monitoring, geo_type=en, peak >= MIN_PEAK
      - mean_last52 >= MIN_LAST52
      - excluded_keywords に含まれるキーワードを除外
    """
    df = run_screening()
    monitoring_en = df[
        (df['status'] == 'monitoring') &
        (df['geo_type'] == 'en') &
        (df['peak'].notna()) &
        (df['peak'] >= MIN_PEAK)
    ]
    if excluded_keywords:
        monitoring_en = monitoring_en[~monitoring_en['keyword'].isin(excluded_keywords)]
    result = monitoring_en.loc[monitoring_en.groupby(['concept', 'keyword'])['peak'].idxmax()].copy()
    result['mean_last52'] = result['keyword'].apply(get_mean_last52)
    result = result[result['mean_last52'] >= MIN_LAST52].reset_index(drop=True)
    return result


def _find_keyword(kw: str, geo_type: str) -> list[dict]:
    """
    キーワードをキャッシュから検索し、見つかった全カテゴリ×全期間を返す。
    geo_type: 'en' → styles_en / items_en
              'jp_ja' → styles_JP / items_JP
              'jp_en' → styles_en_jp / items_en_jp
    """
    cat_map = {
        'en':    ['styles_en', 'items_en'],
        'jp_ja': ['styles_JP', 'items_JP'],
        'jp_en': ['styles_en_jp', 'items_en_jp'],
    }
    target_cats = cat_map[geo_type]
    results = []
    for period in PERIODS:
        for cat in target_cats:
            df = load_category(cat, period)
            if kw in df.columns:
                s = df[kw].dropna()
                if s.empty:
                    continue
                peak_val, peak_date = get_peak(s)
                rolling_max = round(float(s.rolling(ROLLING_WINDOW, min_periods=1).mean().max()), 1)
                results.append({
                    'keyword': kw,
                    'geo_type': geo_type,
                    'period': period,
                    'category': cat,
                    'peak': peak_val,
                    'peak_date': peak_date.strftime('%Y-%m'),
                    'rolling_max': rolling_max,
                    'pass': '✅' if peak_val >= MIN_PEAK else '❌',
                })
    return results


def run_screening() -> pd.DataFrame:
    rows = []
    for group in SYNONYM_GROUPS:
        concept = group['concept']
        status = group['status']
        for geo_type in ['en', 'jp_ja', 'jp_en']:
            for kw in group.get(geo_type, []):
                found = _find_keyword(kw, geo_type)
                if found:
                    for r in found:
                        r['concept'] = concept
                        r['status'] = status
                    rows.extend(found)
                else:
                    # キャッシュに存在しないキーワードも記録
                    rows.append({
                        'concept': concept,
                        'status': status,
                        'keyword': kw,
                        'geo_type': geo_type,
                        'period': '—',
                        'category': '—',
                        'peak': None,
                        'peak_date': '—',
                        'rolling_max': None,
                        'pass': '—（未取得）',
                    })
    return pd.DataFrame(rows)


if __name__ == '__main__':
    df = run_screening()

    pd.set_option('display.max_colwidth', 40)
    pd.set_option('display.width', 200)
    pd.set_option('display.max_rows', 1000)

    cols = ['concept', 'keyword', 'geo_type', 'period', 'peak', 'peak_date', 'rolling_max', 'pass']

    for status, label in STATUS_LABELS.items():
        subset = df[df['status'] == status]
        if subset.empty:
            continue
        print(f'\n{label}')
        print(subset[cols].to_string(index=False))

    df.to_csv('screen_pairs.csv', index=False)
    print(f'\n保存: screen_pairs.csv（{len(df)}行）')
