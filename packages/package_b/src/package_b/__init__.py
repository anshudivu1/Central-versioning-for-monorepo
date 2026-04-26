"""
package_b - Data processing library.
Depends on package_a.

Sentinel version: 0.0.0.dev0
Actual version is injected at build time by the CI/CD version injection pipeline.
"""

__version__ = "0.0.0.dev0"
__author__ = "Divyanshu Sharma"

from package_a import add


def multiply(a: int, b: int) -> int:
    """Multiply two integers using repeated addition."""
    result = 0
    for _ in range(b):
        result = add(result, a)
    return result


def process_data(data: list) -> dict:
    """Return basic stats for a list of numbers."""
    if not data:
        return {"count": 0, "total": 0, "average": 0}
    total = sum(data)
    return {
        "count": len(data),
        "total": total,
        "average": total / len(data),
    }
