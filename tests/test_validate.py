"""Tests for @validate decorator."""

import pytest
from typely import validate, ValidationError, Coerce
from typing import Optional, Union, Literal, Any


# --- Basic primitives ---

class TestBasicTypes:

    def test_int_valid(self):
        @validate
        def f(x: int): return x
        assert f(5) == 5

    def test_int_invalid(self):
        @validate
        def f(x: int): return x
        with pytest.raises(ValidationError):
            f("hello")

    def test_float_valid(self):
        @validate
        def f(x: float): return x
        assert f(3.14) == 3.14

    def test_float_invalid(self):
        @validate
        def f(x: float): return x
        with pytest.raises(ValidationError):
            f("hello")

    def test_str_valid(self):
        @validate
        def f(x: str): return x
        assert f("hello") == "hello"

    def test_str_invalid(self):
        @validate
        def f(x: str): return x
        with pytest.raises(ValidationError):
            f(42)

    def test_bool_valid(self):
        @validate
        def f(x: bool): return x
        assert f(True) is True
        assert f(False) is False

    def test_bool_rejects_int(self):
        """bool is subclass of int in Python, but typely should reject int for bool."""
        @validate
        def f(x: bool): return x
        # True/False are bools, 0 and 1 are ints
        with pytest.raises(ValidationError):
            f(0)
        with pytest.raises(ValidationError):
            f(1)

    def test_none_valid(self):
        @validate
        def f(x: type(None)): return x
        assert f(None) is None

    def test_none_invalid(self):
        @validate
        def f(x: type(None)): return x
        with pytest.raises(ValidationError):
            f(42)

    def test_any_always_valid(self):
        @validate
        def f(x: Any): return x
        assert f("anything") == "anything"
        assert f(42) == 42
        assert f(None) is None

    def test_no_annotations(self):
        @validate
        def f(x): return x
        assert f("anything") == "anything"


class TestMultipleArgs:

    def test_multiple_valid(self):
        @validate
        def f(a: int, b: str, c: float): return (a, b, c)
        assert f(1, "hi", 3.0) == (1, "hi", 3.0)

    def test_multiple_invalid_one(self):
        @validate
        def f(a: int, b: str): return (a, b)
        with pytest.raises(ValidationError) as e:
            f("bad", 123)
        assert len(e.value.errors) == 2

    def test_kwargs_valid(self):
        @validate
        def f(a: int, b: str): return (a, b)
        assert f(a=1, b="hi") == (1, "hi")

    def test_kwargs_invalid(self):
        @validate
        def f(a: int, b: str): return (a, b)
        with pytest.raises(ValidationError):
            f(a="bad", b=123)


class TestReturnValidation:

    def test_return_valid(self):
        @validate
        def f(x: int) -> int:
            return x
        assert f(5) == 5

    def test_return_invalid(self):
        @validate
        def f(x: int) -> str:
            return x  # returns int, expects str
        with pytest.raises(ValidationError):
            f(5)

    def test_return_none_when_not_annotated(self):
        @validate
        def f(x): return None
        assert f(1) is None


class TestOptional:

    def test_optional_valid_with_value(self):
        @validate
        def f(x: Optional[int]): return x
        assert f(5) == 5

    def test_optional_valid_with_none(self):
        @validate
        def f(x: Optional[int]): return x
        assert f(None) is None

    def test_optional_invalid(self):
        @validate
        def f(x: Optional[int]): return x
        with pytest.raises(ValidationError):
            f("bad")

    def test_optional_str(self):
        @validate
        def f(x: str | None): return x
        assert f(None) is None
        assert f("hi") == "hi"


class TestUnion:

    def test_union_first_type(self):
        @validate
        def f(x: Union[int, str]): return x
        assert f(5) == 5

    def test_union_second_type(self):
        @validate
        def f(x: Union[int, str]): return x
        assert f("hi") == "hi"

    def test_union_invalid(self):
        @validate
        def f(x: Union[int, str]): return x
        with pytest.raises(ValidationError):
            f([])


class TestLiteral:

    def test_literal_valid(self):
        @validate
        def f(x: Literal["a", "b", "c"]): return x
        assert f("a") == "a"
        assert f("c") == "c"

    def test_literal_invalid(self):
        @validate
        def f(x: Literal["a", "b"]): return x
        with pytest.raises(ValidationError):
            f("c")

    def test_literal_int(self):
        @validate
        def f(x: Literal[1, 2, 3]): return x
        assert f(2) == 2
        with pytest.raises(ValidationError):
            f(4)


