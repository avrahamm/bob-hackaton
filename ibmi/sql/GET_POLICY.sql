-- =============================================================
-- GET_POLICY
-- Library: ESH101
--
-- Returns a single policy row by POLID, joined with customer name.
-- Returns an empty result set if POLID not found (HTTP 404 handled
-- in Python by checking len(rows) == 0).
--
-- Result set columns:
--   POLID, CUSTID, CUSTNAME, POLTYPE, STARTDT, ENDDT, PREMIUM, STATUS
--
-- Run in ACS to create:
--   Paste into Run SQL Scripts and execute.
-- =============================================================

CREATE OR REPLACE PROCEDURE ESH101.GET_POLICY (
    IN IN_POLID DECIMAL(8, 0)
)
DYNAMIC RESULT SETS 1
LANGUAGE SQL
NOT DETERMINISTIC
READS SQL DATA
SET OPTION COMMIT = *NONE

BEGIN
    DECLARE C1 CURSOR WITH RETURN FOR
        SELECT
            P.POLID,
            P.CUSTID,
            TRIM(C.CUSTNAME)  AS CUSTNAME,
            TRIM(P.POLTYPE)   AS POLTYPE,
            P.STARTDT,
            P.ENDDT,
            P.PREMIUM,
            TRIM(P.STATUS)    AS STATUS
        FROM  ESH101.POLICYPF P
        JOIN  ESH101.CUSTPF   C ON C.CUSTID = P.CUSTID
        WHERE P.POLID = IN_POLID;

    OPEN C1;
END
