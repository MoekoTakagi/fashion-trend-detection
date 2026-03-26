"""
Google Trends 週次データ取得（LAG_PAIRS検証・Pinterest Predicts 2026監視用）
- Google Trendsの5年超週次制限のため2期間に分割して取得
- キャッシュは trends_cache/{期間}/ に分けて保存（衝突防止）
- 過去ヒットは両期間、監視中（Pinterest Predicts 2026 + 現在上昇中）は2021_2026のみ取得
- EN カテゴリは geo=US と geo=JP の両方を自動取得（en_in_jp 相当）
- sleep_sec=90 で慎重に取得・キャッシュ済みはスキップ
"""
import time
import pandas as pd
from pathlib import Path
from pytrends.request import TrendReq

BASE_CACHE_DIR = Path(__file__).parent / 'trends_cache'

PERIODS = {
    '2021_2026': {
        'timeframe': '2021-03-01 2026-02-28',
        'anchor_en': 'Y2K fashion',
        'anchor_jp': 'Y2K',
    },
    '2016_2021': {
        'timeframe': '2016-03-01 2021-02-28',
        'anchor_en': 'korean fashion',
        'anchor_jp': '韓国ファッション',
    },
}

# (lang, 過去ヒット=両期間取得, 監視中=2021_2026のみ取得)
CATEGORIES = {

    # ─── EN (geo=US + geo=JP 自動取得) ───────────────────────────────────────
    'styles_en': ('EN',
        # 過去ヒット（両期間）
        [
            'Y2K fashion', 'normcore', 'quiet luxury', 'balletcore',
            'dark academia', 'cottagecore', 'mob wife aesthetic', 'old money aesthetic',
            'korean street style', 'kpop fashion', 'k-style fashion',
        ],
        # 監視中（Pinterest Predicts 2026）
        [
            'poetcore',                   # 詩人風アカデミックスタイル (+175%)
            'vamp romantic',              # ゴシック×ロマンティック
            'glamoretti fashion',         # 80年代マキシマリスト
            'wilderkind aesthetic',       # 森・動物インスパイア
            'khaki coded',                # ユーティリティカーキ
            'extra celestial aesthetic',  # 宇宙・オパールセント (+80%)
            'glitchy glam',               # メタリックグラマラス
            'barbiecore',
        ],
    ),
    'items_en': ('EN',
        # 過去ヒット（両期間）
        [
            # ボトムス
            'wide leg pants',
            'mini skirt', 'mini skirt outfit', 'mermaid skirt', 'biker shorts',
            # トップス
            'corset top', 'bustier fashion',
            # その他
            'cargo pants',
            # ウェスト丈
            'mid rise jeans', 'mid rise pants', 'low rise jeans', 'low rise pants',
        ],
        # 監視中（Pinterest Predicts 2026）
        [
            'lace outfit', 'lace top outfit', 'lace skirt outfit',               # Laced Up (+215%)
            'brooch aesthetic', 'brooch outfit', 'statement accessories outfit',  # Brooched (+110%)
            'military jacket', 'army jacket', 'safari jacket', 'utility vest',   # Khaki Coded
            'sequin outfit', 'satin dress outfit', 'glossy fashion',              # Glamoretti
            'maximalist accessories', 'layered jewelry', 'statement earrings outfit', # Glamoretti (+105%)
            'crossbody bag', 'messenger bag', 'satchel bag aesthetic', 'leather bag aesthetic', # Poetcore (+85%)
            'barrel jeans outfit', 'wide barrel pants', 'baggy denim outfit',    # 継続トレンド
            'baggy jeans', 'barrel jeans',                                        # 継続トレンド
        ],
    ),

    # ─── JP (geo=JP, 日本語キーワード) ───────────────────────────────────────
    'styles_JP': ('JP',
        # 過去ヒット（両期間）
        [
            '韓国ファッション', 'バレエコア',
            'クワイエットラグジュアリー',
            'オールドマネーコーデ', 'オールドマネーファッション',
            'バービーファッション', 'バービーコーデ',
            'Y2Kファッション', 'Y2Kコーデ',
            # 対応カタカナ
            'ダークアカデミア', 'コテージコア', 'ノームコア', 'モブワイフコーデ',
        ],
        # 監視中（Pinterest Predicts 2026）
        [
            'ヴィンテージブレザーコーデ', 'アカデミックコーデ', 'ブックコア',        # Poetcore
            'ゴシックコーデ', 'ダークロマンティック', 'ヴァンパイアコーデ',          # Vamp Romantic
            'マキシマリストコーデ', '80年代ファッション', 'バブルファッション',        # Glamoretti
            '森ガール', 'ネイチャーコーデ', 'アニマルプリントコーデ',                # Wilderkind
            'カーキコーデ', 'ミリタリーコーデ', 'サファリコーデ',                    # Khaki Coded
            'オパールコーデ', 'パールコーデ', 'ギャラクシーコーデ',                  # Extra Celestial
            'メタリックコーデ', 'シルバーコーデ', 'グリッターコーデ',                # Glitchy Glam
        ],
    ),
    'items_JP': ('JP',
        # 過去ヒット（両期間）
        [
            # ボトムス
            'ワイドパンツ',
            'ミニスカート', 'マーメイドスカート', 'バイカーパンツ',
            # トップス
            'ビスチェ',
            'コルセットトップ', 'コルセットトップス', 'コルセットコーデ', 'コルセット風トップス',
            # その他
            'カーゴパンツ',
            # ウェスト丈
            'ミドルライズ', 'ミドルウェスト', 'センターウェスト', 'レギュラーウェスト',
            'ローライズ', 'ローウェスト',
        ],
        # 監視中（Pinterest Predicts 2026）
        [
            'レースコーデ', 'レーストップス', 'レーススカート',                       # Laced Up
            'ブローチコーデ', 'ブローチつけ方', 'アクセサリーコーデ',                 # Brooched
            'ミリタリージャケット', 'アーミージャケット', 'サファリジャケット', 'ユーティリティベスト', # Khaki Coded
            'スパンコールコーデ', 'サテンドレス', 'グロッシーコーデ', 'ラメコーデ',    # Glamoretti
            'マキシマリストアクセサリー', 'レイヤードアクセサリー', 'ビッグイヤリング', # Glamoretti
            'クロスボディバッグ', 'メッセンジャーバッグ', 'サッチェルバッグ', 'レザーバッグコーデ', # Poetcore
            'バレルジーンズ', 'タルパンツ', 'バギーデニム',                           # 継続トレンド
        ],
    ),
}


