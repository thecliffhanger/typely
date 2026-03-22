"""Type handling: Union, Optional, Literal, generics."""

import types
from typing import Any, Union, get_origin, get_args

# Python 3.10+ these are builtins, but we need the typing module versions too
try:
    from types import UnionType
except ImportError:
    UnionType = None


def _type_name(type_hint: Any) -> str:
    """Get a readable name for a type hint."""
    if type_hint is Any:
        return "Any"
    if type_hint is None or type_hint is type(None):
        return "None"
    if type_hint is int:
        return "int"
    if type_hint is float:
        return "float"
    if type_hint is str:
        return "str"
    if type_hint is bool:
        return "bool"
    if type_hint is list:
        return "list"
    if type_hint is dict:
        return "dict"
    if type_hint is tuple:
        return "tuple"
    if type_hint is set:
        return "set"

    origin = get_origin(type_hint)
    if origin is Union:
        args = get_args(type_hint)
        return " | ".join(_type_name(a) for a in args)
    if origin is type(None):
        return "None"
    if origin is list:
        args = get_args(type_hint)
        if args:
            return f"list[{', '.join(_type_name(a) for a in args)}]"
        return "list"
    if origin is dict:
        args = get_args(type_hint)
        if args:
            return f"dict[{', '.join(_type_name(a) for a in args)}]"
        return "dict"
    if origin is tuple:
        args = get_args(type_hint)
        if args:
            names = [_type_name(a) if a is not ... else "..." for a in args]
            return f"tuple[{', '.join(names)}]"
        return "tuple"
    if origin is set:
        args = get_args(type_hint)
        if args:
            return f"set[{', '.join(_type_name(a) for a in args)}]"
        return "set"
    try:
        return getattr(type_hint, "__name__", str(type_hint))
    except Exception:
        return str(type_hint)


def _is_optional(type_hint: Any) -> bool:
    """Check if a type hint allows None."""
    origin = get_origin(type_hint)
    if origin is Union:
        args = get_args(type_hint)
        return type(None) in args
    if UnionType is not None:
        if isinstance(type_hint, UnionType):
            args = type_hint.__args__
            return type(None) in args
    return type_hint is type(None) or type_hint is None


def _is_union(type_hint: Any) -> bool:
    origin = get_origin(type_hint)
    if origin is Union:
        return True
    if UnionType is not None:
        return isinstance(type_hint, UnionType)
    return False


def _union_args(type_hint: Any) -> tuple:
    if UnionType is not None and isinstance(type_hint, UnionType):
        return type_hint.__args__
    return get_args(type_hint)


def _is_literal(type_hint: Any) -> bool:
    origin = get_origin(type_hint)
    return origin is not None and getattr(origin, "__name__", "") == "Literal"


def _literal_values(type_hint: Any) -> tuple:
    return get_args(type_hint)


