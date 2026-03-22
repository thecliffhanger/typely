"""Integration tests for typely."""

import time
import pytest
from typing import Optional, List, Dict, Any
from typely import validate, check, Coerce, Schema, Field, ValidationError, validator
from typely.validators import _global_validators


@pytest.fixture(autouse=True)
def clean_validators():
    """Clean global validators after each test to avoid leaking."""
    old = dict(_global_validators)
    _global_validators.clear()
    yield
    _global_validators.clear()
    _global_validators.update(old)


# --- API Handler ---

@validate
def create_user(name: str, age: int, email: Optional[str] = None) -> Dict[str, Any]:
    return {"name": name, "age": age, "email": email}


def test_api_handler_valid():
    result = create_user("Alice", 30, "alice@example.com")
    assert result["name"] == "Alice"
    assert result["age"] == 30  # passes positive_int validator


def test_api_handler_no_optional():
    result = create_user("Bob", 25)
    assert result["email"] is None


def test_api_handler_invalid():
    with pytest.raises(ValidationError):
        create_user(123, 30)  # name should be str


# --- Data processing pipeline ---

@validate
def process_record(record: Dict[str, Any]) -> List[str]:
    return list(record.keys())


def test_pipeline_valid():
    result = process_record({"a": 1, "b": 2})
    assert "a" in result


def test_pipeline_invalid_input():
    with pytest.raises(ValidationError):
        process_record([1, 2, 3])  # not a dict


# --- Schema user input ---

def validate_email(v):
    if "@" not in v:
        raise ValueError("invalid email")
    return v

user_schema = Schema({
    "username": Field(str, required=True),
    "email": Field(str, required=True, validators=[validate_email]),
    "age": Field(int, required=False, default=0),
    "tags": Field(List[str], required=False, default=[]),
})


def test_schema_valid():
    result = user_schema.validate({"username": "alice", "email": "a@b.com", "tags": ["admin"]})
    assert result["username"] == "alice"
    assert result["age"] == 0


def test_schema_invalid_email():
    with pytest.raises(ValidationError):
        user_schema.validate({"username": "alice", "email": "not-an-email"})


def test_schema_missing_required():
    with pytest.raises(ValidationError):
        user_schema.validate({"username": "alice"})


# --- Multiple validators on same type ---

def test_multiple_validators():
    global call_log
    call_log = []
    @validator(str)
    def log_and_return(v):
        call_log.append(("str_validator", v))
        return v

    @validate
    def take_str(x: str) -> str:
        return x
    take_str("hello")
    assert len(call_log) >= 1
    assert call_log[0] == ("str_validator", "hello")


# --- Performance: 10K calls ---

@validate
def simple_fn(x: int, y: str) -> int:
    return len(y) + x


def test_performance_10k():
    start = time.perf_counter()
    for i in range(10_000):
        simple_fn(i, "hello")
    elapsed = time.perf_counter() - start
    # Should be reasonably fast (< 5 seconds)
    assert elapsed < 5.0, f"Too slow: {elapsed:.2f}s for 10K calls"


# --- Coercion in schema ---

safe_schema = Schema({"count": Field(int, required=True)}, coerce=Coerce.SAFE)

def test_schema_coercion():
    result = safe_schema.validate({"count": "42"})
    assert result["count"] == 42
    assert isinstance(result["count"], int)


# --- Return type validation ---

@validate
def returns_int(x: int) -> str:
    return str(x)

def test_return_type_ok():
    assert returns_int(5) == "5"

@validate
def bad_return(x: int) -> str:
    return 42  # returns int, not str

def test_return_type_fail():
    with pytest.raises(ValidationError):
        bad_return(5)