def fetch(geo, anchor, keywords, category, timeframe, cache_dir, sleep_sec=90, max_retries=4):
    pytrends = TrendReq(hl='ja-JP' if geo == 'JP' else 'en-US', tz=540)
    cache_dir.mkdir(parents=True, exist_ok=True)
    results = {}

    anchor_cache = cache_dir / f'{category}__anchor.csv'
    if anchor_cache.exists():
        anchor_series = pd.read_csv(anchor_cache, index_col=0, parse_dates=True).iloc[:, 0]
        print(f'  [anchor] {anchor} → キャッシュ')
    else:
        print(f'  [anchor] {anchor} 取得中...')
        for attempt in range(max_retries):
            try:
                pytrends.build_payload([anchor], timeframe=timeframe, geo=geo)
                df = pytrends.interest_over_time()
                if 'isPartial' in df.columns:
                    df = df.drop(columns=['isPartial'])
                anchor_series = df[anchor]
                anchor_series.to_frame().to_csv(anchor_cache)
                print(f'  [anchor] {anchor} → 完了')
                time.sleep(sleep_sec)
                break
            except Exception as e:
                wait = sleep_sec * (attempt + 2)
                print(f'  ⚠️ anchor error (attempt {attempt+1}): {e} → {wait}秒待機')
                time.sleep(wait)
        else:
            print(f'  ❌ anchor取得失敗: {anchor}')
            return None
    results[anchor] = anchor_series

    keywords = [kw for kw in keywords if kw != anchor]

    for i, kw in enumerate(keywords):
        batch_cache = cache_dir / f'{category}__batch{i:03d}.csv'
        if batch_cache.exists():
            s = pd.read_csv(batch_cache, index_col=0, parse_dates=True).iloc[:, 0]
            results[kw] = s
            print(f'  [{i+1}] {kw} → キャッシュ')
            continue

        print(f'  [{i+1}] {kw} 取得中...')
        for attempt in range(max_retries):
            try:
                pytrends.build_payload([anchor, kw], timeframe=timeframe, geo=geo)
                df = pytrends.interest_over_time()
                if 'isPartial' in df.columns:
                    df = df.drop(columns=['isPartial'])
                scale = anchor_series.mean() / (df[anchor].mean() + 1e-9)
                s = (df[kw] * scale).clip(0, 100)
                results[kw] = s
                s.to_frame().to_csv(batch_cache)
                print(f'  [{i+1}] {kw} → 完了')
                time.sleep(sleep_sec)
                break
            except Exception as e:
                wait = sleep_sec * (attempt + 2)
                print(f'  ⚠️ error (attempt {attempt+1}): {e} → {wait}秒待機')
                time.sleep(wait)
        else:
            print(f'  ❌ 取得失敗: {kw}')

    return pd.DataFrame(results)


