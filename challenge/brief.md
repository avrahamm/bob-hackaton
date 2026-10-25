# Challenge brief — Insurance policy lookup: IBM i RPG to modern API

_Last updated: 2026-10-23. Read this at the start of every Bob session._

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
- [x] How JayDeBeApi returns DYNAMIC RESULT SETS from CALL — **confirmed: `fetchall()` on same cursor after `CALL`**
- [x] Whether PUB400 allows `CREATE PROCEDURE` returning result sets — **confirmed via TEST_PROC2**
- [x] Compile CUSTPF, POLICYPF, CLAIMPF, CLAIMLF1 on PUB400 ← **done 2026-10-25**
- [x] Load synthetic data (`challenge/data/synthetic_insert.sql`) on PUB400 ← **done 2026-10-25**
- [ ] Write + compile SQL stored procedures: LIST_POLICIES, GET_POLICY, LIST_CLAIMS ← **Day 2 next**
- [ ] Call insurance stored procedures from FastAPI (flip `DATA_SOURCE=live`)
- [ ] RPG service program: POLSRV with getPolicy, listPolicies, getClaims (native I/O)
- [ ] Minimal web UI (Day 9–10)
- [ ] Cloud deployment (deferred)

---

## Environment

| Component | Detail |
|---|---|
| IBM i | PUB400.com, library ESH101, account confirmed |
| Primary dev machine | Ubuntu PC — IBM ACS + 5250 emulator working, Bob IDE + IBM i extension working |
| Secondary machine | Mac 2021 (64 GB) — Bob IDE + IBM i extension connected; ACS **not working** on Mac; no 5250 emulator on Mac; `tn5250` or Mochasoft as 5250 alternative |
| FastAPI | Runs on Ubuntu **or Mac** (mock mode works anywhere) |
| Python | 3.13 in `.venv` under `api/` (confirmed working on Mac) |
| JT400 jar | `api/lib/jt400.jar` — `jt400-21.0.7-java11.jar`, **not in git** |
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
├── challenge/              ← this folder (brief, blueprint, demo notes)
│   ├── brief.md            ← YOU ARE HERE
│   ├── data/
│   │   └── synthetic_insert.sql  ← run in ACS to load test data
│   └── blueprint.html      ← generated later
├── ibmi/                   ← DDS, RPGLE, SQL procedure sources
│   ├── dds/
│   │   ├── CUSTPF.pf       ← ✅ written, ready to upload+compile
│   │   ├── POLICYPF.pf     ← ✅ written (REFFLD from CUSTPF)
│   │   ├── CLAIMPF.pf      ← ✅ written (REFFLD from POLICYPF)
│   │   └── CLAIMLF1.lf     ← ✅ written (PFILE CLAIMPF, key POLID+CLAIMNO)
│   ├── rpgle/              ← Day 4: POLSRV service program
│   └── sql/                ← Day 2: stored procedures go here
├── api/                    ← FastAPI project
│   ├── main.py             ← 3 endpoints, live+mock switch
│   ├── db.py               ← JT400 JDBC connection (explicit JVM start)
│   ├── test_jt400.py       ← smoke test — ✅ passes against pub400
│   ├── requirements.txt
│   ├── env.example         ← copy to .env, fill credentials
│   ├── mock_data/
│   │   ├── policies.json   ← golden fixture
│   │   └── claims.json     ← golden fixture
│   └── lib/                ← jt400.jar goes here (NOT in git)
└── ui/                     ← minimal web UI (Day 9–10)
```

---

## Physical files (DDS) — defined and written

DDS sources use `REFFLD` for shared key fields (FK documentation + single point of definition).
Compile order: CUSTPF → POLICYPF → CLAIMPF → CLAIML1.

| File | Key | Notable |
|---|---|---|
| CUSTPF | CUSTID(7S0) | Root — CUSTID defined here |
| POLICYPF | POLID(8S0) | CUSTID via `REFFLD(CUSTID CUSTPF)` |
| CLAIMPF | CLAIMNO(8S0) | POLID via `REFFLD(POLID POLICYPF)`; DATFMT(*ISO) on all dates |
| CLAIMLF1 | POLID + CLAIMNO | Logical over CLAIMPF — used by RPG READE loop |

Status codes:
- `POLICYPF.STATUS`: A=Active, E=Expired, C=Cancelled
- `CLAIMPF.CLAIMSTS`: O=Open, A=Approved, R=Rejected, P=Paid
- `POLICYPF.POLTYPE`: AUTO, LIFE, HOME, HEAL
- `CLAIMPF.CLAIMTYPE`: COLL, LIAB, FIRE, DISA, HOSP, DRUG, WIND

### JT400 / Python type mapping (confirmed)
| IBM i type | DDS | Python (JayDeBeApi) | JSON |
|---|---|---|---|
| Zoned decimal | 7S0, 8S0 | `int` or `Decimal` — cast with `int()` | number |
| Packed decimal | 9P2, 11P2 | `Decimal` — cast with `float()` | number |
| Date (ISO) | L + DATFMT(*ISO) | string `'YYYY-MM-DD'` | string |
| Char | 40A, 4A, 1A | string with trailing spaces — use `.strip()` | string |

---

## API contract (target)

| Method | Path | Description |
|---|---|---|
| GET | `/policies` | List all policies (optionally filter by custid) |
| GET | `/policies/{pol_id}` | Get one policy by ID |
| GET | `/policies/{pol_id}/claims` | List claims for a policy |

All responses: JSON, ISO dates (`YYYY-MM-DD`), decimals as numbers.

---

## Day 2 — instructions for next Bob session

Start a new task and open with:
> "Read challenge/brief.md. We are on Day 2. DDS sources are in ibmi/dds/ — ready to upload and compile on PUB400. Next: compile them (CUSTPF→POLICYPF→CLAIMPF→CLAIML1), load synthetic_insert.sql, then write three SQL stored procedures in ibmi/sql/: LIST_POLICIES, GET_POLICY, LIST_CLAIMS. Then wire FastAPI to call them with DATA_SOURCE=live."

---

## Bob usage log

_Append a one-line entry after each Bob session._

- 2026-10-21: Architecture decision, PUB400 capability analysis, project scaffold created.
- 2026-10-22: JT400 JDBC confirmed working (Mac+Ubuntu). API scaffold built. Mock data wired. DDS sources written with REFFLD. Repo committed and pushed.
