# Written Problem and Solution Statement

_For submission on the hackathon site — paste into the "Written problem and solution statement" field._
_Word count: 497 / 500 max_

---

Thousands of companies worldwide run critical business processes on IBM i (AS/400) systems. These systems are reliable and proven, but their interfaces — green-screen 5250 terminals driven by RPG programs — are invisible to modern tooling, hard to integrate with web or mobile applications, and increasingly difficult to hand to new staff who have never seen a terminal emulator.

The specific problem this project addresses: an insurance agent at a company running IBM i must navigate multiple 5250 screens to look up a policy and its associated claims. The data lives in Db2 physical files defined in DDS, accessed by RPG programs through native file I/O. There is no REST API, no web interface, and no path for a browser or mobile app to access this data without a terminal session. The challenge for most organisations is not that they want to rewrite these systems — the RPG programs are well-tested, the data is correct, the business logic is proven over decades. The challenge is exposing that data through a modern interface without touching the legacy core.

The solution is a thin modernisation layer built on a real, live IBM i server. The entire project runs against PUB400.com, a publicly accessible IBM i system running IBM i V7R5. This is not a simulation or a local mock — the data lives in real Db2 physical files on a real IBM i partition, compiled from DDS source, and queried through real SQL stored procedures:

- DDS physical files (CUSTPF, POLICYPF, CLAIMPF, CLAIMLF1) were compiled on PUB400 in library ESH101 — the same way they would be deployed at any IBM i customer site
- Synthetic insurance data — 5 customers, 8 policies, 10 claims — was seeded directly into those tables on PUB400 via JT400 JDBC from a Python script
- SQL stored procedures (LIST_POLICIES, GET_POLICY, LIST_CLAIMS) were deployed on PUB400 and return dynamic result sets
- A FastAPI service connects to PUB400 over JT400 JDBC (port 446/449, the same driver IBM ACS uses), calls the stored procedures live, and serves JSON
- A single-page web UI lets an insurance agent type a policy ID and see the policy card and claims history in a browser — data pulled live from IBM i on every request

The target user is any developer or architect at a company with an IBM i system who wants to expose legacy data to modern applications. The approach is repeatable: DDS → stored procedures → JDBC → REST API → web UI applies to any IBM i read workflow.

IBM Bob was used at every stage: architectural decisions, writing and debugging DDS sources on a real IBM i compiler, writing the SQL stored procedures, generating the FastAPI scaffold, building the web UI, diagnosing IBM i-specific compiler errors, and maintaining project memory across sessions. Every piece of code was written or reviewed with Bob — the full session exports are in the repository.

What makes this creative is the demonstration that IBM i modernisation does not require a rewrite, a cloud migration, or specialised middleware. A developer with standard web skills, IBM Bob, and access to any IBM i system — even a free public one — can expose a legacy workflow to a modern browser in a single hackathon week.
