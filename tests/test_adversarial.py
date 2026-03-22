"""Adversarial tests for typely."""

import pytest
from typing import Optional, Union, Literal, List, Dict, Tuple, Set, Any
from typely import validate, check, is_valid, Coerce, Schema, Field, ValidationError, validator


# --- None to non-Optional ---

def test_none_to_non_optional():
    assert not check(None, int)
    assert not check(None, str)
    assert not check(None, list)
    assert check(None, Optional[int])
    assert check(None, Union[int, None])


# --- STRICT mode rejects coercible types ---

@validate(coerce=Coerce.STRICT)
def strict_fn(x: int) -> int:
    return x

def test_strict_rejects_string():
    with pytest.raises(ValidationError):
        strict_fn("42")

def test_strict_rejects_float():
    with pytest.raises(ValidationError):
        strict_fn(3.14)


# --- Deeply nested types ---

DeepType = Dict[str, List[Dict[str, List[Dict[str, int]]]]]

def test_deeply_nested_valid():
    val = {"a": [{"b": [{"c": 1}, {"c": 2}]}]}
    assert check(val, DeepType)

def test_deeply_nested_invalid():
    val = {"a": [{"b": [{"c": "oops"}]}]}
    assert not check(val, DeepType)


# --- Union with many types ---

def test_union_many_types():
    hint = Union[int, str, float, bool, list, dict, tuple, set, bytes, type(None)]
    assert check(42, hint)
    assert check("hi", hint)
    assert check(3.14, hint)
    assert check(True, hint)
    assert check([1], hint)
    assert check(None, hint)
    assert not check(object(), hint)


# --- Literal with many values ---

def test_literal_many_values():
    hint = Literal["a", "b", "c", "d", "e", "f", "g", "h"]
    assert check("a", hint)
    assert check("h", hint)
    assert not check("z", hint)


# --- Custom class without annotations ---

class NoAnnotations:
    pass

def test_custom_class():
    assert check(NoAnnotations(), NoAnnotations)
    assert not check("not a class", NoAnnotations)


# --- Function with *args, **kwargs ---

def test_args_kwargs():
    # *args and **kwargs annotations map to var-positional and var-keyword params.
    # Typely validates positional args against param names; *args/**kwargs are special.
    @validate
    def fn(x: int, *args, **kwargs: str) -> int:
        return x
    assert fn(5) == 5
    with pytest.raises(ValidationError):
        fn("not_int")


# --- Function with no annotations ---

@validate
def no_annot_fn(a, b, c):
    return a + b + c

def test_no_annotations():
    assert no_annot_fn(1, 2, 3) == 6


# --- Async function ---

@validate
async def async_fn(x: int) -> int:
    return x + 1

def test_async_function():
    import asyncio
    result = asyncio.get_event_loop().run_until_complete(async_fn(5))
    assert result == 6


# --- Generator return type ---

@validate
def gen_fn(n: int):
    for i in range(n):
        yield i

def test_generator():
    g = gen_fn(3)
    assert list(g) == [0, 1, 2]


# --- Class method, static method, property ---

class MyClass:
    @validate
    def method(self, x: int) -> int:
        return x * 2

    @classmethod
    @validate
    def cmethod(cls, x: str) -> str:
        return x.upper()

    @staticmethod
    @validate
    def smethod(x: int) -> int:
        return x + 1

obj = MyClass()

def test_instance_method():
    assert obj.method(5) == 10

def test_classmethod():
    assert MyClass.cmethod("hi") == "HI"

def test_staticmethod():
    assert MyClass.smethod(5) == 6


# --- Schema with conflicting validators ---

def raise_err(val):
    raise ValueError("always fails")

def raise_err2(val):
    raise ValueError("also fails")

def test_schema_conflicting_validators():
    s = Schema({
        "x": Field(int, required=True, validators=[raise_err, raise_err2])
    })
    with pytest.raises(ValidationError) as exc_info:
        s.validate({"x": 42})
    assert "always fails" in str(exc_info.value)


# --- Schema deeply nested ---

def test_schema_deeply_nested():
    s = Schema({
        "data": Field(Dict[str, List[int]], required=True)
    })
    assert s.validate({"data": {"a": [1, 2], "b": [3]}}) == {"data": {"a": [1, 2], "b": [3]}}
    with pytest.raises(ValidationError):
        s.validate({"data": {"a": [1, "bad"]}})


# --- Coercion edge cases ---

def test_nan_string_to_float():
    # "nan" is a valid float string in Python
    import math
    @validate(coerce=Coerce.SAFE)
    def safe_float(x: float) -> float:
        return x
    result = safe_float("nan")
    assert math.isnan(result)
    result = safe_float("inf")
    assert math.isinf(result)

def test_empty_string_to_int():
    assert not check("", int)  # strict
    @validate(coerce=Coerce.SAFE)
    def safe_int(x: int) -> int:
        return x
    with pytest.raises(ValidationError):
        safe_int("")


# --- Very long strings, large lists ---

def test_long_string():
    s = "a" * 1_000_000
    assert check(s, str)

def test_large_list():
    lst = list(range(10_000))
    assert check(lst, list[int])
    assert not check(lst + ["bad"], list[int])


# --- Bool is not int ---

def test_bool_not_int():
    assert not check(True, int)
    assert not check(False, int)
    assert check(True, bool)
    assert check(1, int)


# --- Empty collections ---

def test_empty_collections():
    assert check([], list[int])
    assert check({}, dict[str, int])
    assert check(set(), set[int])
    assert check((), tuple[int, ...])


# --- Nested Optional ---

def test_nested_optional():
    assert check(None, Optional[List[int]])
    assert check([1, 2], Optional[List[int]])
    assert not check([1, "bad"], Optional[List[int]])


# --- bytes type ---

def test_bytes_type():
    assert check(b"hello", bytes)
    assert not check("hello", bytes)


# --- Coerce int to float always works (even strict) ---

def test_int_to_float_always():
    # This is a design choice: int→float is implicit
    assert check(42, float)


# --- Union with None first ---

def test_union_none_first():
    hint = Union[None, int, str]
    assert check(None, hint)
    assert check(42, hint)
    assert check("hi", hint)
