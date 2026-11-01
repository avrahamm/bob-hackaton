# IBM i Modernisation — Insurance Policy Lookup

> **IBM Bob Hackathon 2026**  
> Demonstrating how a legacy IBM i green-screen workflow can be understood, documented, and exposed through a modern REST API and web UI — without rewriting the IBM i core.

---

## The Problem

Insurance agents at companies running IBM i systems navigate multiple 5250 green-screen panels to look up a policy and its claims. The data lives in Db2 physical files, accessed by RPG programs through native file I/O. This works, but it is invisible to modern tooling, hard to integrate, and slow to hand to new staff.

## The Solution

A thin modernisation layer, built with **IBM Bob** at every step:

```
Browser  →  Web UI (HTML/CSS/JS)
             ↓
         FastAPI (Python)  ←  mock fallback for offline demo
             ↓  JT400 JDBC
         IBM i Db2 (PUB400.com)
             ↓  SQL stored procedures
         DDS physical files  (CUSTPF · POLICYPF · CLAIMPF · CLAIMLF1)
             ↓
         Synthetic insurance data
```

**No legacy code was rewritten.** The DDS physical files and their structure are unchanged. The stored procedures sit alongside the existing data layer and read the same tables.

---

## Live Demo

Start the API (requires `api/.env` with IBM i credentials and `api/lib/jt400.jar`):

```bash
cd api
cp env.example .env        # fill in IBMI_HOST, IBMI_USER, IBMI_PASSWORD
# download jt400-21.0.7-java11.jar → api/lib/jt400.jar
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open the web UI: **http://localhost:8000/ui/**

Enter any policy ID from the synthetic data:

| Policy ID | Customer | Type | Status |
|---|---|---|---|
| 10000001 | Hartwell Insurance Test Co | Auto | Expired |
| 10000002 | Hartwell Insurance Test Co | Home | Active |
| 10000003 | Brennan Fixtures LLC | Life | Active |
| 10000005 | Okafor Demo Agency | Health | Active |
| 10000007 | Yilmaz Sample Group | Auto | Active |

### Mock mode (no IBM i required)

```bash
# In api/.env:
DATA_SOURCE=mock
uvicorn main:app --reload --port 8000
```

Works on any machine without credentials or `jt400.jar`.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/policies` | List all policies (optional `?cust_id=` filter) |
| `GET` | `/policies/{pol_id}` | Get one policy by ID |
| `GET` | `/policies/{pol_id}/claims` | List claims for a policy |
| `GET` | `/source` | Returns `{"source":"live"}` or `{"source":"mock"}` |
| `GET` | `/ui/` | Web UI |

All responses: JSON, ISO dates (`YYYY-MM-DD`), decimals as numbers.

---

## Repository Layout

```
bob-hackaton/
├── api/                        ← FastAPI project
│   ├── main.py                 ← 3 endpoints + /source + static /ui mount
│   ├── db.py                   ← JT400 JDBC connection (JPype1 + JayDeBeApi)
│   ├── load_synthetic_data.py  ← seeds IBM i tables via JDBC (--truncate flag)
│   ├── requirements.txt
│   ├── env.example             ← copy to .env, fill credentials
│   ├── mock_data/
│   │   ├── policies.json       ← golden fixture for mock mode
│   │   └── claims.json
│   └── lib/                    ← place jt400.jar here (NOT in git)
├── ibmi/
│   ├── dds/
│   │   ├── CUSTPF.pf           ← Customer physical file
│   │   ├── POLICYPF.pf         ← Policy physical file (REFFLD from CUSTPF)
│   │   ├── CLAIMPF.pf          ← Claim physical file (REFFLD from POLICYPF)
│   │   └── CLAIMLF1.lf         ← Logical file over CLAIMPF (key: POLID+CLAIMNO)
│   └── sql/
│       ├── LIST_POLICIES.sql   ← stored procedure: all policies, optional CUSTID filter
│       ├── GET_POLICY.sql      ← stored procedure: single policy by POLID
│       └── LIST_CLAIMS.sql     ← stored procedure: claims for a policy
├── challenge/
│   ├── brief.md                ← project decisions and session log
│   └── data/
│       └── synthetic_insert.sql ← seed script (run in ACS Run SQL Scripts)
├── ui/
│   └── index.html              ← single-page web UI (no build step)
└── bob-sessions/               ← IBM Bob task session summary screenshots
```

