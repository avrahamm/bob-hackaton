# ibmi/ — IBM i source members

This directory mirrors the source members on PUB400 (library ESH101).
Edit here on your workstation and upload with Code for IBM i, or edit
directly on the IBM i and download. Both workflows work.

## Layout

```
ibmi/
├── dds/            ← Physical files (.pf) and logical files (.lf)
│   ├── CUSTPF.pf
│   ├── POLICYPF.pf
│   ├── CLAIMPF.pf
│   └── CLAIML1.lf
├── rpgle/          ← ILE RPG programs and service programs
│   ├── POLSRV.rpgle        (service program: getPolicy, listPolicies, getClaims)
│   ├── POLMAIN.rpgle       (test caller — uses native I/O, *INLR)
│   └── POLSCR.rpgle        (display file program — legacy green screen, READ-ONLY ref)
├── sql/            ← SQL stored procedures
│   ├── LIST_POLICIES.sql
│   ├── GET_POLICY.sql
│   └── LIST_CLAIMS.sql
└── README.md       ← THIS FILE
```

## Source member types on IBM i

| Extension | IBM i type | SRCPF member type |
|-----------|-----------|-------------------|
| .pf       | DDS       | PF                |
| .lf       | DDS       | LF                |
| .dspf     | DDS       | DSPF              |
| .rpgle    | ILE RPG   | RPGLE             |
| .sql      | SQL       | (run via ACS)     |

## Compile order

1. CRTPF   — CUSTPF, POLICYPF, CLAIMPF (physical files first)
2. CRTLF   — CLAIML1 (logical over CLAIMPF)
3. Load data — run challenge/data/synthetic_insert.sql via ACS
4. CRTRPGMOD — POLSRV (service module)
5. CRTSRVPGM — bind POLSRV into a *SRVPGM
6. CRTBNDRPG — POLMAIN (test caller, bound to POLSRV)
7. Run SQL procedures — paste each .sql file into ACS Run SQL Scripts
