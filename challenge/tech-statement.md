# Written Statement on Technology

_For submission on the hackathon site — paste into the "Written statement on technology" field._
_This field is optional but recommended._

---

IBM Bob was the primary development tool throughout this project, used in every phase from initial architecture through final submission preparation.

In the architecture phase, Bob evaluated three connection options — JT400 JDBC, SSH tunneling, and ILEastic — against the constraints of a shared public IBM i server (PUB400.com). It recommended JT400 JDBC, justified the choice, and identified the specific ports to test. That decision proved correct and saved significant exploration time.

In the IBM i development phase, Bob wrote all four DDS source members (CUSTPF, POLICYPF, CLAIMPF, CLAIMLF1) with correct fixed-format column alignment and REFFLD syntax. It diagnosed real IBM i compiler errors from listing output — CPD7401 (missing R indicator in col 29), CPD7902 (unqualified PFILE), SQL0418 (DATE parameter marker in blocked INSERT) — and produced corrected source in each case. It wrote all three SQL stored procedures (LIST_POLICIES, GET_POLICY, LIST_CLAIMS) with DYNAMIC RESULT SETS syntax verified against PUB400's Db2 engine.

In the application development phase, Bob generated the full FastAPI scaffold including the JT400 JDBC connection module (JPype1 + JayDeBeApi with explicit JVM startup), Pydantic response models, live/mock data source switching, and the Python data seeder with --truncate flag. It generated the complete single-page web UI — search input, policy card with status pill, scrollable claims table, live/mock badge — without any build toolchain.

Bob also maintained the project's challenge/brief.md as a living memory document across sessions, recording decisions, open items, and verified capabilities — functioning as a persistent project context that survived session boundaries.

watsonx Orchestrate was not used in the current implementation. The natural next step would be to register the three FastAPI endpoints as Orchestrate skills, enabling an insurance agent to query policies and claims in plain English through an Orchestrate assistant — "Show me all open claims for policy 10000005" — with Orchestrate handling intent recognition and skill routing over the live IBM i data.
