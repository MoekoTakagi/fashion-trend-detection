"""
trends_cache からローカルキャッシュを読み込むユーティリティ。
各 CSV カラム名がキーワード名なのでインデックス計算不要。
"""
import pandas as pd
from pathlib import Path

BASE_CACHE_DIR = Path(__file__).parent / 'trends_cache'

PERIODS = ['2021_2026', '2016_2021']
CATEGORIES = ['styles_en', 'styles_en_jp', 'styles_JP', 'items_en', 'items_en_jp', 'items_JP']
EN_CATS = ['styles_en', 'items_en']
JP_CATS = ['styles_JP', 'items_JP', 'styles_en_jp', 'items_en_jp']


def load_category(category: str, period: str) -> pd.DataFrame:
    """指定カテゴリ・期間の全キーワード時系列を返す。カラム名=キーワード名。"""
    cache_dir = BASE_CACHE_DIR / period
    dfs = []

    anchor_path = cache_dir / f'{category}__anchor.csv'
    if anchor_path.exists():
        dfs.append(pd.read_csv(anchor_path, index_col=0, parse_dates=True))

    for p in sorted(cache_dir.glob(f'{category}__batch*.csv')):
        dfs.append(pd.read_csv(p, index_col=0, parse_dates=True))

    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, axis=1)


def load_keyword(keyword: str, period: str | None = None) -> pd.Series | None:
    """キーワード名で全カテゴリ・全期間を検索して最初に見つかった Series を返す。"""
    search_periods = [period] if period else PERIODS
    for p in search_periods:
        for cat in CATEGORIES:
            df = load_category(cat, p)
            if keyword in df.columns:
                return df[keyword].rename(f'{keyword} [{p}]')
    return None


def load_keyword_both_periods(keyword: str) -> dict[str, pd.Series]:
    """両期間で同キーワードを返す。period→Series の dict。"""
    result = {}
    for p in PERIODS:
        for cat in CATEGORIES:
            df = load_category(cat, p)
            if keyword in df.columns:
                result[p] = df[keyword]
                break
    return result


def stitch_periods(series_2016: pd.Series, series_2021: pd.Series) -> pd.Series:
    """2016_2021 と 2021_2026 を接合してアンカー正規化で繋ぐ（重複期間の平均でスケール合わせ）。"""
    overlap = series_2016.index.intersection(series_2021.index)
    if len(overlap) == 0:
        return pd.concat([series_2016, series_2021]).sort_index()

    scale_old = series_2016.loc[overlap].mean()
    scale_new = series_2021.loc[overlap].mean()
    if scale_new > 0:
        adjusted = (series_2016 * (scale_new / scale_old)).clip(0, 100)
    else:
        adjusted = series_2016

    combined = pd.concat([adjusted[~adjusted.index.isin(series_2021.index)], series_2021])
    return combined.sort_index()


def get_peak(series: pd.Series) -> tuple[float, pd.Timestamp]:
    """raw最大値の日付とスコアを返す。同値が複数ある場合は最初の出現日。"""
    peak_date = series.idxmax()
    peak_val  = round(float(series.max()), 1)
    return peak_val, peak_date


def get_series_stitched(keyword: str) -> pd.Series | None:
    """両期間を stitch して結合した series を返す。片方のみ存在する場合はその series を返す。"""
    periods = load_keyword_both_periods(keyword)
    if not periods:
        return None
    if len(periods) == 1:
        return list(periods.values())[0]
    return stitch_periods(periods['2016_2021'], periods['2021_2026'])


def get_en_series(keyword: str) -> pd.Series | None:
    """EN カテゴリ（styles_en / items_en）から keyword を検索して返す。"""
    for period in PERIODS:
        for cat in EN_CATS:
            df = load_category(cat, period)
            if keyword in df.columns:
                return df[keyword]
    return None


def get_jp_series(keyword: str) -> pd.Series | None:
    """JP カテゴリ（styles_JP / items_JP / *_en_jp）から keyword を検索して返す。"""
    if not keyword or (isinstance(keyword, float) and pd.isna(keyword)):
        return None
    for period in PERIODS:
        for cat in JP_CATS:
            df = load_category(cat, period)
            if keyword in df.columns:
                return df[keyword]
    return None


def get_mean_last52(keyword: str, geo: str = 'en') -> float:
    """直近 52 週の平均スコアを返す。geo='en' または 'jp'。"""
    s = get_en_series(keyword) if geo == 'en' else get_jp_series(keyword)
    return round(float(s.iloc[-52:].mean()), 1) if s is not None else 0.0


def month_diff(date_from: pd.Timestamp, date_to: pd.Timestamp) -> int:
    """2つの日付間のカレンダー月数を返す（date_to - date_from）。"""
    return (date_to.year - date_from.year) * 12 + (date_to.month - date_from.month)


def get_status(peak_date_str: str, data_end: pd.Timestamp, today: pd.Timestamp | None = None) -> str:
    """EN ピーク日から状態ラベルを返す（EN上昇初期 / EN上昇中 / ENピーク済み）。"""
    if today is None:
        today = pd.Timestamp.now().normalize()
    d = pd.Timestamp(peak_date_str)
    if d >= data_end:
        return 'EN上昇初期'
    elif d >= today - pd.DateOffset(months=6):
        return 'EN上昇中'
    else:
        return 'ENピーク済み'


if __name__ == '__main__':
    # 動作確認
    for period in PERIODS:
        print(f'\n=== {period} ===')
        for cat in CATEGORIES:
            df = load_category(cat, period)
            if not df.empty:
                print(f'  {cat}: {list(df.columns)[:3]} ... ({len(df.columns)}件, {len(df)}週)')
