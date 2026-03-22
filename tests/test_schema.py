"""Tests for Schema and Field."""

import pytest
from typely import Schema, Field, SchemaError, validator
from typing import Optional


class TestField:

    def test_field_creation(self):
        f = Field(int, required=True)
        assert f.type_hint is int
        assert f.required is True
        assert f.default is None

    def test_field_with_default(self):
        f = Field(str, default="hello")
        assert f.default == "hello"


class TestSchema:

    def setup_method(self):
        from typely.validators import _global_validators
        _global_validators.clear()

    def test_valid_data(self):
        schema = Schema({
            "name": Field(str, required=True),
            "age": Field(int, required=True),
        })
        result = schema.validate({"name": "Alice", "age": 30})
        assert result == {"name": "Alice", "age": 30}

    def test_missing_required(self):
        schema = Schema({
            "name": Field(str, required=True),
            "age": Field(int, required=True),
        })
        with pytest.raises(SchemaError) as e:
            schema.validate({"name": "Alice"})
        assert any("missing" in err["message"] for err in e.value.errors)

    def test_default_value(self):
        schema = Schema({
            "name": Field(str, required=True),
            "bio": Field(str, default=""),
        })
        result = schema.validate({"name": "Alice"})
        assert result["bio"] == ""

    def test_default_list(self):
        schema = Schema({
            "name": Field(str, required=True),
            "tags": Field(list[str], default=[]),
        })
        result = schema.validate({"name": "Alice"})
        assert result["tags"] == []

    def test_invalid_type(self):
        schema = Schema({
            "age": Field(int, required=True),
        })
        with pytest.raises(SchemaError):
            schema.validate({"age": "not int"})

    def test_field_validators(self):
        @validator(int)
        def positive(v):
            if v <= 0:
                raise ValueError("must be positive")
            return v

        schema = Schema({
            "age": Field(int, required=True, validators=[positive]),
        })
        result = schema.validate({"age": 25})
        assert result["age"] == 25
        with pytest.raises(SchemaError):
            schema.validate({"age": -1})

    def test_non_dict_input(self):
        schema = Schema({"x": Field(int, required=True)})
        with pytest.raises(SchemaError):
            schema.validate("not a dict")

    def test_extra_fields_ignored(self):
        schema = Schema({
            "name": Field(str, required=True),
        })
        result = schema.validate({"name": "Alice", "extra": "ignored"})
        assert result["name"] == "Alice"
        assert "extra" not in result

    def test_nested_type_validation(self):
        schema = Schema({
            "scores": Field(dict[str, int], required=True),
        })
        result = schema.validate({"scores": {"math": 90, "eng": 85}})
        assert result == {"scores": {"math": 90, "eng": 85}}
        with pytest.raises(SchemaError):
            schema.validate({"scores": {"math": "bad"}})

    def test_optional_field_with_none(self):
        schema = Schema({
            "bio": Field(Optional[str], default=None),
        })
        result = schema.validate({"bio": None})
        assert result["bio"] is None

    def test_optional_field_with_value(self):
        schema = Schema({
            "bio": Field(Optional[str], default=None),
        })
        result = schema.validate({"bio": "hello"})
        assert result["bio"] == "hello"

    def test_schema_error_is_validation_error(self):
        from typely import ValidationError
        schema = Schema({"x": Field(int, required=True)})
        with pytest.raises(ValidationError):
            schema.validate({"x": "bad"})
