import pandas as pd

from trend_utils import get_peak, get_status, month_diff, stitch_periods


class TestMonthDiff:
    def test_same_month(self):
        assert month_diff(pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-01")) == 0

    def test_one_year(self):
        assert month_diff(pd.Timestamp("2023-01-01"), pd.Timestamp("2024-01-01")) == 12

    def test_cross_year_boundary(self):
        assert month_diff(pd.Timestamp("2023-11-01"), pd.Timestamp("2024-02-01")) == 3

    def test_negative(self):
        assert month_diff(pd.Timestamp("2024-06-01"), pd.Timestamp("2024-01-01")) == -5


class TestGetStatus:
    DATA_END = pd.Timestamp("2025-12-01")
    TODAY = pd.Timestamp("2026-03-01")

    def test_peak_after_data_end_is_rising_early(self):
        assert get_status("2026-01-01", self.DATA_END, self.TODAY) == "EN上昇初期"

    def test_peak_within_six_months_is_rising(self):
        assert get_status("2025-10-01", self.DATA_END, self.TODAY) == "EN上昇中"

    def test_peak_older_than_six_months_is_peaked(self):
        assert get_status("2024-01-01", self.DATA_END, self.TODAY) == "ENピーク済み"

    def test_boundary_at_data_end(self):
        assert get_status("2025-12-01", self.DATA_END, self.TODAY) == "EN上昇初期"

    def test_boundary_six_months_ago(self):
        # ちょうど6ヶ月前 = 2025-09-01 → EN上昇中
        assert get_status("2025-09-01", self.DATA_END, self.TODAY) == "EN上昇中"


class TestGetPeak:
    def test_returns_max_value_and_date(self):
        idx = pd.date_range("2024-01", periods=4, freq="MS")
        s = pd.Series([10.0, 50.0, 80.0, 30.0], index=idx)
        val, date = get_peak(s)
        assert val == 80.0
        assert date == pd.Timestamp("2024-03-01")

    def test_first_occurrence_when_duplicate_max(self):
        idx = pd.date_range("2024-01", periods=3, freq="MS")
        s = pd.Series([80.0, 30.0, 80.0], index=idx)
        _, date = get_peak(s)
        assert date == pd.Timestamp("2024-01-01")

    def test_value_is_rounded_to_one_decimal(self):
        idx = pd.date_range("2024-01", periods=2, freq="MS")
        s = pd.Series([33.333, 66.666], index=idx)
        val, _ = get_peak(s)
        assert val == 66.7


class TestStitchPeriods:
    def test_no_overlap_concatenates(self):
        s1 = pd.Series([10.0, 20.0], index=pd.date_range("2020-01", periods=2, freq="MS"))
        s2 = pd.Series([30.0, 40.0], index=pd.date_range("2021-01", periods=2, freq="MS"))
        result = stitch_periods(s1, s2)
        assert len(result) == 4
        assert result.is_monotonic_increasing

    def test_scale_adjustment_on_overlap(self):
        # s1 の overlap 平均=20、s2 の overlap 平均=40 → s1 を2倍スケール
        overlap_idx = pd.date_range("2021-01", periods=3, freq="MS")
        s1 = pd.Series([20.0, 20.0, 20.0], index=overlap_idx)
        s2 = pd.Series([40.0, 40.0, 40.0], index=overlap_idx)
        result = stitch_periods(s1, s2)
        # overlap 期間は s2 の値がそのまま使われる
        for d in overlap_idx:
            assert result[d] == 40.0

    def test_s2_takes_priority_in_overlap(self):
        overlap_idx = pd.date_range("2021-01", periods=2, freq="MS")
        s1 = pd.Series([50.0, 50.0], index=overlap_idx)
        s2 = pd.Series([70.0, 80.0], index=overlap_idx)
        result = stitch_periods(s1, s2)
        assert result[pd.Timestamp("2021-01-01")] == 70.0
        assert result[pd.Timestamp("2021-02-01")] == 80.0
