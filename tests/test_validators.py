"""Tests for custom validators."""

import pytest
from typely import validate, validator, ValidationError
from typing import Annotated


class TestValidatorDecorator:

    def setup_method(self):
        # Clear global validators before each test
        from typely.validators import _global_validators
        _global_validators.clear()

    def test_global_validator_int(self):
        @validator(int)
        def positive(v):
            if v <= 0:
                raise ValueError("must be positive")
            return v

        @validate
        def f(x: int): return x

        assert f(5) == 5
        with pytest.raises(ValidationError) as e:
            f(-1)
        assert "must be positive" in str(e.value)

    def test_global_validator_str(self):
        @validator(str)
        def nonempty(v):
            if not v.strip():
                raise ValueError("must be non-empty")
            return v

        @validate
        def f(x: str): return x

        assert f("hello") == "hello"
        with pytest.raises(ValidationError):
            f("   ")

    def test_multiple_validators_same_type(self):
        @validator(int)
        def positive(v):
            if v <= 0:
                raise ValueError("must be positive")
            return v

        @validator(int)
        def small(v):
            if v > 100:
                raise ValueError("must be <= 100")
            return v

        @validate
        def f(x: int): return x

        assert f(50) == 50
        with pytest.raises(ValidationError):
            f(-1)
        with pytest.raises(ValidationError):
            f(200)

    def test_annotated_validator(self):
        """Test using Annotated with validator callables."""
        def positive(v):
            if v <= 0:
                raise ValueError("must be positive")
            return v

        @validate
        def f(x: Annotated[int, positive]): return x

        assert f(5) == 5
        with pytest.raises(ValidationError) as e:
            f(-1)
        assert "must be positive" in str(e.value)

    def test_annotated_multiple_validators(self):
        def positive(v):
            if v <= 0:
                raise ValueError("must be positive")
            return v

        def small(v):
            if v > 100:
                raise ValueError("must be <= 100")
            return v

        @validate
        def f(x: Annotated[int, positive, small]): return x

        assert f(50) == 50
        with pytest.raises(ValidationError):
            f(-1)

    def test_validator_return_value_used(self):
        @validator(int)
        def double(v):
            return v * 2

        @validate
        def f(x: int): return x

        # The validator modifies the value
        assert f(5) == 10

    def test_validator_error_message_in_details(self):
        @validator(int)
        def positive(v):
            if v <= 0:
                raise ValueError("must be positive")
            return v

        @validate
        def f(x: int): return x

        with pytest.raises(ValidationError) as e:
            f(-1)
        assert e.value.errors[0]["message"] == "must be positive"
        assert e.value.errors[0]["expected"] == "positive int"
