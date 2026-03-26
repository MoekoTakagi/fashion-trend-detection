"""
確定 LAG_PAIRS 4ペアの EN→JP 時系列を重ね合わせて可視化。
ラグ（EN→JP 波及遅延）の根拠グラフを生成する。
ピーク = raw 最大値の最初の出現日（idxmax）。
"""
from copy import deepcopy

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from trend_utils import load_category, get_peak
from lag_estimator import LAG_PAIRS as _base_pairs, AVG_LAG_MONTHS

# Y2K fashion に可視化用 extra 参照系列を追加（lag_estimator には持たせない）
LAG_PAIRS = deepcopy(_base_pairs)
for pair in LAG_PAIRS:
    if pair['en_kw'] == 'Y2K fashion':
        pair['extra'] = [
            {'kw': 'Y2K', 'cat': 'styles_JP', 'period': '2021_2026',
             'label': 'Y2K (geo=JP 英語検索)', 'color': '#F28E2B'},
        ]


def build_figure(pairs: list[dict], title: str = '') -> go.Figure:
    n = len(pairs)
    cols = min(n, 2)
    rows = (n + cols - 1) // cols

    fig = make_subplots(
        rows=rows, cols=cols,
        subplot_titles=[p['label'] for p in pairs],
        vertical_spacing=0.15,
        horizontal_spacing=0.08,
    )

    positions = [(r + 1, c + 1) for r in range(rows) for c in range(cols)]

    for pair, (row, col) in zip(pairs, positions):
        en_s = load_category(pair['en_cat'], pair['en_period'])[pair['en_kw']]
        jp_s = load_category(pair['jp_cat'], pair['jp_period'])[pair['jp_kw']]

        en_peak_val, en_peak_date = get_peak(en_s)
        jp_peak_val, jp_peak_date = get_peak(jp_s)

        show_legend = (row == 1 and col == 1)

        # EN 時系列
        fig.add_trace(go.Scatter(
            x=en_s.index, y=en_s.values,
            name='EN (geo=US)', line=dict(color='#4472C4', width=2),
            legendgroup='en', showlegend=show_legend,
        ), row=row, col=col)

        # JP 時系列
        fig.add_trace(go.Scatter(
            x=jp_s.index, y=jp_s.values,
            name='JP (geo=JP)', line=dict(color='#E15759', width=2),
            legendgroup='jp', showlegend=show_legend,
        ), row=row, col=col)

        # extra シリーズ（参照線）
        for ex in pair.get('extra', []):
            ex_s = load_category(ex['cat'], ex['period'])[ex['kw']]
            ex_peak_val, ex_peak_date = get_peak(ex_s)
            fig.add_trace(go.Scatter(
                x=ex_s.index, y=ex_s.values,
                name=ex['label'], line=dict(color=ex['color'], width=1.5, dash='dot'),
                legendgroup=ex['label'], showlegend=show_legend,
            ), row=row, col=col)
            # extra ピーク点
            fig.add_trace(go.Scatter(
                x=[ex_peak_date], y=[ex_peak_val],
                mode='markers+text',
                marker=dict(color=ex['color'], size=10, symbol='circle'),
                text=[f'<b>{ex_peak_val}</b>'],
                textposition='top center',
                textfont=dict(color=ex['color'], size=11),
                showlegend=False,
            ), row=row, col=col)

        # EN ピーク点マーカー
        fig.add_trace(go.Scatter(
            x=[en_peak_date], y=[en_peak_val],
            mode='markers+text',
            marker=dict(color='#4472C4', size=12, symbol='circle'),
            text=[f'<b>{en_peak_val}</b>'],
            textposition='top center',
            textfont=dict(color='#4472C4', size=12),
            showlegend=False,
        ), row=row, col=col)

        # JP ピーク点マーカー
        fig.add_trace(go.Scatter(
            x=[jp_peak_date], y=[jp_peak_val],
            mode='markers+text',
            marker=dict(color='#E15759', size=12, symbol='circle'),
            text=[f'<b>{jp_peak_val}</b>'],
            textposition='top center',
            textfont=dict(color='#E15759', size=12),
            showlegend=False,
        ), row=row, col=col)

        # EN→JP ピーク間の矢印（ラグ表示）
        mid_y = (en_peak_val + jp_peak_val) / 2 + 8
        fig.add_annotation(
            x=jp_peak_date, y=mid_y,
            ax=en_peak_date, ay=mid_y,
            xref=f'x{(row-1)*2+col}' if (row, col) != (1, 1) else 'x',
            yref=f'y{(row-1)*2+col}' if (row, col) != (1, 1) else 'y',
            axref=f'x{(row-1)*2+col}' if (row, col) != (1, 1) else 'x',
            ayref=f'y{(row-1)*2+col}' if (row, col) != (1, 1) else 'y',
            showarrow=True,
            arrowhead=2, arrowwidth=1.5, arrowcolor='#888',
            text=f'+{pair["lag_months"]}ヶ月',
            font=dict(size=11, color='#555'),
            align='center',
        )

    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        height=max(400, 380 * rows),
        template='plotly_white',
        legend=dict(orientation='h', y=-0.08, x=0.5, xanchor='center'),
    )
    fig.update_yaxes(range=[0, 105], title_text='トレンドスコア')

    return fig


if __name__ == '__main__':
    fig = build_figure(
        LAG_PAIRS,
        title=f'確定 LAG_PAIRS（クラスターA）— EN→JP 波及ラグ検証（平均 {AVG_LAG_MONTHS}ヶ月）',
    )
    fig.write_html('lag_pairs_validation.html')
    fig.write_image('docs/lag_pairs_validation.png', width=1200, height=700, scale=2)
    print('保存: lag_pairs_validation.html / docs/lag_pairs_validation.png')
    fig.show()
