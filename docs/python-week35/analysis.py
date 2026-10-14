"""Read-only SQL/pandas comparison for the Week35 fictional library."""
import argparse
from contextlib import closing
import json
import pandas as pd
from library_db import connect, require_version, REPORT_SQL


def compare(con):
    require_version(con)
    sql = pd.read_sql_query(REPORT_SQL, con)
    members = pd.read_sql_query("SELECT id,name FROM members ORDER BY id", con)
    loans = pd.read_sql_query("SELECT id,member_id,returned_on FROM loans ORDER BY id", con)
    counts = loans.groupby("member_id").size()
    opens = loans.loc[loans["returned_on"].isna()].groupby("member_id").size()
    python = members.assign(
        loan_count=members["id"].map(counts).fillna(0).astype("int64"),
        open_count=members["id"].map(opens).fillna(0).astype("int64"))
    # Align result dtypes deliberately before checking all values and ordering.
    sql = sql.astype({"id": "int64", "loan_count": "int64", "open_count": "int64"})
    python = python.astype({"id": "int64"})
    pd.testing.assert_frame_equal(sql, python)
    return {"same_result": True, "members": sql.to_dict("records"),
            "event_total": int(sql["loan_count"].sum()),
            "open_total": int(sql["open_count"].sum())}


def main():
    parser = argparse.ArgumentParser(description="Read-only Week35 SQL/pandas parity")
    parser.add_argument("database")
    args = parser.parse_args()
    with closing(connect(args.database, readonly=True)) as con:
        print(json.dumps(compare(con), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