class TestCollections:

    def test_list_valid(self):
        @validate
        def f(x: list): return x
        assert f([1, 2, 3]) == [1, 2, 3]

    def test_list_invalid(self):
        @validate
        def f(x: list): return x
        with pytest.raises(ValidationError):
            f("not a list")

    def test_list_int_valid(self):
        @validate
        def f(x: list[int]): return x
        assert f([1, 2, 3]) == [1, 2, 3]

    def test_list_int_invalid_item(self):
        @validate
        def f(x: list[int]): return x
        with pytest.raises(ValidationError):
            f([1, "bad", 3])

    def test_dict_valid(self):
        @validate
        def f(x: dict): return x
        assert f({"a": 1}) == {"a": 1}

    def test_dict_str_int_valid(self):
        @validate
        def f(x: dict[str, int]): return x
        assert f({"a": 1, "b": 2}) == {"a": 1, "b": 2}

    def test_dict_str_int_invalid_value(self):
        @validate
        def f(x: dict[str, int]): return x
        with pytest.raises(ValidationError):
            f({"a": "bad"})

    def test_dict_str_int_invalid_key(self):
        @validate
        def f(x: dict[str, int]): return x
        with pytest.raises(ValidationError):
            f({1: "a"})

    def test_tuple_valid(self):
        @validate
        def f(x: tuple): return x
        assert f((1, 2)) == (1, 2)

    def test_tuple_int_ellipsis_valid(self):
        @validate
        def f(x: tuple[int, ...]): return x
        assert f((1, 2, 3)) == (1, 2, 3)

    def test_tuple_int_ellipsis_invalid(self):
        @validate
        def f(x: tuple[int, ...]): return x
        with pytest.raises(ValidationError):
            f((1, "bad", 3))

    def test_tuple_fixed_valid(self):
        @validate
        def f(x: tuple[int, str]): return x
        assert f((1, "hi")) == (1, "hi")

    def test_tuple_fixed_wrong_length(self):
        @validate
        def f(x: tuple[int, str]): return x
        with pytest.raises(ValidationError):
            f((1, "hi", 3))

    def test_set_valid(self):
        @validate
        def f(x: set): return x
        assert f({1, 2}) == {1, 2}

    def test_set_str_valid(self):
        @validate
        def f(x: set[str]): return x
        assert f({"a", "b"}) == {"a", "b"}


class TestNested:

    def test_dict_of_list_int(self):
        @validate
        def f(x: dict[str, list[int]]): return x
        assert f({"a": [1, 2], "b": [3]}) == {"a": [1, 2], "b": [3]}

    def test_dict_of_list_int_invalid(self):
        @validate
        def f(x: dict[str, list[int]]): return x
        with pytest.raises(ValidationError):
            f({"a": [1, "bad"]})

    def test_optional_list_of_dict(self):
        @validate
        def f(x: Optional[list[dict[str, str]]]): return x
        assert f(None) is None
        assert f([{"a": "b"}]) == [{"a": "b"}]

    def test_optional_list_of_dict_invalid(self):
        @validate
        def f(x: Optional[list[dict[str, str]]]): return x
        with pytest.raises(ValidationError):
            f([{"a": 1}])


class TestCoercion:

    def test_coerce_safe_str_to_int(self):
        @validate(coerce=Coerce.SAFE)
        def f(x: int): return x
        assert f("42") == 42

    def test_coerce_safe_str_to_float(self):
        @validate(coerce=Coerce.SAFE)
        def f(x: float): return x
        assert f("3.14") == 3.14

    def test_coerce_safe_str_to_bool(self):
        @validate(coerce=Coerce.SAFE)
        def f(x: bool): return x
        assert f("true") is True
        assert f("false") is False

    def test_coerce_safe_int_to_float(self):
        @validate(coerce=Coerce.SAFE)
        def f(x: float): return x
        assert f(42) == 42.0

    def test_coerce_strict_no_coercion(self):
        @validate(coerce=Coerce.STRICT)
        def f(x: int): return x
        with pytest.raises(ValidationError):
            f("42")

    def test_coerce_invalid_str_to_int(self):
        @validate(coerce=Coerce.SAFE)
        def f(x: int): return x
        with pytest.raises(ValidationError):
            f("not a number")


class TestErrorDetails:

    def test_error_list_structure(self):
        @validate
        def f(x: int): return x
        with pytest.raises(ValidationError) as e:
            f("bad")
        errors = e.value.errors
        assert len(errors) == 1
        assert errors[0]["field"] == "x"
        assert errors[0]["expected"] == "int"
        assert errors[0]["got"] == "str"
        assert errors[0]["value"] == "bad"

    def test_pretty_output(self):
        @validate
        def f(x: int): return x
        with pytest.raises(ValidationError) as e:
            f("bad")
        pretty = e.value.pretty()
        assert "x:" in pretty
        assert "int" in pretty
