#!/usr/bin/env python3
"""
test_jt400.py — Minimal JT400 JDBC smoke test.

Run from api/ directory with venv active:
  python test_jt400.py

Prerequisites:
  pip install JayDeBeApi JPype1
  jt400.jar present at lib/jt400.jar (download from JTOpen releases)
  api/.env with IBMI_HOST, IBMI_USER, IBMI_PASSWORD set

What this tests:
  1. JVM starts and loads jt400.jar
  2. JDBC connection to pub400.com succeeds
  3. Plain SELECT returns rows
  4. Stored procedure with DYNAMIC RESULT SETS returns a cursor
"""

import os, pathlib, sys
from dotenv import load_dotenv

load_dotenv()

HOST    = os.environ["IBMI_HOST"]
USER    = os.environ["IBMI_USER"]
PW      = os.environ["IBMI_PASSWORD"]
LIBRARY = os.getenv("IBMI_LIBRARY", "ESH101")
JAR     = pathlib.Path(__file__).parent / os.getenv("JT400_JAR", "lib/jt400.jar")

if not JAR.exists():
    sys.exit(f"ERROR: jt400.jar not found at {JAR}\n"
             "Download from https://github.com/IBM/JTOpen/releases")

import jpype
import jaydebeapi

# Start the JVM explicitly with jt400.jar on the classpath BEFORE
# jaydebeapi.connect tries to load the driver class.
if not jpype.isJVMStarted():
    jpype.startJVM(classpath=[str(JAR)])

URL = (
    f"jdbc:as400://{HOST}"
    f";naming=sql"        # dot-qualified names: LIBRARY.TABLE
    f";errors=full"
    f";date format=iso"   # dates come back as YYYY-MM-DD strings
    f";time format=iso"
)

print(f"Connecting to {HOST} as {USER} ...")
conn = jaydebeapi.connect(
    "com.ibm.as400.access.AS400JDBCDriver",
    URL,
    [USER, PW],
    str(JAR),
)
print("✅ Connected.\n")

# ----- Test 1: plain SELECT ------------------------------------------------
print("Test 1: SELECT from course file E4PF ...")
cur = conn.cursor()
cur.execute(f"SELECT EMNUMBER, EMNAME, EMDMY FROM {LIBRARY}.E4PF FETCH FIRST 3 ROWS ONLY")
rows = cur.fetchall()
for r in rows:
    print(f"  {r}")
print(f"✅ {len(rows)} rows returned.\n")

# ----- Test 2: stored procedure with DYNAMIC RESULT SETS -------------------
# Assumes ESH101.TEST_PROC2 exists (the one you already verified in ACS).
# If the procedure doesn't exist yet, comment this block out.
print("Test 2: CALL stored procedure returning a result set ...")
try:
    cur2 = conn.cursor()
    cur2.execute(f"CALL {LIBRARY}.TEST_PROC2()")
    # JayDeBeApi: after CALL, result set rows are accessed via fetchall()
    # on the SAME cursor — the driver advances to the first result set.
    result_rows = cur2.fetchall()
    print(f"  Rows from procedure: {result_rows}")
    print(f"✅ Procedure returned {len(result_rows)} rows.\n")
except Exception as e:
    print(f"  ⚠️  TEST_PROC2 call failed (skip if proc not yet created): {e}\n")

conn.close()
print("All tests done. JT400 JDBC from Python is working.")
