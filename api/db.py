"""
db.py — IBM i connection via JT400 JDBC (JayDeBeApi).

Supports two modes controlled by DATA_SOURCE env var:
  "live"  → connects to pub400.com via JT400 JDBC
  "mock"  → reads golden JSON from api/mock_data/

Usage:
    from db import get_connection   # for live
    from db import DATA_SOURCE      # to branch in routes
"""

import os
import pathlib
from dotenv import load_dotenv

load_dotenv()

DATA_SOURCE = os.getenv("DATA_SOURCE", "mock")

# ---------------------------------------------------------------------------
# Live connection (only imported/used when DATA_SOURCE == "live")
# ---------------------------------------------------------------------------

def get_connection():
    """
    Return a JayDeBeApi connection to IBM i on pub400.com.

    Requires:
      - api/lib/jt400.jar  (not in git — download from JTOpen releases)
      - IBMI_HOST, IBMI_USER, IBMI_PASSWORD, IBMI_LIBRARY in .env

    JDBC URL notes:
      - naming=sql  → use schema.table qualified names (ESH101.POLICYPF)
      - errors=full → full SQL error messages
      - date format → returned as java.sql.Date, JayDeBeApi gives string YYYY-MM-DD
    """
    import jpype
    import jaydebeapi  # deferred import — not available in mock mode

    host    = os.environ["IBMI_HOST"]
    user    = os.environ["IBMI_USER"]
    pw      = os.environ["IBMI_PASSWORD"]
    jar     = pathlib.Path(__file__).parent / os.getenv("JT400_JAR", "lib/jt400.jar")

    # Start the JVM with jt400.jar on the classpath before connect().
    if not jpype.isJVMStarted():
        jpype.startJVM(classpath=[str(jar)])

    url = (
        f"jdbc:as400://{host}"
        f";naming=sql"
        f";errors=full"
        f";date format=iso"      # DATE columns → YYYY-MM-DD strings
        f";time format=iso"
    )

    return jaydebeapi.connect(
        "com.ibm.as400.access.AS400JDBCDriver",
        url,
        [user, pw],
        str(jar),
    )
