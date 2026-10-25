
#!/usr/bin/env python3
"""
load_synthetic_data.py — Seed ESH101 tables with synthetic data via JT400 JDBC.

Use this on Mac (no ACS) or any machine where the Python venv + jt400.jar work.
Reads credentials from api/.env (same as FastAPI).

Usage:
    cd api
    source .venv/bin/activate
    python load_synthetic_data.py

Options:
    --dry-run   Print the SQL statements without executing them.
    --truncate  DELETE existing rows before inserting (idempotent re-run).
"""

import argparse
import os
import pathlib
import sys

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Synthetic data — mirrors challenge/data/synthetic_insert.sql exactly
# ---------------------------------------------------------------------------

CUSTOMERS = [
    (1000001, "Hartwell Insurance Test Co", "555-0101", "Chicago"),
    (1000002, "Brennan Fixtures LLC",       "555-0102", "Dallas"),
    (1000003, "Okafor Demo Agency",         "555-0103", "Atlanta"),
    (1000004, "Yılmaz Sample Group",        "555-0104", "Detroit"),
    (1000005, "Patel Synthetic Corp",       "555-0105", "Seattle"),
]

POLICIES = [
    (10000001, 1000001, "AUTO", "2024-01-01", "2025-01-01", 1200.00, "E"),
    (10000002, 1000001, "HOME", "2024-03-15", "2025-03-15", 2400.50, "A"),
    (10000003, 1000002, "LIFE", "2023-06-01", "2033-06-01",  800.00, "A"),
    (10000004, 1000002, "AUTO", "2022-01-01", "2023-01-01",  950.75, "E"),
    (10000005, 1000003, "HEAL", "2025-01-01", "2026-01-01", 3100.00, "A"),
    (10000006, 1000003, "HOME", "2020-05-10", "2021-05-10", 1800.00, "C"),
    (10000007, 1000004, "AUTO", "2025-04-01", "2026-04-01", 1050.00, "A"),
    (10000008, 1000005, "LIFE", "2024-07-01", "2034-07-01",  600.00, "A"),
]

CLAIMS = [
    (20000001, 10000001, "2024-08-15", "COLL",  3500.00, "P", "Rear-end collision on I-90"),
    (20000002, 10000001, "2024-11-01", "LIAB",  1200.00, "A", "Third-party liability claim"),
    (20000003, 10000002, "2024-09-20", "FIRE",  8500.00, "O", "Kitchen fire damage"),
    (20000004, 10000003, "2024-06-05", "DISA",  5000.00, "A", "Short-term disability payout"),
    (20000005, 10000004, "2022-09-10", "COLL",  4200.00, "P", "Parking lot collision"),
    (20000006, 10000005, "2025-03-01", "HOSP", 12000.00, "O", "Emergency hospitalisation"),
    (20000007, 10000005, "2025-05-14", "DRUG",   450.00, "A", "Prescription reimbursement"),
    (20000008, 10000007, "2025-07-22", "COLL",  2100.00, "O", "Side-swipe on highway"),
    (20000009, 10000007, "2025-08-30", "WIND",   780.00, "R", "Hailstorm claim outside coverage"),
    (20000010, 10000008, "2024-10-01", "DISA",  2500.00, "P", "Disability benefit paid"),
]

# ---------------------------------------------------------------------------
# SQL statements
# ---------------------------------------------------------------------------

LIB = "ESH101"

INSERT_CUST = (
    f"INSERT INTO {LIB}.CUSTPF (CUSTID, CUSTNAME, PHONE, CITY) VALUES (?, ?, ?, ?)"
)
INSERT_POL = (
    f"INSERT INTO {LIB}.POLICYPF "
    f"(POLID, CUSTID, POLTYPE, STARTDT, ENDDT, PREMIUM, STATUS) "
    f"VALUES (?, ?, ?, ?, ?, ?, ?)"
)
INSERT_CLAIM = (
    f"INSERT INTO {LIB}.CLAIMPF "
    f"(CLAIMNO, POLID, CLAIMDT, CLAIMTYPE, AMOUNT, CLAIMSTS, DESCR) "
    f"VALUES (?, ?, ?, ?, ?, ?, ?)"
)

DELETE_CLAIMS = f"DELETE FROM {LIB}.CLAIMPF"
DELETE_POLS   = f"DELETE FROM {LIB}.POLICYPF"
DELETE_CUSTS  = f"DELETE FROM {LIB}.CUSTPF"

# ---------------------------------------------------------------------------
# Connection helper (reuses db.py logic without importing it)
# ---------------------------------------------------------------------------

def open_connection():
    import jpype
    import jaydebeapi

    host = os.environ["IBMI_HOST"]
    user = os.environ["IBMI_USER"]
    pw   = os.environ["IBMI_PASSWORD"]
    jar  = pathlib.Path(__file__).parent / os.getenv("JT400_JAR", "lib/jt400.jar")

    if not jar.exists():
        sys.exit(f"ERROR: jt400.jar not found at {jar}\n"
                 "Download jt400-21.0.7-java11.jar and place it in api/lib/")

    if not jpype.isJVMStarted():
        jpype.startJVM(classpath=[str(jar)])

    url = (
        f"jdbc:as400://{host}"
        ";naming=sql"
        ";errors=full"
        ";date format=iso"
        ";time format=iso"
    )

    print(f"Connecting to {host} as {user} …")
    return jaydebeapi.connect(
        "com.ibm.as400.access.AS400JDBCDriver",
        url,
        [user, pw],
        str(jar),
    )

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Seed IBM i synthetic data")
    parser.add_argument("--dry-run",  action="store_true",
                        help="Print statements without executing")
    parser.add_argument("--truncate", action="store_true",
                        help="DELETE existing rows before inserting")
    args = parser.parse_args()

    if args.dry_run:
        print("=== DRY RUN — no statements executed ===\n")
        if args.truncate:
            for s in [DELETE_CLAIMS, DELETE_POLS, DELETE_CUSTS]:
                print(s + ";")
            print()
        for row in CUSTOMERS:
            print(INSERT_CUST.replace("?", "{}").format(*row) + ";")
        print()
        for row in POLICIES:
            print(INSERT_POL.replace("?", "{}").format(*row) + ";")
        print()
        for row in CLAIMS:
            print(INSERT_CLAIM.replace("?", "{}").format(*row) + ";")
        return

    conn = open_connection()
    cur  = conn.cursor()

    try:
        if args.truncate:
            print("Truncating existing rows …")
            # Delete in FK order: claims → policies → customers
            for stmt in [DELETE_CLAIMS, DELETE_POLS, DELETE_CUSTS]:
                print(f"  {stmt}")
                cur.execute(stmt)
            conn.commit()

        print(f"Inserting {len(CUSTOMERS)} customers …")
        cur.executemany(INSERT_CUST, CUSTOMERS)
        conn.commit()

        print(f"Inserting {len(POLICIES)} policies …")
        cur.executemany(INSERT_POL, POLICIES)
        conn.commit()

        print(f"Inserting {len(CLAIMS)} claims …")
        cur.executemany(INSERT_CLAIM, CLAIMS)
        conn.commit()

        print("\n✅  Done. Rows inserted:")
        for table, count in [
            (f"{LIB}.CUSTPF",   len(CUSTOMERS)),
            (f"{LIB}.POLICYPF", len(POLICIES)),
            (f"{LIB}.CLAIMPF",  len(CLAIMS)),
        ]:
            print(f"  {table}: {count} rows")

    except Exception as exc:
        conn.rollback()
        print(f"\n❌  Error: {exc}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
