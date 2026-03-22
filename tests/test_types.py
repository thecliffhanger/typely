"""Tests for advanced type handling: Union, Optional, Literal."""

import pytest
from typing import Optional, Union, Literal
from typely import validate, ValidationError, check


class TestUnionTypes:

    def test_union_int_str_int(self):
        @validate
        def f(x: Union[int, str]): return x
        assert f(42) == 42

    def test_union_int_str_str(self):
        @validate
        def f(x: Union[int, str]): return x
        assert f("hi") == "hi"

    def test_union_int_str_list_fails(self):
        @validate
        def f(x: Union[int, str]): return x
        with pytest.raises(ValidationError):
            f([1, 2])

    def test_union_none_types(self):
        @validate
        def f(x: Union[int, None]): return x
        assert f(None) is None
        assert f(5) == 5

    def test_union_three_types(self):
        @validate
        def f(x: Union[int, str, float]): return x
        assert f(42) == 42
        assert f("hi") == "hi"
        assert f(3.14) == 3.14
        with pytest.raises(ValidationError):
            f([])

    def test_check_union(self):
        assert check(5, Union[int, str]) is True
        assert check("hi", Union[int, str]) is True
        assert check(None, Union[int, str]) is False


class TestOptionalTypes:

    def test_optional_int_none(self):
        @validate
        def f(x: Optional[int]): return x
        assert f(None) is None

    def test_optional_int_value(self):
        @validate
        def f(x: Optional[int]): return x
        assert f(42) == 42

    def test_optional_int_str_fails(self):
        @validate
        def f(x: Optional[int]): return x
        with pytest.raises(ValidationError):
            f("bad")

    def test_optional_list_none(self):
        @validate
        def f(x: Optional[list[int]]): return x
        assert f(None) is None

    def test_optional_list_value(self):
        @validate
        def f(x: Optional[list[int]]): return x
        assert f([1, 2, 3]) == [1, 2, 3]

    def test_optional_list_invalid_item(self):
        @validate
        def f(x: Optional[list[int]]): return x
        with pytest.raises(ValidationError):
            f([1, "bad"])

    def test_pipe_syntax(self):
        """Test Python 3.10+ X | Y syntax."""
        @validate
        def f(x: int | None): return x
        assert f(None) is None
        assert f(5) == 5

    def test_check_optional(self):
        assert check(None, Optional[int]) is True
        assert check(5, Optional[int]) is True
        assert check("bad", Optional[int]) is False


class TestLiteralTypes:

    def test_literal_strings(self):
        @validate
        def f(x: Literal["red", "green", "blue"]): return x
        assert f("red") == "red"
        assert f("blue") == "blue"
        with pytest.raises(ValidationError):
            f("yellow")

    def test_literal_ints(self):
        @validate
        def f(x: Literal[1, 2, 3]): return x
        assert f(1) == 1
        assert f(3) == 3
        with pytest.raises(ValidationError):
            f(4)

    def test_literal_mixed(self):
        @validate
        def f(x: Literal["yes", "no", 1, 0]): return x
        assert f("yes") == "yes"
        assert f(1) == 1
        with pytest.raises(ValidationError):
            f("maybe")

    def test_literal_bool(self):
        @validate
        def f(x: Literal[True]): return x
        assert f(True) is True
        with pytest.raises(ValidationError):
            f(False)

    def test_check_literal(self):
        assert check("a", Literal["a", "b"]) is True
        assert check("c", Literal["a", "b"]) is False
        assert check(1, Literal[1, 2]) is True
        assert check(3, Literal[1, 2]) is False


class TestEdgeCases:

    def test_empty_list(self):
        @validate
        def f(x: list[int]): return x
        assert f([]) == []

    def test_empty_dict(self):
        @validate
        def f(x: dict[str, int]): return x
        assert f({}) == {}

    def test_empty_tuple(self):
        @validate
        def f(x: tuple[int, ...]): return x
        assert f(()) == ()

    def test_empty_set(self):
        @validate
        def f(x: set[int]): return x
        assert f(set()) == set()

    def test_nested_empty(self):
        @validate
        def f(x: dict[str, list[int]]): return x
        assert f({}) == {}
        assert f({"a": []}) == {"a": []}

    def test_bool_not_int(self):
        """bool should not pass int validation."""
        @validate
        def f(x: int): return x
        with pytest.raises(ValidationError):
            f(True)
        with pytest.raises(ValidationError):
            f(False)

    def test_list_of_lists(self):
        @validate
        def f(x: list[list[int]]): return x
        assert f([[1, 2], [3]]) == [[1, 2], [3]]
        with pytest.raises(ValidationError):
            f([[1, "bad"]])

    def test_complex_nested(self):
        @validate
        def f(x: dict[str, list[dict[str, int]]]): return x
        assert f({"a": [{"x": 1}]}) == {"a": [{"x": 1}]}
        with pytest.raises(ValidationError):
            f({"a": [{"x": "bad"}]})

    def test_return_optional_none(self):
        @validate
        def f(x: int) -> Optional[int]:
            if x < 0:
                return None
            return x
        assert f(5) == 5
        assert f(-1) is None
