import pytest
from app.utils.validators import validate_iso_date


class TestValidateIsoDate:
    def test_valid_date_only(self):
        result = validate_iso_date("2024-03-15")
        assert result == "2024-03-15"

    def test_valid_datetime(self):
        result = validate_iso_date("2024-03-15T14:30:00")
        assert result == "2024-03-15T14:30:00"

    def test_valid_datetime_with_timezone(self):
        result = validate_iso_date("2024-03-15T14:30:00Z")
        assert result == "2024-03-15T14:30:00Z"

    def test_valid_datetime_with_offset(self):
        result = validate_iso_date("2024-03-15T14:30:00+05:00")
        assert result == "2024-03-15T14:30:00+05:00"

    def test_valid_datetime_with_microseconds(self):
        result = validate_iso_date("2024-03-15T14:30:00.123456")
        assert result == "2024-03-15T14:30:00.123456"

    def test_none_returns_none(self):
        result = validate_iso_date(None)
        assert result is None

    def test_invalid_format_raises_error(self):
        with pytest.raises(ValueError):
            validate_iso_date("03/15/2024")

    def test_invalid_string_raises_error(self):
        with pytest.raises(ValueError):
            validate_iso_date("not-a-date")

    def test_empty_string_raises_error(self):
        with pytest.raises(ValueError):
            validate_iso_date("")

    def test_partial_date_raises_error(self):
        with pytest.raises(ValueError):
            validate_iso_date("2024-03")

    def test_invalid_month_raises_error(self):
        with pytest.raises(ValueError):
            validate_iso_date("2024-13-01")

    def test_invalid_day_raises_error(self):
        with pytest.raises(ValueError):
            validate_iso_date("2024-02-30")