def _check_type(value: Any, type_hint: Any, field: str, errors: list, coerce: int = 0) -> Any:
    """
    Check if value matches type_hint.
    
    Args:
        value: The value to check
        type_hint: The type hint to check against
        field: Field name for error messages
        errors: List to append errors to
        coerce: Coercion mode (0=STRICT, 1=SAFE)
    
    Returns:
        The (possibly coerced) value
    """
    if type_hint is Any:
        return value

    # None check
    if value is None:
        if _is_optional(type_hint):
            return None
        errors.append({
            "field": field,
            "expected": _type_name(type_hint),
            "got": type(None).__name__,
            "value": None,
            "message": f"expected {_type_name(type_hint)}, got None",
        })
        return None

    # Union
    if _is_union(type_hint):
        args = _union_args(type_hint)
        for arg in args:
            test_errors = []
            try:
                _check_type(value, arg, field, test_errors, coerce)
                if not test_errors:
                    return value
            except Exception:
                continue
        errors.append({
            "field": field,
            "expected": _type_name(type_hint),
            "got": type(value).__name__,
            "value": value,
            "message": f"expected {_type_name(type_hint)}, got {type(value).__name__}",
        })
        return value

    # Literal
    if _is_literal(type_hint):
        allowed = _literal_values(type_hint)
        if value in allowed:
            return value
        errors.append({
            "field": field,
            "expected": _type_name(type_hint),
            "got": type(value).__name__,
            "value": value,
            "message": f"expected {_type_name(type_hint)}, got {value!r}",
        })
        return value

    # Primitives
    if type_hint is int:
        if isinstance(value, bool):
            errors.append({"field": field, "expected": "int", "got": "bool", "value": value,
                           "message": f"expected int, got bool ({value!r})"})
            return value
        if isinstance(value, int):
            return value
        if coerce and isinstance(value, str):
            try:
                return int(value)
            except (ValueError, TypeError):
                pass
        if coerce and isinstance(value, float):
            return int(value)
        errors.append({"field": field, "expected": "int", "got": type(value).__name__, "value": value,
                       "message": f"expected int, got {type(value).__name__} ({value!r})"})
        return value

    if type_hint is float:
        if isinstance(value, bool):
            errors.append({"field": field, "expected": "float", "got": "bool", "value": value,
                           "message": f"expected float, got bool ({value!r})"})
            return value
        if isinstance(value, float):
            return value
        if isinstance(value, int):
            return float(value)
        if coerce and isinstance(value, str):
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
        errors.append({"field": field, "expected": "float", "got": type(value).__name__, "value": value,
                       "message": f"expected float, got {type(value).__name__} ({value!r})"})
        return value

    if type_hint is str:
        if isinstance(value, str):
            return value
        if coerce and isinstance(value, (int, float, bool)):
            return str(value)
        errors.append({"field": field, "expected": "str", "got": type(value).__name__, "value": value,
                       "message": f"expected str, got {type(value).__name__} ({value!r})"})
        return value

    if type_hint is bool:
        if isinstance(value, bool):
            return value
        if coerce and isinstance(value, str):
            if value.lower() in ("true", "1", "yes"):
                return True
            if value.lower() in ("false", "0", "no"):
                return False
        errors.append({"field": field, "expected": "bool", "got": type(value).__name__, "value": value,
                       "message": f"expected bool, got {type(value).__name__} ({value!r})"})
        return value

    # Collections
    origin = get_origin(type_hint)

    if type_hint is list or origin is list:
        if not isinstance(value, list):
            errors.append({"field": field, "expected": _type_name(type_hint), "got": type(value).__name__,
                           "value": value, "message": f"expected {_type_name(type_hint)}, got {type(value).__name__}"})
            return value
        args = get_args(type_hint)
        if args:
            item_hint = args[0]
            result = []
            for i, item in enumerate(value):
                checked = _check_type(item, item_hint, f"{field}[{i}]", errors, coerce)
                result.append(checked)
            return result
        return value

    if type_hint is dict or origin is dict:
        if not isinstance(value, dict):
            errors.append({"field": field, "expected": _type_name(type_hint), "got": type(value).__name__,
                           "value": value, "message": f"expected {_type_name(type_hint)}, got {type(value).__name__}"})
            return value
        args = get_args(type_hint)
        if args and len(args) == 2:
            key_hint, val_hint = args
            result = {}
            for k, v in value.items():
                _check_type(k, key_hint, f"{field}.key({k!r})", errors, coerce)
                checked_v = _check_type(v, val_hint, f"{field}[{k!r}]", errors, coerce)
                result[k] = checked_v
            return result
        return value

    if type_hint is tuple or origin is tuple:
        if not isinstance(value, tuple):
            errors.append({"field": field, "expected": _type_name(type_hint), "got": type(value).__name__,
                           "value": value, "message": f"expected {_type_name(type_hint)}, got {type(value).__name__}"})
            return value
        args = get_args(type_hint)
        if args:
            if len(args) == 2 and args[1] is ...:
                # tuple[T, ...]
                item_hint = args[0]
                result = []
                for i, item in enumerate(value):
                    checked = _check_type(item, item_hint, f"{field}[{i}]", errors, coerce)
                    result.append(checked)
                return tuple(result)
            else:
                # Fixed-length tuple
                if len(value) != len(args):
                    errors.append({"field": field, "expected": f"tuple of length {len(args)}",
                                   "got": f"tuple of length {len(value)}", "value": value,
                                   "message": f"expected tuple of length {len(args)}, got {len(value)}"})
                    return value
                result = []
                for i, (item, hint) in enumerate(zip(value, args)):
                    checked = _check_type(item, hint, f"{field}[{i}]", errors, coerce)
                    result.append(checked)
                return tuple(result)
        return value

    if type_hint is set or origin is set:
        if not isinstance(value, set):
            errors.append({"field": field, "expected": _type_name(type_hint), "got": type(value).__name__,
                           "value": value, "message": f"expected {_type_name(type_hint)}, got {type(value).__name__}"})
            return value
        args = get_args(type_hint)
        if args:
            item_hint = args[0]
            result = set()
            for item in value:
                checked = _check_type(item, item_hint, f"{field}.item", errors, coerce)
                result.add(checked)
            return result
        return value

    # Fallback: isinstance check
    if isinstance(type_hint, type):
        if isinstance(value, type_hint):
            return value
        if isinstance(value, bool) and type_hint is not bool:
            errors.append({"field": field, "expected": type_hint.__name__, "got": "bool", "value": value,
                           "message": f"expected {type_hint.__name__}, got bool ({value!r})"})
            return value
        errors.append({"field": field, "expected": type_hint.__name__, "got": type(value).__name__,
                       "value": value, "message": f"expected {type_hint.__name__}, got {type(value).__name__}"})
        return value

    errors.append({"field": field, "expected": _type_name(type_hint), "got": type(value).__name__,
                   "value": value, "message": f"expected {_type_name(type_hint)}, got {type(value).__name__}"})
    return value
