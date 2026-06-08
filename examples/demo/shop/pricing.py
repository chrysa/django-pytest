"""Tiny pricing helpers — one is tested, one is not (to create a coverage gap)."""

from __future__ import annotations


def apply_discount(price: float, percent: float) -> float:
    """Return *price* reduced by *percent* (0-100)."""
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return round(price * (1 - percent / 100), 2)


def bulk_price(unit_price: float, quantity: int) -> float:
    """Return the price for *quantity* units, with a 10% break above 100.

    This function is intentionally left untested so `testcheck` reports it as a
    coverage gap when the suite is run with --cov.
    """
    total = unit_price * quantity
    if quantity > 100:
        total *= 0.9
    return round(total, 2)
