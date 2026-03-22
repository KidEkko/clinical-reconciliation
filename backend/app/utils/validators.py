from datetime import datetime


def validate_iso_date(value: str | None) -> str | None:
    """Validates that a string is in ISO 8601 format."""
    if value is None:
        return value
    datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value
