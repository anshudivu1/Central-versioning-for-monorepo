"""
package_a - Core utilities library.

Sentinel version: 0.0.0.dev0
Actual version is injected at build time by the CI/CD version injection pipeline.
"""

__version__ = "0.0.0.dev0"
__author__ = "Divyanshu Sharma"


def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello from package_a, {name}!"


def add(a: int, b: int) -> int:
    """Add two integers and return the result."""
    return a + b
