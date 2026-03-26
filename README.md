# Fashion Trend Detection — EN→JP 波及タイミング予測

Google Trends データを用いて、英語圏（EN）で上昇中のファッショントレンドが
日本（JP）でピークを迎えるタイミングを定量的に予測するプロジェクト。

---

## 予測の全体像

本プロジェクトの予測は **「確定 LAG_PAIRS」** と呼ぶ 4 つの EN→JP 波及実績ペアを軸に成立している。

> 過去に EN でピークを打ち、その後 JP でも波及が確認できたキーワードペアを 10 年分の Google Trends データから特定し、
> その波形パターンとラグ（11〜16ヶ月）を新規キーワードの予測テンプレートとして使う。

| EN キーワード | JP キーワード | EN→JP ラグ |
|---|---|---|
| Y2K fashion | Y2Kファッション | 11ヶ月 |
| balletcore | バレエコア | 14ヶ月 |
| low rise jeans | ローライズ | 16ヶ月 |
| normcore | ノームコア | 14ヶ月 |

LAG_PAIRS の**選定過程・除外ペア・データ設計の根拠**は [`docs/lag_pairs_analysis.md`](docs/lag_pairs_analysis.md) に詳述している。
分析の前提となるドキュメントのため、あわせて参照のこと。

---

## 分析フロー

```
1. monitoring_keyword_screening.ipynb   — 監視キーワードのスクリーニング
2. lag_validation.ipynb                 — EN→JP ラグの検証（確定 LAG_PAIRS）
3. en_peak_prediction.ipynb             — EN ピーク日の予測（DTW）
4. jp_timing_estimation.ipynb          — JP 波及タイミングの推定
```

### 1. キーワードスクリーニング (`monitoring_keyword_screening.ipynb`)
- Google Trends の EN/JP データから監視対象キーワードを抽出
- フラット・季節性・ピーク済みなど予測不適なキーワードを除外
- 最終的に `status=monitoring` のキーワードリストを生成

### 2. LAG_PAIRS 検証 (`lag_validation.ipynb`)
- クロスコリレーション vs DTW の精度比較（4ペア中クロスコリレーションは 1/4 しか一致せず → DTW を採用）
- DTW アナログマッチングのセルフマッチ確認（実装の正しさを担保）
- 確定 4 ペアの EN 波形を重ね描きしテンプレートとしての多様性を確認

### 3. EN ピーク予測 (`en_peak_prediction.ipynb`)
- DTW スライディングウィンドウで各キーワードの EN ピーク日を推定
- LOO バックテスト: MAE 3.5ヶ月、中央値 1.0ヶ月、±6M 以内 90%
- Chronos / Prophet / ARIMA を信頼度シグナルとして併用
- Pinterest Predicts 2026 選定キーワードを対象に 2027 年前後のピークを予測

### 4. JP 波及推定 (`jp_timing_estimation.ipynb`)
- DTW analog: EN 波形を確定 LAG_PAIRS と照合し最近傍ラグを適用
- Prophet による JP 直接予測と比較検討した結果、JP 上昇途中キーワードには
  Prophet が機能しないことを確認 → dtw_analog を採用
- EN ピーク後 約 11〜16ヶ月 で JP 波及ピークと推定

---

## 主要モジュール

| ファイル | 役割 |
|---|---|
| `lag_estimator.py` | 確定 LAG_PAIRS・ADOPTED_TEMPLATES の定義、DTW アナログマッチング・EN ピーク推定のコアロジック |
| `synonym_groups.py` | 全監視キーワードの定義（EN/JP 対応・ステータス管理） |
| `trend_utils.py` | キャッシュ読み込み・ピーク取得・状態判定などの共通ユーティリティ |
| `screen_pairs.py` | キーワードスクリーニングのロジック |
| `fetch_trends.py` | Google Trends データの取得・保存 |
| `validate_lags.py` | 確定 LAG_PAIRS の EN→JP 時系列を重ね合わせてラグを可視化 |
| `validate_clusters.py` | クラスターB（遅行波及）・クラスターC（早期波及）の時系列を可視化 |
| `main.py` | `docs/` 用検証グラフを一括再生成するエントリーポイント |

---

## 技術スタック

- **時系列予測**: DTW (Dynamic Time Warping), Prophet, Chronos, ARIMA
- **検証**: Leave-One-Out バックテスト, クロスコリレーション
- **可視化**: Plotly
- **データ**: Google Trends (pytrends)

---

## データ構造

### キャッシュディレクトリ (`trends_cache/`)

Google Trends データはバッチ取得してローカルにキャッシュしている。

```
trends_cache/
├── 2016_2021/          # 2016-02-28 〜 2021-02-28（週次）
│   ├── styles_en__anchor.csv
│   ├── styles_en__batch000.csv
│   ├── styles_en__batch001.csv
│   ├── ...
│   ├── styles_JP__*.csv
│   ├── styles_en_jp__*.csv
│   ├── items_en__*.csv
│   ├── items_JP__*.csv
│   └── items_en_jp__*.csv
└── 2021_2026/          # 2021-02-28 〜 2026-02-22（週次）
    └── （同構成）
```

### カテゴリ分類

| カテゴリ名 | geo | キーワード種別 |
|---|---|---|
| `styles_en` | グローバル | EN スタイル系（"Y2K fashion", "balletcore" など） |
| `styles_JP` | 日本 | JP スタイル系（"Y2Kファッション", "バレエコア" など） |
| `styles_en_jp` | 日本 | EN スタイル系の JP 検索量 |
| `items_en` | グローバル | EN アイテム系（"low rise jeans", "lace outfit" など） |
| `items_JP` | 日本 | JP アイテム系（"ローライズ", "レーススカート" など） |
| `items_en_jp` | 日本 | EN アイテム系の JP 検索量 |

### ファイル形式

- **anchor**: バッチ結合の基準となる週次系列（index 正規化用）
- **batch000〜**: キーワードを 5 件ずつバッチ取得した系列
- `load_category(cat, period)` で結合済み DataFrame として読み込み可能

### データ範囲

- 期間: 2016-2021 / 2021-2026（2 期間に分割して取得）
- DATA_END: 2026-02-22（最終取得日）

---

## ドキュメント

### [`docs/lag_pairs_analysis.md`](docs/lag_pairs_analysis.md) — LAG_PAIRS 選定分析ノート

予測モデルの根幹となる確定 LAG_PAIRS の選定根拠をまとめたドキュメント。
ノートブックと合わせて読むことで分析の背景・判断の経緯が把握できる。

- 確定 4 ペアの詳細（EN/JP ピーク値・日付・データソース）
- 調査済み除外ペアの一覧と除外理由（逆方向波及・EN 定番アイテム・JP 検索量不足など）
- データ取得設計（アンカー正規化の仕組み・MIN_PEAK=10 の根拠）
- 早期波及クラスター（+5ヶ月）・遅行波及クラスター（+63ヶ月）の観察

---

## 実行方法

```bash
# 依存関係のインストール
uv sync

# データの準備（どちらか一方）
tar -xzf trends_cache.tar.gz        # 付属キャッシュを展開して使う場合
uv run python fetch_trends.py       # Google Trends から新規取得する場合（時間がかかります）

# ノートブックの実行（順番通りに実行すること）
source .venv/bin/activate
jupyter lab

# テストの実行
uv sync --group dev
uv run pytest tests/
```
