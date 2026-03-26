import numpy as np
import pandas as pd
import pytest

from lag_estimator import _dtw_distance, add_months, cross_correlate_lag


class TestAddMonths:
    def test_simple(self):
        assert add_months(pd.Timestamp("2024-01-01"), 3) == pd.Timestamp("2024-04-01")

    def test_cross_year(self):
        assert add_months(pd.Timestamp("2024-11-01"), 3) == pd.Timestamp("2025-02-01")

    def test_twelve_months(self):
        assert add_months(pd.Timestamp("2023-06-01"), 12) == pd.Timestamp("2024-06-01")

    def test_fractional_rounds_down(self):
        # 0.5ヶ月は切り捨て → 同月
        assert add_months(pd.Timestamp("2024-01-01"), 0.5) == pd.Timestamp("2024-01-01")

    def test_avg_lag(self):
        # AVG_LAG_MONTHS=13.8 → 13ヶ月加算（切り捨て）
        result = add_months(pd.Timestamp("2024-01-01"), 13.8)
        assert result == pd.Timestamp("2025-02-01")


class TestDtwDistance:
    def test_identical_sequences(self):
        s = np.array([0.2, 0.5, 1.0, 0.8, 0.3])
        assert _dtw_distance(s, s) == 0.0

    def test_non_negative(self):
        s1 = np.array([0.0, 1.0, 0.0])
        s2 = np.array([1.0, 0.0, 1.0])
        assert _dtw_distance(s1, s2) >= 0.0

    def test_larger_difference_gives_larger_distance(self):
        base = np.array([0.0, 0.5, 1.0, 0.5, 0.0])
        close = np.array([0.1, 0.6, 0.9, 0.4, 0.1])
        far   = np.array([1.0, 0.0, 0.0, 0.0, 1.0])
        assert _dtw_distance(base, close) < _dtw_distance(base, far)

    def test_single_element(self):
        assert _dtw_distance(np.array([0.5]), np.array([0.5])) == 0.0
        assert _dtw_distance(np.array([0.0]), np.array([1.0])) == pytest.approx(1.0)


class TestCrossCorrelate:
    def test_identical_series_has_zero_lag(self):
        idx = pd.date_range("2020-01", periods=60, freq="W")
        s = pd.Series(np.sin(np.linspace(0, 4 * np.pi, 60)), index=idx)
        lag, corr, _ = cross_correlate_lag(s, s, max_lag_months=5)
        assert lag == 0
        assert corr > 0.99

    def test_detects_two_month_lag(self):
        # jp[t] = en[t-8]: EN が JP より 8週（=2ヶ月）先行するシリーズ
        n = 80
        wave = np.sin(np.linspace(0, 4 * np.pi, n))
        idx = pd.date_range("2020-01", periods=n, freq="W")
        en = pd.Series(wave, index=idx)
        jp = pd.Series(np.concatenate([np.zeros(8), wave[:-8]]), index=idx)
        lag, corr, _ = cross_correlate_lag(en, jp, max_lag_months=5)
        assert lag == 2
        assert corr > 0.95

    def test_corr_curve_length(self):
        idx = pd.date_range("2020-01", periods=60, freq="W")
        s = pd.Series(np.sin(np.linspace(0, 2 * np.pi, 60)), index=idx)
        _, _, curve = cross_correlate_lag(s, s, max_lag_months=10)
        assert len(curve) == 11  # 0〜10ヶ月の11点
