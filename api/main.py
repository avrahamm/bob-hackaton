"""
main.py — FastAPI entry point for insurance policy lookup API.

Endpoints:
  GET /policies?cust_id=...     list policies (optionally filter by customer)
  GET /policies/{pol_id}        get one policy by ID
  GET /policies/{pol_id}/claims list claims for a policy

Run (from api/ directory, with venv active):
  uvicorn main:app --reload --port 8000

Switch between live IBM i and mock data via DATA_SOURCE in .env:
  DATA_SOURCE=mock   (default — safe to run anywhere)
  DATA_SOURCE=live   (requires jt400.jar and valid .env credentials)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import json, pathlib

from db import DATA_SOURCE, get_connection

app = FastAPI(title="Insurance Policy Lookup API", version="0.1.0")

MOCK_DIR = pathlib.Path(__file__).parent / "mock_data"

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class Policy(BaseModel):
    pol_id:   int
    cust_id:  int
    pol_type: str
    start_dt: str          # ISO date YYYY-MM-DD
    end_dt:   str
    premium:  float
    status:   str          # A / E / C
    status_label: str      # Active / Expired / Cancelled

class Claim(BaseModel):
    claim_no:   int
    pol_id:     int
    claim_dt:   str
    claim_type: str
    amount:     float
    claim_sts:  str        # O / A / R / P
    claim_sts_label: str   # Open / Approved / Rejected / Paid
    descr:      str

STATUS_LABELS   = {"A": "Active", "E": "Expired",  "C": "Cancelled"}
CLAIM_STS_LABELS = {"O": "Open",  "A": "Approved", "R": "Rejected", "P": "Paid"}

# ---------------------------------------------------------------------------
# Helper — load mock data
# ---------------------------------------------------------------------------

def _load_mock(filename: str):
    with open(MOCK_DIR / filename) as f:
        return json.load(f)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/policies", response_model=list[Policy])
def list_policies(cust_id: Optional[int] = None):
    if DATA_SOURCE == "mock":
        data = _load_mock("policies.json")
        if cust_id:
            data = [p for p in data if p["cust_id"] == cust_id]
        return data

    # Live path
    conn = get_connection()
    try:
        cur = conn.cursor()
        if cust_id:
            cur.execute(
                "SELECT POLID,CUSTID,POLTYPE,STARTDT,ENDDT,PREMIUM,STATUS "
                "FROM ESH101.POLICYPF WHERE CUSTID=? ORDER BY POLID",
                [cust_id]
            )
        else:
            cur.execute(
                "SELECT POLID,CUSTID,POLTYPE,STARTDT,ENDDT,PREMIUM,STATUS "
                "FROM ESH101.POLICYPF ORDER BY POLID"
            )
        rows = cur.fetchall()
    finally:
        conn.close()

    return [_row_to_policy(r) for r in rows]


@app.get("/policies/{pol_id}", response_model=Policy)
def get_policy(pol_id: int):
    if DATA_SOURCE == "mock":
        data = _load_mock("policies.json")
        matches = [p for p in data if p["pol_id"] == pol_id]
        if not matches:
            raise HTTPException(status_code=404, detail="Policy not found")
        return matches[0]

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT POLID,CUSTID,POLTYPE,STARTDT,ENDDT,PREMIUM,STATUS "
            "FROM ESH101.POLICYPF WHERE POLID=?",
            [pol_id]
        )
        row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    return _row_to_policy(row)


@app.get("/policies/{pol_id}/claims", response_model=list[Claim])
def list_claims(pol_id: int):
    if DATA_SOURCE == "mock":
        data = _load_mock("claims.json")
        return [c for c in data if c["pol_id"] == pol_id]

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT CLAIMNO,POLID,CLAIMDT,CLAIMTYPE,AMOUNT,CLAIMSTS,DESCR "
            "FROM ESH101.CLAIMPF WHERE POLID=? ORDER BY CLAIMNO",
            [pol_id]
        )
        rows = cur.fetchall()
    finally:
        conn.close()

    return [_row_to_claim(r) for r in rows]


# ---------------------------------------------------------------------------
# Row mappers
# ---------------------------------------------------------------------------

def _row_to_policy(r) -> dict:
    status = str(r[6]).strip()
    return {
        "pol_id":      int(r[0]),
        "cust_id":     int(r[1]),
        "pol_type":    str(r[2]).strip(),
        "start_dt":    str(r[3]),   # JayDeBeApi returns date as string with date format=iso
        "end_dt":      str(r[4]),
        "premium":     float(r[5]),
        "status":      status,
        "status_label": STATUS_LABELS.get(status, status),
    }

def _row_to_claim(r) -> dict:
    sts = str(r[5]).strip()
    return {
        "claim_no":      int(r[0]),
        "pol_id":        int(r[1]),
        "claim_dt":      str(r[2]),
        "claim_type":    str(r[3]).strip(),
        "amount":        float(r[4]),
        "claim_sts":     sts,
        "claim_sts_label": CLAIM_STS_LABELS.get(sts, sts),
        "descr":         str(r[6]).strip(),
    }
