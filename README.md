# typely

Runtime type validation for Python — lightweight, fast, decorator-based.

## Install

```bash
pip install -e .
```

## Quick Start

```python
from typely import validate

@validate
def create_user(name: str, age: int) -> dict:
    return {"name": name, "age": age}

create_user("Alice", 30)  # ✅
create_user("Alice", "30")  # TypeError: age must be int, got str
```

## Features

- **Decorator validation** — `@validate` validates args and return values at call time
- **Advanced types** — `Optional`, `Union`, `Literal`, generics (`list[int]`, `dict[str, float]`)
- **Custom validators** — `@validator(int)` to add custom checks
- **Coercion** — `Coerce.SAFE` for str→int, str→float, etc.
- **Schema validation** — `Schema({field: Field(...)})` for dict validation
- **Standalone checks** — `typely.check(value, type_hint)` and `typely.is_valid()`
- **Zero dependencies** — stdlib only

## License

MIT
