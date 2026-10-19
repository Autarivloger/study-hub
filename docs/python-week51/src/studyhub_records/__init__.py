"""Public, dependency-free record helpers; see the API guide for contracts."""

from .core import running_totals, totals_by_category, unique_in_order

__all__ = ["running_totals", "totals_by_category", "unique_in_order"]
