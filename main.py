"""
ドキュメント用グラフ（docs/）を再生成するスクリプト。
"""
from validate_lags import build_figure, LAG_PAIRS, AVG_LAG_MONTHS
from validate_clusters import build_cluster_b_figure, CLUSTER_C


def main():
    fig = build_figure(
        LAG_PAIRS,
        title=f'確定 LAG_PAIRS（クラスターA）— EN→JP 波及ラグ検証（平均 {AVG_LAG_MONTHS}ヶ月）',
    )
    fig.write_html('lag_pairs_validation.html')
    fig.write_image('docs/lag_pairs_validation.png', width=1200, height=700, scale=2)
    print('保存: lag_pairs_validation.html / docs/lag_pairs_validation.png')

    fig_b = build_cluster_b_figure()
    fig_b.write_html('cluster_b_validation.html')
    fig_b.write_image('docs/cluster_b_validation.png', width=1200, height=420, scale=2)
    print('保存: cluster_b_validation.html / docs/cluster_b_validation.png')

    fig_c = build_figure(CLUSTER_C, title='クラスターC（早期波及）— EN→JP ラグ約5ヶ月')
    fig_c.write_html('cluster_c_validation.html')
    fig_c.write_image('docs/cluster_c_validation.png', width=800, height=420, scale=2)
    print('保存: cluster_c_validation.html / docs/cluster_c_validation.png')


if __name__ == '__main__':
    main()
