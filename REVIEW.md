# typely Code Review

## Summary
Runtime type validation library for Python. Decorator-based (`@validate`) and standalone (`check`, `Schema`). Supports coercion, custom validators, nested generics, Optional/Union/Literal. Well-structured, ~600 LOC across 7 modules.

## Bug Fixed
- **Async function support**: `@validate` on async functions returned the coroutine object instead of awaiting it. The wrapper now detects `iscoroutinefunction` and creates an async wrapper that properly awaits before validating the return value.

## Code Quality Assessment

### Strengths
- **Correct bool/int handling**: Properly rejects `True`/`False` for `int` fields (bool is subclass of int in Python)
- **Good error messages**: Include field name, expected type, got type, and actual value
- **Clean separation**: types.py (type checking), validate.py (decorator), schema.py (dict validation), validators.py (registry)
- **Annotated support**: Extracts validators from `typing.Annotated` hints
- **10K calls in ~1s**: Performance is solid with current approach

### Weaknesses / Improvement Opportunities
1. **No caching**: `_check_type` re-derives origin/args on every call. For hot paths with complex types, caching `get_origin`/`get_args` results would help.
2. **Global mutable validator registry**: `_global_validators` is a plain dict shared across all tests. Consider a context/scoping mechanism or make it per-decorator.
3. **No ForwardRef resolution**: Unresolved forward references (e.g., recursive classes) are not handled.
4. **Schema doesn't reject unknown keys**: Extra fields in input data are silently ignored. Could add `allow_extra=False` option.
5. **`float` coercion in STRICT mode**: `int → float` always succeeds (design choice, but surprising in STRICT mode).
6. **Return validation for async: global validators don't run** if Annotated validators raise — minor control flow issue in `_validate_return` (checks `not ret_errors` after Annotated loop but validators already set errors).
7. **No `frozen` Schema**: Once created, schema fields are mutable (can add/remove fields after creation).

### Test Coverage
- **197 tests pass** (157 original + 40 new adversarial/integration)
- Covers: primitives, collections, nested generics, Optional, Union, Literal, Annotated, coercion (STRICT/SAFE), custom validators, Schema, async functions, classmethod/staticmethod, error messages, edge cases

### No Critical Issues Found
The library is correct for its stated scope. The async bug was the only functional defect discovered.
