-- =============================================================
-- LIST_CLAIMS
-- Library: ESH101
--
-- Returns all claims for a given POLID, ordered by CLAIMDT DESC.
--
-- Result set columns:
--   CLAIMNO, POLID, CLAIMDT, CLAIMTYPE, AMOUNT, CLAIMSTS, DESCR
--
-- Run in ACS to create:
--   Paste into Run SQL Scripts and execute.
-- =============================================================

CREATE OR REPLACE PROCEDURE ESH101.LIST_CLAIMS (
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
            CLAIMNO,
            POLID,
            CLAIMDT,
            TRIM(CLAIMTYPE)  AS CLAIMTYPE,
            AMOUNT,
            TRIM(CLAIMSTS)   AS CLAIMSTS,
            TRIM(DESCR)      AS DESCR
        FROM  ESH101.CLAIMPF
        WHERE POLID = IN_POLID
        ORDER BY CLAIMDT DESC, CLAIMNO;

    OPEN C1;
END
