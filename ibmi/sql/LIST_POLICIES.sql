-- =============================================================
-- LIST_POLICIES
-- Library: ESH101
--
-- Returns all policies, optionally filtered by CUSTID.
-- Pass CUSTID = NULL (or 0) to get all policies.
--
-- Result set columns:
--   POLID, CUSTID, CUSTNAME, POLTYPE, STARTDT, ENDDT, PREMIUM, STATUS
--
-- Run in ACS to create:
--   Paste into Run SQL Scripts and execute.
-- =============================================================

CREATE OR REPLACE PROCEDURE ESH101.LIST_POLICIES (
    IN IN_CUSTID DECIMAL(7, 0)      -- pass NULL or 0 for all policies
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
        WHERE (IN_CUSTID IS NULL OR IN_CUSTID = 0 OR P.CUSTID = IN_CUSTID)
        ORDER BY P.POLID;

    OPEN C1;
END
