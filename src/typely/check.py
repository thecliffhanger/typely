"""Type checking utilities."""

from typing import Any
from typely.types import _check_type


def check(value: Any, type_hint: Any) -> bool:
    """Check if value matches type_hint. Returns bool."""
    errors = []
    try:
        _check_type(value, type_hint, field="", errors=errors)
    except Exception:
        return False
    return len(errors) == 0


def is_valid(value: Any, type_hint: Any) -> bool:
    """Check if value matches type_hint. Never raises. Returns bool."""
    try:
        return check(value, type_hint)
    except Exception:
        return False
