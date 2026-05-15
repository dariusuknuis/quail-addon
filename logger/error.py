# pyright: basic, reportGeneralTypeIssues=false

from typing import List

# Global list to store error messages
error_messages: List[str] = []  # Type-annotated empty list

def error(msg: str) -> None:
    """
    Add an error message to the global error list.

    Args:
        msg: The error message to add
    """
    print(msg)
    error_messages.append(msg)

def error_clear() -> None:
    """Clear all error messages from the list."""
    error_messages.clear()

def errors() -> List[str]:
    """
    Return the list of error messages.

    Returns:
        List of all recorded error messages
    """
    return error_messages.copy()  # Return a copy to prevent accidental modification