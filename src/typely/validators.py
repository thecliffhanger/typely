"""Custom validators."""

# Global validator registry: type -> list of validator callables
_global_validators: dict = {}


def validator(target_type):
    """Decorator to register a custom validator for a type."""
    def decorator(fn):
        if target_type not in _global_validators:
            _global_validators[target_type] = []
        _global_validators[target_type].append(fn)
        # Create an Annotated-like marker for use in annotations
        fn._typely_target_type = target_type
        fn._typely_name = fn.__name__
        return fn
    return decorator


def get_validators(type_hint):
    """Get validators for a type hint."""
    return _global_validators.get(type_hint, [])


def run_validators(value, type_hint, field: str, errors: list):
    """Run all registered validators for a type hint. Returns value or raises."""
    validators = get_validators(type_hint)
    for vfn in validators:
        try:
            value = vfn(value)
        except (ValueError, TypeError) as e:
            errors.append({
                "field": field,
                "expected": f"{vfn._typely_name} {_type_name_for(type_hint)}",
                "got": type(value).__name__,
                "value": value,
                "message": str(e),
            })
            break
    return value


def _type_name_for(t):
    from typely.types import _type_name
    return _type_name(t)
