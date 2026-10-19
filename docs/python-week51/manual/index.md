# Study Hub Records

Three small functions for synthetic study records. Python 3.12 or later,
no runtime dependencies. This project is separate from the website's saved data.

## First successful result

After installing the package, run this in Python:

```python
from studyhub_records import unique_in_order, totals_by_category, running_totals

print(unique_in_order(["Python", "SQL", "Python"]))
print(totals_by_category([("Python", 20), ("Python", 10)]))
print(running_totals([20, 0, 10]))
```

Expected output:

```text
['Python', 'SQL']
{'Python': 30}
[20, 20, 30]
```

The distribution name is `studyhub51-records`; the import is `studyhub_records`.
Read [the API contract](api.md) before supplying your own data.

## CSV command

Create `sample.csv` with `category,minutes` as the header and rows such as `Python,20`.

```text
studyhub-records sample.csv --output report.json
```

The command reports row count and totals. Exit status 0 means success; 2 means
input/output failed. A failed validation preserves an existing output file.
The command materializes input rows; it is not a bounded-memory CSV processor.
