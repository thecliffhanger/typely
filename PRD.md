# PRD — typely v1.0

## What It Is
Runtime type validation for Python with zero dependencies. Decorator-based, fast, and developer-friendly. Like pydantic for functions, but lightweight.

## Why It Matters
- `pydantic` is the king but pulls in massive dependencies
- `typeguard` exists but verbose
- Python's type hints are everywhere but ignored at runtime
- People want validation without the weight of a full ORM/framework
- FastAPI made type validation mainstream — this brings it to any project

## Core Features

### 1. Decorator validation
```python
from typely import validate

@validate
def create_user(name: str, age: int, email: str) -> dict:
    return {"name": name, "age": age}

create_user("Alice", 30, "alice@example.com")  # ✅
create_user("Alice", "30", "alice@example.com")  # TypeError: age must be int, got str
```

### 2. Advanced types
```python
from typely import validate, Optional, Union, Literal

@validate
def process(data: Optional[dict[str, int]], mode: Literal["fast", "slow"]) -> Union[int, str]:
    ...

process(None, "fast")      # ✅
process({"a": 1}, "slow")  # ✅
process("bad", "fast")     # TypeError
```

### 3. List/Dict generics
```python
@validate
def add_scores(scores: list[int]) -> int:
    return sum(scores)

@validate
def index_users(users: dict[str, User]) -> list[str]:
    return list(users.keys())
```

### 4. Custom validators
```python
from typely import validate, validator

@validator(int)
def positive(v):
    if v <= 0:
        raise ValueError("must be positive")
    return v

@validator(str)
def email(v):
    if "@" not in v:
        raise ValueError("invalid email")
    return v

@validate
def create(name: str, age: positive[int], contact: email[str]):
    ...
```

### 5. Coercion mode
```python
from typely import validate, Coerce

@validate(coerce=Coerce.SAFE)
def process(count: int, active: bool):
    ...

process("5", "true")  # count=5, active=True (safe coercion)
# SAFE: str→int, str→float, str→bool, int→float
# STRICT: no coercion (default)
```

### 6. Validation errors
```python
try:
    create_user(123, -5, None)
except ValidationError as e:
    print(e.errors)
    # [
    #   {"field": "name", "expected": "str", "got": "int", "value": 123},
    #   {"field": "age", "expected": "positive int", "got": "int", "value": -5},
    #   {"field": "email", "expected": "str", "got": "NoneType", "value": None}
    # ]
    print(e.pretty())
    # name: expected str, got int (123)
    # age: must be positive
    # email: expected str, got None
```

### 7. Schema validation (for dicts/dataclasses)
```python
from typely import Schema, Field

UserSchema = Schema({
    "name": Field(str, required=True),
    "age": Field(int, required=True, validators=[positive]),
    "email": Field(str, required=True, validators=[email]),
    "bio": Field(str, default=""),
    "tags": Field(list[str], default=[]),
})

UserSchema.validate(data)
```

### 8. Performance
- Cached type checks — same signature validated once, cached
- No imports parsed at runtime — uses `__annotations__` directly
- 10x faster than typeguard for repeated calls

### 9. Integration
- Works with dataclasses, attrs, pydantic models as input types
- Can validate return values
- Can be used standalone: `typely.check(5, int)` → True

## API Surface
- `@validate` — decorator for function validation
- `@validator(type)` — custom validator for a type
- `Schema({...})` — dict/data validation
- `Field(type, required, default, validators)` — schema field
- `ValidationError` — with `.errors` and `.pretty()`
- `Coerce.SAFE` / `Coerce.STRICT` — coercion mode
- `typely.check(value, type)` — standalone check
- `typely.is_valid(value, type)` — returns bool

## Dependencies
- Zero required (stdlib only)

## Testing
- 130+ tests
- All Python types: primitives, Optional, Union, Literal, Any, list/dict generics
- Custom validators
- Coercion edge cases
- Error messages
- Performance benchmarks vs typeguard
- Schema validation
- Dataclass integration

## Target
- Python 3.10+
- MIT license
