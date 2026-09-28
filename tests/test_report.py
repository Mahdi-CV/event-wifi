from event_wifi.report import pct, percentile


def test_percentile_empty():
    assert percentile([], 0.95) is None


def test_percentile_interpolates():
    assert percentile([1.0, 2.0, 3.0, 4.0], 0.5) == 2.5


def test_percent():
    assert pct(49, 50) == 98.0
    assert pct(0, 0) == 0.0

