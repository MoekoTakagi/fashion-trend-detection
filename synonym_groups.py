"""
ファッショントレンドキーワードの同義語グループ定義。

同じ概念を表す異なる表現をまとめたもの。
screen_pairs.py からimportして全パターンのスクリーニングに使用する。

各グループ:
  concept : 概念名（代表キーワード）
  status  : STATUS_LABELS のキーと対応
  en      : geo=US で取得した英語キーワードリスト
  jp_ja   : geo=JP で取得した日本語キーワードリスト
  jp_en   : geo=JP で取得した英語キーワードリスト（日本人の英語検索）
"""

STATUS_LABELS = {
    'confirmed':  '■ 確定LAGペア（クラスターA）',
    'cluster_b':  '■ クラスターB（遅行波及）',
    'cluster_c':  '■ クラスターC（早期波及）',
    'monitoring': '■ 監視中',
    'excluded':   '■ 除外済み・定番',
    'jp_leads':   '■ JP先行',
}

SYNONYM_GROUPS = [

    # ── 確定LAGペア（クラスターA）────────────────────────────────────────────
    {
        'concept': 'Y2K fashion',
        'status': 'confirmed',
        'en':    ['Y2K fashion'],
        'jp_ja': ['Y2Kファッション', 'Y2Kコーデ'],
        'jp_en': ['Y2K fashion'],
    },
    {
        'concept': 'balletcore',
        'status': 'confirmed',
        'en':    ['balletcore'],
        'jp_ja': ['バレエコア'],
        'jp_en': ['balletcore'],
    },
    {
        'concept': 'low rise jeans',
        'status': 'confirmed',
        'en':    ['low rise jeans', 'low rise pants'],
        'jp_ja': ['ローライズ', 'ローウェスト'],
        'jp_en': ['low rise jeans', 'low rise pants'],
    },
    {
        'concept': 'normcore',
        'status': 'confirmed',
        'en':    ['normcore'],
        'jp_ja': ['ノームコア'],
        'jp_en': ['normcore'],
    },

    # ── クラスターB（遅行波及）────────────────────────────────────────────────
    {
        'concept': 'mermaid skirt',
        'status': 'cluster_b',
        'en':    ['mermaid skirt'],
        'jp_ja': ['マーメイドスカート'],
        'jp_en': ['mermaid skirt'],
    },

    # ── クラスターC（早期波及）────────────────────────────────────────────────
    {
        'concept': 'barrel jeans',
        'status': 'cluster_c',
        'en':    ['barrel jeans', 'barrel jeans outfit', 'wide barrel pants'],
        'jp_ja': ['バレルジーンズ', 'タルパンツ'],
        'jp_en': ['barrel jeans', 'barrel jeans outfit', 'wide barrel pants'],
    },
    {
        'concept': 'baggy jeans',
        'status': 'excluded',
        'en':    ['baggy jeans', 'baggy denim outfit'],
        'jp_ja': ['バギーデニム'],
        'jp_en': ['baggy jeans', 'baggy denim outfit'],
    },

    # ── 監視中────────────────────────────────────────────────────────────────
    {
        'concept': 'mid rise jeans',
        'status': 'monitoring',
        'en':    ['mid rise jeans', 'mid rise pants'],
        'jp_ja': ['ミドルライズ', 'ミドルウェスト', 'センターウェスト', 'レギュラーウェスト'],
        'jp_en': ['mid rise jeans', 'mid rise pants'],
    },
    {
        'concept': 'quiet luxury',
        'status': 'monitoring',
        'en':    ['quiet luxury'],
        'jp_ja': ['クワイエットラグジュアリー'],
        'jp_en': ['quiet luxury'],
    },
    {
        'concept': 'old money aesthetic',
        'status': 'monitoring',
        'en':    ['old money aesthetic'],
        'jp_ja': ['オールドマネーコーデ', 'オールドマネーファッション'],
        'jp_en': ['old money aesthetic'],
    },
    {
        'concept': 'mob wife aesthetic',
        'status': 'monitoring',
        'en':    ['mob wife aesthetic'],
        'jp_ja': ['モブワイフコーデ'],
        'jp_en': ['mob wife aesthetic'],
    },
    {
        'concept': 'poetcore',
        'status': 'monitoring',
        'en':    ['poetcore'],
        'jp_ja': ['ヴィンテージブレザーコーデ', 'アカデミックコーデ', 'ブックコア'],
        'jp_en': ['poetcore'],
    },
    {
        'concept': 'crossbody bag',
        'status': 'monitoring',
        'en':    ['crossbody bag', 'messenger bag', 'satchel bag aesthetic', 'leather bag aesthetic'],
        'jp_ja': ['クロスボディバッグ', 'メッセンジャーバッグ', 'サッチェルバッグ', 'レザーバッグコーデ'],
        'jp_en': ['crossbody bag', 'messenger bag', 'satchel bag aesthetic', 'leather bag aesthetic'],
    },
    {
        'concept': 'vamp romantic',
        'status': 'monitoring',
        'en':    ['vamp romantic'],
        'jp_ja': ['ゴシックコーデ', 'ダークロマンティック', 'ヴァンパイアコーデ'],
        'jp_en': ['vamp romantic'],
    },
    {
        'concept': 'glamoretti fashion',
        'status': 'monitoring',
        'en':    ['glamoretti fashion', 'sequin outfit', 'satin dress outfit', 'glossy fashion',
                  'maximalist accessories', 'layered jewelry', 'statement earrings outfit'],
        'jp_ja': ['マキシマリストコーデ', '80年代ファッション', 'バブルファッション',
                  'スパンコールコーデ', 'サテンドレス', 'グロッシーコーデ', 'ラメコーデ',
                  'マキシマリストアクセサリー', 'レイヤードアクセサリー', 'ビッグイヤリング'],
        'jp_en': ['glamoretti fashion', 'sequin outfit', 'satin dress outfit', 'glossy fashion',
                  'maximalist accessories', 'layered jewelry', 'statement earrings outfit'],
    },
    {
        'concept': 'wilderkind aesthetic',
        'status': 'monitoring',
        'en':    ['wilderkind aesthetic'],
        'jp_ja': ['森ガール', 'ネイチャーコーデ', 'アニマルプリントコーデ'],
        'jp_en': ['wilderkind aesthetic'],
    },
    {
        'concept': 'khaki coded',
        'status': 'monitoring',
        'en':    ['khaki coded', 'military jacket', 'army jacket', 'safari jacket', 'utility vest'],
        'jp_ja': ['カーキコーデ', 'ミリタリーコーデ', 'サファリコーデ',
                  'ミリタリージャケット', 'アーミージャケット', 'サファリジャケット', 'ユーティリティベスト'],
        'jp_en': ['khaki coded', 'military jacket', 'army jacket', 'safari jacket', 'utility vest'],
    },
    {
        'concept': 'extra celestial aesthetic',
        'status': 'monitoring',
        'en':    ['extra celestial aesthetic'],
        'jp_ja': ['オパールコーデ', 'パールコーデ', 'ギャラクシーコーデ'],
        'jp_en': ['extra celestial aesthetic'],
    },
    {
        'concept': 'glitchy glam',
        'status': 'monitoring',
        'en':    ['glitchy glam'],
        'jp_ja': ['メタリックコーデ', 'シルバーコーデ', 'グリッターコーデ'],
        'jp_en': ['glitchy glam'],
    },
    {
        'concept': 'lace outfit',
        'status': 'monitoring',
        'en':    ['lace outfit', 'lace top outfit', 'lace skirt outfit'],
        'jp_ja': ['レースコーデ', 'レーストップス', 'レーススカート'],
        'jp_en': ['lace outfit', 'lace top outfit', 'lace skirt outfit'],
    },
    {
        'concept': 'brooch aesthetic',
        'status': 'monitoring',
        'en':    ['brooch aesthetic', 'brooch outfit', 'statement accessories outfit'],
        'jp_ja': ['ブローチコーデ', 'ブローチつけ方', 'アクセサリーコーデ'],
        'jp_en': ['brooch aesthetic', 'brooch outfit', 'statement accessories outfit'],
    },

    # ── 除外済み・定番────────────────────────────────────────────────────────
    {
        'concept': 'wide leg pants',
        'status': 'excluded',
        'en':    ['wide leg pants'],
        'jp_ja': ['ワイドパンツ'],
        'jp_en': ['wide leg pants'],
    },
    {
        'concept': 'mini skirt',
        'status': 'excluded',
        'en':    ['mini skirt', 'mini skirt outfit'],
        'jp_ja': ['ミニスカート'],
        'jp_en': ['mini skirt', 'mini skirt outfit'],
    },
    {
        'concept': 'biker shorts',
        'status': 'excluded',
        'en':    ['biker shorts'],
        'jp_ja': ['バイカーパンツ'],
        'jp_en': ['biker shorts'],
    },
    {
        'concept': 'corset top',
        'status': 'excluded',
        'en':    ['corset top'],
        'jp_ja': ['コルセットトップ', 'コルセットトップス', 'コルセットコーデ', 'コルセット風トップス'],
        'jp_en': ['corset top'],
    },
    {
        'concept': 'bustier fashion',
        'status': 'excluded',
        'en':    ['bustier fashion'],
        'jp_ja': ['ビスチェ'],
        'jp_en': ['bustier fashion'],
    },
    {
        'concept': 'cargo pants',
        'status': 'excluded',
        'en':    ['cargo pants'],
        'jp_ja': ['カーゴパンツ'],
        'jp_en': ['cargo pants'],
    },
    {
        'concept': 'dark academia',
        'status': 'excluded',
        'en':    ['dark academia'],
        'jp_ja': ['ダークアカデミア'],
        'jp_en': ['dark academia'],
    },
    {
        'concept': 'cottagecore',
        'status': 'excluded',
        'en':    ['cottagecore'],
        'jp_ja': ['コテージコア'],
        'jp_en': ['cottagecore'],
    },
    {
        'concept': 'barbiecore',
        'status': 'excluded',
        'en':    ['barbiecore'],
        'jp_ja': ['バービーファッション', 'バービーコーデ'],
        'jp_en': ['barbiecore'],
    },

    # ── JP先行────────────────────────────────────────────────────────────────
    {
        'concept': 'korean fashion',
        'status': 'jp_leads',
        'en':    ['korean street style', 'kpop fashion', 'k-style fashion'],
        'jp_ja': ['韓国ファッション'],
        'jp_en': ['korean street style', 'kpop fashion', 'k-style fashion'],
    },
]
