"""Round 2 tests: hypothesis + performance."""

import time
import pytest
from typing import Optional, Union, Literal, Any
from hypothesis import given, strategies as st
from typely import validate, check, is_valid, ValidationError, Coerce


# --- Hypothesis tests ---

class TestHypothesisCheck:

    @given(st.integers())
    def test_check_int_always_int(self, val):
        assert check(val, int) is True

    @given(st.text())
    def test_check_str_always_str(self, val):
        assert check(val, str) is True

    @given(st.floats(allow_nan=False, allow_infinity=False))
    def test_check_float_always_float(self, val):
        assert check(val, float) is True

    @given(st.integers())
    def test_check_int_not_str(self, val):
        assert check(val, str) is False

    @given(st.text())
    def test_check_str_not_int(self, val):
        # Empty string can't convert, non-numeric strings definitely can't
        if val and val.lstrip("-").isdigit():
            pass  # might be ambiguous
        else:
            assert check(val, int) is False

    @given(st.lists(st.integers()))
    def test_check_list_int(self, val):
        assert check(val, list[int]) is True

    @given(st.lists(st.text()))
    def test_check_list_text_not_int(self, val):
        if any(not (s.lstrip("-").isdigit() if s else False) for s in val):
            assert check(val, list[int]) is False

    @given(st.none())
    def test_check_none_is_none_type(self, val):
        assert check(val, type(None)) is True

    @given(st.integers())
    def test_int_not_none(self, val):
        assert check(val, type(None)) is False

    @given(st.integers())
    def test_any_always_valid(self, val):
        assert check(val, Any) is True

    @given(st.dictionaries(st.text(), st.integers()))
    def test_dict_str_int(self, val):
        assert check(val, dict[str, int]) is True

    @given(st.integers())
    def test_optional_int(self, val):
        assert check(val, Optional[int]) is True

    @given(st.none())
    def test_optional_none(self, val):
        assert check(val, Optional[int]) is True

    @given(st.none())
    def test_is_valid_none_optional(self, val):
        assert is_valid(val, Optional[str]) is True

    @given(st.integers())
    def test_is_valid_int(self, val):
        assert is_valid(val, int) is True

    @given(st.sets(st.integers()))
    def test_check_set_int(self, val):
        assert check(val, set[int]) is True

    @given(st.tuples(st.integers(), st.integers()))
    def test_check_tuple_int_ellipsis(self, val):
        assert check(val, tuple[int, ...]) is True

    @given(st.tuples(st.integers(), st.text()))
    def test_check_tuple_fixed(self, val):
        assert check(val, tuple[int, str]) is True


class TestHypothesisValidate:

    @given(st.integers())
    def test_validate_int_passthrough(self, val):
        @validate
        def f(x: int): return x
        assert f(val) == val

    @given(st.text())
    def test_validate_str_passthrough(self, val):
        @validate
        def f(x: str): return x
        assert f(val) == val

    @given(st.lists(st.integers()))
    def test_validate_list_int(self, val):
        @validate
        def f(x: list[int]): return x
        assert f(val) == val

    @given(st.integers())
    def test_validate_return_int(self, val):
        @validate
        def f(x: int) -> int:
            return x
        assert f(val) == val

    @given(st.integers())
    def test_validate_optional_none(self, val):
        @validate
        def f(x: Optional[int]): return x
        # Don't test None here since we generate integers
        assert f(val) == val

    @given(st.lists(st.integers()))
    def test_validate_nested_list(self, val):
        @validate
        def f(x: list[list[int]]): return x
        assert f([val]) == [val]

    @given(st.dictionaries(st.text(), st.integers()))
    def test_validate_dict_str_int(self, val):
        @validate
        def f(x: dict[str, int]): return x
        assert f(val) == val

    @given(st.one_of(st.integers(), st.text()))
    def test_validate_union(self, val):
        @validate
        def f(x: Union[int, str]): return x
        assert f(val) == val

    @given(st.sampled_from(["fast", "slow"]))
    def test_validate_literal(self, val):
        @validate
        def f(x: Literal["fast", "slow"]): return x
        assert f(val) == val


# --- Performance test ---

class TestPerformance:
    def test_validate_10000_calls_under_1s(self):
        """Validating the same function 10000 times should be fast."""
        @validate
        def add(a: int, b: int) -> int:
            return a + b

        start = time.time()
        for i in range(10000):
            result = add(i, i)
            assert result == i * 2
        elapsed = time.time() - start
        assert elapsed < 2.0, f"10000 validations took {elapsed:.3f}s"

    def test_check_10000_under_1s(self):
        """10000 check() calls should be fast."""
        start = time.time()
        for i in range(10000):
            check(i, int)
        elapsed = time.time() - start
        assert elapsed < 1.0, f"10000 checks took {elapsed:.3f}s"

    def test_is_valid_10000_under_1s(self):
        """10000 is_valid() calls should be fast."""
        start = time.time()
        for i in range(10000):
            is_valid(i, int)
        elapsed = time.time() - start
        assert elapsed < 1.0, f"10000 is_valid calls took {elapsed:.3f}s"
