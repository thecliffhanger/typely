"""@validate decorator."""

import functools
import inspect
from typing import get_type_hints, Any
from typely.errors import ValidationError
from typely.types import _check_type, _is_optional, get_origin, get_args
from typely.validators import run_validators, get_validators
from typely.coerce import Coerce

_ANNOTATED_MARKER = "__typely_validators__"


def _extract_hint_and_validators(annotation, localns=None):
    """Extract (base_type_hint, [validators]) from an annotation.
    
    Supports typing.Annotated[X, validator1, validator2] (Python 3.9+)
    and plain type hints.
    """
    origin = get_origin(annotation)
    if origin is not None and hasattr(origin, "__name__") and origin.__name__ == "Annotated":
        args = get_args(annotation)
        base_type = args[0]
        validator_fns = [a for a in args[1:] if callable(a)]
        return base_type, validator_fns
    return annotation, []


def _validate_return(result, annotations, coerce):
    """Validate return value against annotations. Returns validated result."""
    ret_hint = annotations.get("return")
    if ret_hint is None:
        return result
    base_hint, validators = _extract_hint_and_validators(ret_hint)
    ret_errors = []
    coerced_result = _check_type(result, base_hint, "return", ret_errors, coerce)
    if ret_errors:
        raise ValidationError(ret_errors)
    for vfn in validators:
        coerced_result = vfn(coerced_result)
    if not ret_errors:
        coerced_result = run_validators(coerced_result, base_hint, "return", ret_errors)
    if ret_errors:
        raise ValidationError(ret_errors)
    return coerced_result


def validate(fn=None, *, coerce=Coerce.STRICT):
    """Decorator for runtime type validation of function arguments and return value."""
    
    def decorator(func):
        is_async = inspect.iscoroutinefunction(func)

        def _validate_args(args, kwargs, annotations):
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            errors = []
            new_args = list(args)

            # Validate positional args
            for i, arg_val in enumerate(args):
                if i < len(params):
                    param_name = params[i]
                    if param_name in annotations:
                        hint = annotations[param_name]
                        base_hint, validators = _extract_hint_and_validators(hint)
                        coerced = _check_type(arg_val, base_hint, param_name, errors, coerce)
                        if not errors:
                            for vfn in validators:
                                try:
                                    coerced = vfn(coerced)
                                except (ValueError, TypeError) as e:
                                    errors.append({
                                        "field": param_name,
                                        "expected": vfn.__name__,
                                        "got": type(coerced).__name__,
                                        "value": coerced,
                                        "message": str(e),
                                    })
                                    break
                            if not errors:
                                coerced = run_validators(coerced, base_hint, param_name, errors)
                        new_args[i] = coerced

            # Validate keyword args
            for key, arg_val in kwargs.items():
                if key in annotations:
                    hint = annotations[key]
                    base_hint, validators = _extract_hint_and_validators(hint)
                    coerced = _check_type(arg_val, base_hint, key, errors, coerce)
                    if not errors:
                        for vfn in validators:
                            try:
                                coerced = vfn(coerced)
                            except (ValueError, TypeError) as e:
                                errors.append({
                                    "field": key,
                                    "expected": vfn.__name__,
                                    "got": type(coerced).__name__,
                                    "value": coerced,
                                    "message": str(e),
                                })
                                break
                        if not errors:
                            coerced = run_validators(coerced, base_hint, key, errors)
                    kwargs[key] = coerced

            if errors:
                raise ValidationError(errors)
            return new_args, kwargs

        if is_async:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                annotations = {}
                try:
                    annotations = get_type_hints(func, include_extras=True)
                except Exception:
                    annotations = getattr(func, "__annotations__", {})

                new_args, kwargs = _validate_args(args, kwargs, annotations)
                result = await func(*new_args, **kwargs)
                return _validate_return(result, annotations, coerce)
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                annotations = {}
                try:
                    annotations = get_type_hints(func, include_extras=True)
                except Exception:
                    annotations = getattr(func, "__annotations__", {})

                new_args, kwargs = _validate_args(args, kwargs, annotations)
                result = func(*new_args, **kwargs)
                return _validate_return(result, annotations, coerce)

        return wrapper

    if fn is not None:
        return decorator(fn)
    return decorator
