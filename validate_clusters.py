"""
クラスターB（遅行波及）・クラスターC（早期波及）の時系列可視化。
クラスターB は2期間をstitchして10年間で表示。
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from trend_utils import load_category, stitch_periods, get_peak, month_diff
from validate_lags import build_figure

# ─── クラスターC（barrel jeans, 単一期間）────────────────────────────────────
CLUSTER_C = [
    {
        'label': 'barrel jeans → バレルジーンズ',
        'en_kw': 'barrel jeans', 'en_cat': 'items_en', 'en_period': '2021_2026',
        'jp_kw': 'バレルジーンズ', 'jp_cat': 'items_JP', 'jp_period': '2021_2026',
        'lag_months': 5,
    },
]


def build_cluster_b_figure() -> go.Figure:
    """マーメイドスカートの10年間（2016-2026）＋2波のピーク表示。"""
    en = stitch_periods(
        load_category('items_en', '2016_2021')['mermaid skirt'],
        load_category('items_en', '2021_2026')['mermaid skirt'],
    )
    jp = stitch_periods(
        load_category('items_JP', '2016_2021')['マーメイドスカート'],
        load_category('items_JP', '2021_2026')['マーメイドスカート'],
    )

    # EN: 第1波ピーク（2016-10）、JP: 全期間最大ピーク（2022-01）
    en_peak_date = load_category('items_en', '2016_2021')['mermaid skirt'].idxmax()
    jp_peak_date = load_category('items_JP', '2021_2026')['マーメイドスカート'].idxmax()
    en_peak_val  = round(float(en.loc[en_peak_date]), 1)
    jp_peak_val  = round(float(jp.loc[jp_peak_date]), 1)
    lag = month_diff(en_peak_date, jp_peak_date)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=en.index, y=en.values,
        name='EN (geo=US)', line=dict(color='#4472C4', width=2),
    ))
    fig.add_trace(go.Scatter(
        x=jp.index, y=jp.values,
        name='JP (geo=JP)', line=dict(color='#E15759', width=2),
    ))

    # ピークマーカーと矢印を追加する関数
    def add_peak_pair(en_date, en_val, jp_date, jp_val, lag, wave_label):
        for date, val, color in [(en_date, en_val, '#4472C4'), (jp_date, jp_val, '#E15759')]:
            fig.add_trace(go.Scatter(
                x=[date], y=[val],
                mode='markers+text',
                marker=dict(color=color, size=12, symbol='circle'),
                text=[f'<b>{val}</b>'],
                textposition='top center',
                textfont=dict(color=color, size=11),
                showlegend=False,
            ))
        mid_y = max(en_val, jp_val) + 10
        fig.add_annotation(
            x=jp_date, y=mid_y, ax=en_date, ay=mid_y,
            xref='x', yref='y', axref='x', ayref='y',
            showarrow=True, arrowhead=2, arrowwidth=1.5, arrowcolor='#888',
            text=f'{wave_label}  +{lag}ヶ月',
            font=dict(size=11, color='#555'),
        )

    add_peak_pair(en_peak_date, en_peak_val, jp_peak_date, jp_peak_val, lag, '')

    fig.update_layout(
        title=dict(
            text='クラスターB（遅行波及）— mermaid skirt → マーメイドスカート（10年間）',
            font=dict(size=15),
        ),
        height=420,
        template='plotly_white',
        yaxis=dict(range=[0, 105], title='トレンドスコア'),
        legend=dict(orientation='h', y=-0.15, x=0.5, xanchor='center'),
    )
    return fig


if __name__ == '__main__':
    fig_b = build_cluster_b_figure()
    fig_b.write_html('cluster_b_validation.html')
    fig_b.write_image('docs/cluster_b_validation.png', width=1200, height=420, scale=2)
    print('保存: cluster_b_validation.html / docs/cluster_b_validation.png')
    fig_b.show()

    fig_c = build_figure(CLUSTER_C, title='クラスターC（早期波及）— EN→JP ラグ約5ヶ月')
    fig_c.write_html('cluster_c_validation.html')
    fig_c.write_image('docs/cluster_c_validation.png', width=800, height=420, scale=2)
    print('保存: cluster_c_validation.html / docs/cluster_c_validation.png')
    fig_c.show()
