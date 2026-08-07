class ParseError(Exception):
    """Custom exception for map file parsing errors."""

    def __init__(self, line_number: int, reason: str) -> None:
        """Initialize a ParseError.

        Args:
            line_number: The line number where the error occurred.
            reason: A human-readable description of the error.
        """
        self.line_number = line_number
        self.reason = reason

    def __str__(self) -> str:
        """Return a formatted error message with line number and reason."""
        return f"Parse error at line {self.line_number}: {self.reason}"