---

## IBM i Setup (PUB400.com)

All IBM i objects live in library **ESH101**.

### Compile order

```cl
/* Physical files */
CRTPF FILE(ESH101/CUSTPF)   SRCFILE(ESH101/QDDSSRC) SRCMBR(CUSTPF)
CRTPF FILE(ESH101/POLICYPF) SRCFILE(ESH101/QDDSSRC) SRCMBR(POLICYPF)
CRTPF FILE(ESH101/CLAIMPF)  SRCFILE(ESH101/QDDSSRC) SRCMBR(CLAIMPF)

/* Logical file */
CRTLF  FILE(ESH101/CLAIMLF1) SRCFILE(ESH101/QDDSSRC) SRCMBR(CLAIMLF1)
```

### Create stored procedures

Run each `.sql` file in **ACS Run SQL Scripts** connected to PUB400:
- `ibmi/sql/LIST_POLICIES.sql`
- `ibmi/sql/GET_POLICY.sql`
- `ibmi/sql/LIST_CLAIMS.sql`

### Seed synthetic data

```bash
# Option A: ACS Run SQL Scripts
# Open challenge/data/synthetic_insert.sql → Run All (F5)

# Option B: Python (any machine with venv + jt400.jar)
cd api && source .venv/bin/activate
python load_synthetic_data.py --truncate
```

---

## How IBM Bob Was Used

Bob was used at every stage of this project — not just for code generation:

| Stage | Bob's role |
|---|---|
| Architecture decision | Evaluated JT400 JDBC vs SSH bridge vs ILEastic; recommended and justified the JDBC path |
| DDS source files | Wrote CUSTPF, POLICYPF, CLAIMPF, CLAIMLF1 with correct REFFLD syntax; debugged compiler errors |
| SQL stored procedures | Wrote LIST_POLICIES, GET_POLICY, LIST_CLAIMS with DYNAMIC RESULT SETS |
| FastAPI scaffold | Generated db.py, main.py, Pydantic models, live/mock switch |
| Python data seeder | Wrote load_synthetic_data.py; diagnosed and fixed SQL0418 DATE(?) parameter marker error |
| Web UI | Generated ui/index.html — search, policy card, claims table, LIVE/MOCK badge |
| IBM i debugging | Diagnosed DDS column-alignment errors (CPD7401, CPD7593), PFILE library qualification, SFLPAG sizing |
| Session log | challenge/brief.md maintained throughout as project memory |

The **Bob task session summaries** are in `bob-sessions/` — they show the full conversation history for each work session.

---

## Technology Stack

| Layer | Technology |
|---|---|
| IBM i data | Db2 for i, DDS physical/logical files, SQL stored procedures |
| JDBC bridge | JT400 (JTOpen 21.0.7), JayDeBeApi, JPype1 |
| API | FastAPI 0.115, Python 3.13, Pydantic v2 |
| Web UI | Single-page HTML/CSS/vanilla JS, no build step |
| Dev tooling | IBM Bob (AI coding assistant), IBM i extension for VS Code |
| IBM i system | PUB400.com (public shared IBM i) |

---

## Security

- Credentials are in `api/.env` — git-ignored, never committed
- `jt400.jar` is in `api/lib/` — git-ignored
- All data is **100% synthetic** — no real customer, policy or claim data anywhere
- See [SECURITY.MD](SECURITY.MD) for full guidelines
