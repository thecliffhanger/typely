"""Validation errors."""


class ValidationError(TypeError):
    """Raised when type validation fails."""

    def __init__(self, errors):
        self.errors = errors
        parts = [e.get("message", str(e)) for e in errors]
        super().__init__("\n".join(parts))

    def pretty(self):
        lines = []
        for e in self.errors:
            field = e.get("field", "?")
            msg = e.get("message", "")
            lines.append(f"{field}: {msg}")
        return "\n".join(lines)


class SchemaError(ValidationError):
    """Raised when schema validation fails."""
    pass
