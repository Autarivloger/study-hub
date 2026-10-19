"""Small algorithms with explicit validation, ordering and input ownership."""

from collections.abc import Iterable


def _integer(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("minutes must be an integer, not bool")
    if value < 0:
        raise ValueError("minutes must be nonnegative")
    return value


def unique_in_order(values: Iterable[str]) -> list[str]:
    """Return distinct strings in first-seen order, without altering values.

    Equality is case-sensitive. Empty strings are valid. All items must be strings.
    Input is consumed once. Expected O(n) time uses O(u) auxiliary set space,
    where u is the number of distinct strings; hashing is not worst-case O(1).

    >>> unique_in_order(["Python", "SQL", "Python", "python"])
    ['Python', 'SQL', 'python']
    >>> unique_in_order([])
    []
    """
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if not isinstance(value, str):
            raise TypeError("every label must be a string")
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def totals_by_category(rows: Iterable[tuple[str, int]]) -> dict[str, int]:
    """Sum nonnegative integer minutes by nonblank category, in first-seen order.

    Each row must be a length-two tuple. Whitespace inside a nonblank label is
    preserved, not silently normalized. bool is rejected despite subclassing int.
    Consume the iterable once; do not mutate it. Expected O(n) time, O(k) result
    space for k categories, assuming bounded-size labels and ordinary hashing.

    >>> totals_by_category([("Python", 20), ("SQL", 10), ("Python", 5)])
    {'Python': 25, 'SQL': 10}
    """
    totals: dict[str, int] = {}
    for row in rows:
        if not isinstance(row, tuple) or len(row) != 2:
            raise TypeError("each record must be a (category, minutes) tuple")
        category, raw_minutes = row
        if not isinstance(category, str):
            raise TypeError("category must be a string")
        if not category.strip():
            raise ValueError("category must not be blank")
        minutes = _integer(raw_minutes)
        totals[category] = totals.get(category, 0) + minutes
    return totals


def running_totals(values: Iterable[int]) -> list[int]:
    """Return prefix sums of nonnegative integer minutes, consuming input once.

    >>> running_totals([10, 0, 5])
    [10, 10, 15]
    >>> running_totals([])
    []

    O(n) additions, O(n) output space and O(1) auxiliary state, treating integer
    arithmetic as constant cost. Extremely large integers cost more per addition.
    """
    result: list[int] = []
    total = 0
    for raw_value in values:
        total += _integer(raw_value)
        result.append(total)
    return result
