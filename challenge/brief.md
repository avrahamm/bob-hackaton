# Challenge brief — Insurance policy lookup: IBM i RPG to modern API

_Last updated: 2026-10-22. Read this at the start of every Bob session._

---

## Team

- Solo developer, backend (13+ years PHP/Laravel), recently completed RPG/IBM i
  and COBOL courses.
- Experience with coding agents: **some** (first hackathon project with Bob).

---

## The idea

Demonstrate how one small, real workflow in a legacy IBM i system can be
understood, documented, tested, and then exposed through a modern API and
web UI — **without rewriting the legacy core**.

An insurance agent today moves between several green screens to find a policy
and its claims. The modernisation target:

1. RPG business-logic procedures (`getPolicy`, `listPolicies`, `getClaims`)
   separated from screen and transport code.
2. A thin FastAPI layer exposing JSON over JT400 JDBC, calling Db2 stored
   procedures on IBM i.
3. A minimal single-page web UI: search → policy card → claims table.
4. Bob used visibly at every step: code explanation, business-rule extraction,
   API contract design, code review. Bob session log kept in repo.

Scope is **read-only**. No CREATE/UPDATE/DELETE anywhere in the MVP.

---

## Decisions made

| Decision | Choice | Rationale |
|---|---|---|
| API approach | **Option A — live JT400 JDBC** from FastAPI on Ubuntu | All required ports open and verified; ACS already uses JT400 |
| Fallback | **Option C — mock/golden JSON files** | Coded in parallel; zero-risk fallback |
| SSH bridge | **Parked** | SSH to PUB400 failed on ports 22, 23, 2222 |
| ILEastic/noxDB | **Parked** | Unverified; shared system install risk |
| RPG I/O style | **Native I/O** (CHAIN/READE) in legacy program; **embedded SQL** in service wrapper | Shows before/after contrast |
| API framework | **FastAPI (Python)** | Simpler than Laravel; ibm_db/JayDeBeApi in same ecosystem |
| Deployment | **Local (Ubuntu) first**, cloud later | Reduce scope risk |
| Data | **100% synthetic** | PUB400 is a shared public system; no real data |

---

## What is still open

- [x] JT400 JDBC from own Python code (JayDeBeApi + JPype1 in venv) — **confirmed 2026-10-22**
- [ ] Calling insurance stored procedures (LIST_POLICIES, GET_POLICY, LIST_CLAIMS) from Python
- [ ] How JayDeBeApi returns DYNAMIC RESULT SETS from CALL
- [ ] Whether PUB400 allows `CREATE PROCEDURE` returning result sets in ESH101
  (✅ TEST_PROC2 already confirmed this works)
- [ ] Cloud deployment (deferred)

---

## Environment

| Component | Detail |
|---|---|
| IBM i | PUB400.com, library ESH101, account confirmed |
| Primary dev machine | Ubuntu PC — IBM ACS + 5250 emulator working, Bob IDE + IBM i extension working |
| Secondary machine | Mac 2021 (64 GB) — Bob IDE + IBM i extension connected; ACS **not working** on Mac; no 5250 emulator on Mac |
| FastAPI | Runs on Ubuntu (or Mac — no IBM i dependency for mock path) |
| Python target | 3.11+ in a venv under `api/` |
| JT400 jar | `api/lib/jt400.jar` — downloaded manually, **not in git** |
| Credentials | In `api/.env` — **not in git** |

---

## PUB400 capability — verified (2026-10-21)

| Test | Result |
|---|---|
| TCP to pub400.com:446,449,8470,8471,8476,9471 | ✅ All connect |
| ACS Run SQL Scripts from Ubuntu | ✅ Works |
| STRSQL inside PUB400 | ✅ Works |
| SYSCOLUMNS / SELECT on ESH101.E4PF | ✅ Works (24 rows) |
| Stored procedure DYNAMIC RESULT SETS (TEST_PROC2) | ✅ Works |
| JSON_OBJECT, JSON_ARRAYAGG, TRIM | ✅ Works |
| CRTPF / CRTDSPF from DDS | ✅ Works |
| CRTBNDRPG, CALL | ✅ Works |
| PASE: python 2.7/3.6/3.9/3.13, node, git, jq, curl | ✅ Present |
| SSH from Ubuntu (ports 22, 23, 2222) | ❌ Failed — parked |
| JT400 JDBC from Python (JayDeBeApi) | ✅ Works — Mac + Ubuntu confirmed (jt400-21.0.7-java11.jar) |
| ibm_db / itoolkit on PUB400 PASE | ⬜ Not yet tested |
| IWS / user CGI on PUB400 | ⬜ Unknown |

---

## Source layout

```
bob-hackaton/
├── challenge/          ← this folder (brief, blueprint, demo notes)
│   ├── brief.md        ← YOU ARE HERE
│   ├── data/           ← synthetic SQL INSERT scripts
│   └── blueprint.html  ← generated later
├── ibmi/               ← DDS, RPGLE, SQL procedure sources
│   ├── dds/
│   ├── rpgle/
│   └── sql/
├── api/                ← FastAPI project
│   ├── main.py
│   ├── db.py
│   ├── requirements.txt
│   ├── .env.example
│   └── lib/            ← jt400.jar goes here (NOT in git)
└── ui/                 ← minimal web UI (later)
```

---

## Physical files (DDS) — defined

| File | Key | Fields |
|---|---|---|
| CUSTPF | CUSTID | CUSTID(7S0), CUSTNAME(40A), PHONE(15A), CITY(25A) |
| POLICYPF | POLID | POLID(8S0), CUSTID(7S0), POLTYPE(4A), STARTDT(L), ENDDT(L), PREMIUM(9P2), STATUS(1A) |
| CLAIMPF | CLAIMNO | CLAIMNO(8S0), POLID(8S0), CLAIMDT(L), CLAIMTYPE(4A), AMOUNT(11P2), CLAIMSTS(1A), DESCR(50A) |
| CLAIML1 | POLID, CLAIMNO | Logical over CLAIMPF, keyed by POLID+CLAIMNO |

Status codes:
- `POLICYPF.STATUS`: A=Active, E=Expired, C=Cancelled
- `CLAIMPF.CLAIMSTS`: O=Open, A=Approved, R=Rejected, P=Paid

---

## API contract (target)

| Method | Path | Description |
|---|---|---|
| GET | `/policies` | List all policies (optionally filter by custid) |
| GET | `/policies/{pol_id}` | Get one policy by ID |
| GET | `/policies/{pol_id}/claims` | List claims for a policy |

All responses: JSON, ISO dates (`YYYY-MM-DD`), decimals as numbers.

---

## Bob usage log

_Append a one-line entry after each Bob session._

- 2026-10-21: Architecture decision, PUB400 capability analysis, project scaffold created.
