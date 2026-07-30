import pytest

from src.normalize.date_repair import repair


@pytest.mark.parametrize("text", ["6/78/0047", "13/45/2020", "not a date", ""])
def test_invalid_dates_flagged(text):
    result = repair(text)
    assert result.status in {"suspicious", "unrepairable"}
    if result.status == "unrepairable":
        assert result.parsed is None


@pytest.mark.parametrize("text", ["2025-06-15", "06/15/2025"])
def test_valid_dates_parsed(text):
    result = repair(text)
    assert result.status == "valid"
    assert result.parsed is not None
    assert result.parsed.year == 2025