if __name__ == '__main__':
    for period_name, period_cfg in PERIODS.items():
        timeframe = period_cfg['timeframe']
        cache_dir = BASE_CACHE_DIR / period_name
        print(f'\n{"="*50}')
        print(f'期間: {period_name}  ({timeframe})')
        print('='*50)

        all_results = {}
        for category, (lang, past_kws, watch_kws) in CATEGORIES.items():
            # 2016_2021は過去ヒットのみ、2021_2026は全キーワード
            keywords = past_kws + (watch_kws if period_name == '2021_2026' else [])

            if lang == 'EN':
                # geo=US
                print(f'\n📡 [{category}] geo=US  anchor={period_cfg["anchor_en"]}  ({len(keywords)}件)')
                df = fetch('US', period_cfg['anchor_en'], keywords, category, timeframe, cache_dir)
                if df is not None and not df.empty:
                    all_results[category] = df
                    print(f'✅ [{category}] 完了: {df.shape}')

                # geo=JP（en_in_jp 相当）
                cat_jp = f'{category}_jp'
                print(f'\n📡 [{cat_jp}] geo=JP  anchor={period_cfg["anchor_jp"]}  ({len(keywords)}件)')
                df = fetch('JP', period_cfg['anchor_jp'], keywords, cat_jp, timeframe, cache_dir)
                if df is not None and not df.empty:
                    all_results[cat_jp] = df
                    print(f'✅ [{cat_jp}] 完了: {df.shape}')
            else:
                print(f'\n📡 [{category}] geo=JP  anchor={period_cfg["anchor_jp"]}  ({len(keywords)}件)')
                df = fetch('JP', period_cfg['anchor_jp'], keywords, category, timeframe, cache_dir)
                if df is not None and not df.empty:
                    all_results[category] = df
                    print(f'✅ [{category}] 完了: {df.shape}')

        print('\n' + '='*50)
        print(f'取得結果サマリー [{period_name}]（全期間ピーク）')
        print('='*50)
        for cat, df in all_results.items():
            print(f'\n[{cat}]')
            for kw in df.columns:
                s = df[kw]
                peak_val = round(s.max(), 1)
                peak_date = s.idxmax().strftime('%Y-%m')
                recent = round(s.iloc[-52:].mean(), 1)
                print(f'  {kw}: 直近={recent}, ピーク={peak_val} ({peak_date})')
