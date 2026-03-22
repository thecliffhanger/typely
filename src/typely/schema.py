"""Schema and Field for dict validation."""

from typing import Any, Callable, Optional
from typely.errors import SchemaError
from typely.types import _check_type, _type_name
from typely.coerce import Coerce


class Field:
    """A field definition for Schema validation."""

    def __init__(self, type_hint: Any, *, required: bool = False, default: Any = None,
                 validators: list = None):
        self.type_hint = type_hint
        self.required = required
        self.default = default
        self.validators = validators or []


class Schema:
    """Dict/data validation schema."""

    def __init__(self, fields: dict, *, coerce=Coerce.STRICT):
        self.fields = fields  # name -> Field
        self.coerce = coerce

    def validate(self, data: dict) -> dict:
        """Validate data against schema. Returns (possibly coerced) data dict."""
        if not isinstance(data, dict):
            raise SchemaError([{
                "field": "data",
                "expected": "dict",
                "got": type(data).__name__,
                "value": data,
                "message": f"expected dict, got {type(data).__name__}",
            }])

        errors = []
        result = {}

        # Check required fields and validate present fields
        for name, field in self.fields.items():
            if name not in data:
                if field.required:
                    errors.append({
                        "field": name,
                        "expected": _type_name(field.type_hint),
                        "got": "missing",
                        "value": None,
                        "message": f"required field '{name}' is missing",
                    })
                else:
                    result[name] = field.default
            else:
                value = data[name]
                checked = _check_type(value, field.type_hint, name, errors, self.coerce)
                if not errors:
                    for vfn in field.validators:
                        try:
                            checked = vfn(checked)
                        except (ValueError, TypeError) as e:
                            errors.append({
                                "field": name,
                                "expected": vfn.__name__,
                                "got": type(checked).__name__,
                                "value": checked,
                                "message": str(e),
                            })
                            break
                result[name] = checked

        if errors:
            raise SchemaError(errors)

        return result
