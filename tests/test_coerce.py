"""Tests for Coerce module."""

import pytest
from typely import Coerce


class TestCoerceEnum:

    def test_strict_value(self):
        assert Coerce.STRICT == 0

    def test_safe_value(self):
        assert Coerce.SAFE == 1

    def test_comparison(self):
        assert Coerce.SAFE > Coerce.STRICT
