"""Tests for typely.check() and typely.is_valid()."""

import pytest
from typing import Optional, Union, Literal, Any
from typely import check, is_valid


class TestCheck:

    def test_check_int(self):
        assert check(5, int) is True
        assert check("5", int) is False

    def test_check_str(self):
        assert check("hi", str) is True
        assert check(5, str) is False

    def test_check_float(self):
        assert check(3.14, float) is True
        assert check("hi", float) is False

    def test_check_bool(self):
        assert check(True, bool) is True
        assert check(1, bool) is False

    def test_check_none(self):
        assert check(None, type(None)) is True
        assert check(None, int) is False

    def test_check_any(self):
        assert check("anything", Any) is True
        assert check(42, Any) is True
        assert check(None, Any) is True

    def test_check_optional(self):
        assert check(None, Optional[int]) is True
        assert check(5, Optional[int]) is True
        assert check("bad", Optional[int]) is False

    def test_check_union(self):
        assert check(5, Union[int, str]) is True
        assert check("hi", Union[int, str]) is True
        assert check([], Union[int, str]) is False

    def test_check_literal(self):
        assert check("a", Literal["a", "b"]) is True
        assert check("c", Literal["a", "b"]) is False

    def test_check_list_int(self):
        assert check([1, 2, 3], list[int]) is True
        assert check([1, "bad"], list[int]) is False

    def test_check_dict_str_int(self):
        assert check({"a": 1}, dict[str, int]) is True
        assert check({"a": "bad"}, dict[str, int]) is False

    def test_check_nested(self):
        assert check({"a": [1, 2]}, dict[str, list[int]]) is True
        assert check({"a": [1, "bad"]}, dict[str, list[int]]) is False

    def test_check_set(self):
        assert check({1, 2}, set[int]) is True
        assert check({1, "bad"}, set[int]) is False

    def test_check_tuple_ellipsis(self):
        assert check((1, 2, 3), tuple[int, ...]) is True
        assert check((1, "bad"), tuple[int, ...]) is False

    def test_check_tuple_fixed(self):
        assert check((1, "hi"), tuple[int, str]) is True
        assert check((1, 2), tuple[int, str]) is False


class TestIsValid:

    def test_is_valid_true(self):
        assert is_valid(5, int) is True

    def test_is_valid_false(self):
        assert is_valid("bad", int) is False

    def test_is_valid_never_raises(self):
        """is_valid should never raise, even with weird inputs."""
        assert is_valid(5, "not a type") is False
        assert is_valid(None, int) is False

    def test_is_valid_none_optional(self):
        assert is_valid(None, Optional[str]) is True
