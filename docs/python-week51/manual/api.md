# API contract

## unique_in_order(values)

Accept an iterable of strings, including a one-shot generator. Return a new list
in first-occurrence order. Empty strings and case differences are retained.
Reject non-strings with `TypeError`. Do not mutate the input. Expected O(n) time
and O(u) extra set memory, where u is distinct labels, assuming ordinary hashing
and bounded label length. Returning a list necessarily retains the result.

## totals_by_category(rows)

Accept an iterable of length-two **tuples** `(category, minutes)`. Category must
be a nonblank string; surrounding whitespace is preserved. Minutes must be a
nonnegative integer; bool and floats raise `TypeError`, negative values raise
`ValueError`. Return a dict in first-category order. Empty input returns `{}`.
Expected O(n) dictionary work, O(k) result memory for k distinct categories.

## running_totals(values)

Return prefix sums of nonnegative integer minutes. Empty input returns `[]`.
Apply the same integer/bool validation as above. O(n) additions and O(n) output
space, with O(1) auxiliary state. Big integers have nonconstant arithmetic cost.

## Failure and compatibility

Functions raise before returning a partial result. They do consume any input
items reached before an exception; a generator cannot be rewound automatically.
Exceptions are a documented part of the public interface. Changing ordering,
accepted types or failure behavior requires an explicit compatibility decision.

The CLI accepts UTF-8 CSV, optionally with a BOM. It requires exactly two named
columns in order. CSV minutes contain ASCII digits only; missing fields, extra
fields, signs and decimals are rejected. It writes JSON by replacing one file
after complete validation. This is not a durable multi-file transaction.
