"""
package_c - Reporting and output library.
Depends on package_a and package_b.

Sentinel version: 0.0.0.dev0
Actual version is injected at build time by the CI/CD version injection pipeline.
"""

__version__ = "0.0.0.dev0"
__author__ = "Divyanshu Sharma"

from package_a import greet
from package_b import process_data


def generate_report(name: str, data: list) -> str:
    """Generate a formatted text report for the given dataset."""
    stats = process_data(data)
    header = greet(name)
    lines = [
        header,
        "-" * len(header),
        f"Count   : {stats['count']}",
        f"Total   : {stats['total']}",
        f"Average : {stats['average']:.2f}",
    ]
    return "\n".join(lines)
