"""Safe type coercion."""

from enum import IntEnum


class Coerce(IntEnum):
    STRICT = 0
    SAFE = 1
