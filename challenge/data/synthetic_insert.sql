-- =============================================================
-- Synthetic insurance data for ESH101 on PUB400
-- ALL DATA IS INVENTED. No real customers, policies or claims.
-- Run in ACS Run SQL Scripts against your library.
-- =============================================================

-- Prerequisites: CUSTPF, POLICYPF, CLAIMPF must already exist.
-- Create them with CRTPF from DDS before running this script.

-- -----------------------------------------------
-- Customers
-- -----------------------------------------------
INSERT INTO ESH101.CUSTPF (CUSTID, CUSTNAME, PHONE, CITY) VALUES
  (1000001, 'Hartwell Insurance Test Co', '555-0101', 'Chicago'),
  (1000002, 'Brennan Fixtures LLC',       '555-0102', 'Dallas'),
  (1000003, 'Okafor Demo Agency',         '555-0103', 'Atlanta'),
  (1000004, 'Yılmaz Sample Group',        '555-0104', 'Detroit'),
  (1000005, 'Patel Synthetic Corp',       '555-0105', 'Seattle');

-- -----------------------------------------------
-- Policies
-- STATUS: A=Active  E=Expired  C=Cancelled
-- POLTYPE: AUTO LIFE HOME HEAL
-- -----------------------------------------------
INSERT INTO ESH101.POLICYPF (POLID, CUSTID, POLTYPE, STARTDT, ENDDT, PREMIUM, STATUS) VALUES
  (10000001, 1000001, 'AUTO', DATE('2024-01-01'), DATE('2025-01-01'), 1200.00, 'E'),
  (10000002, 1000001, 'HOME', DATE('2024-03-15'), DATE('2025-03-15'), 2400.50, 'A'),
  (10000003, 1000002, 'LIFE', DATE('2023-06-01'), DATE('2033-06-01'), 800.00,  'A'),
  (10000004, 1000002, 'AUTO', DATE('2022-01-01'), DATE('2023-01-01'), 950.75,  'E'),
  (10000005, 1000003, 'HEAL', DATE('2025-01-01'), DATE('2026-01-01'), 3100.00, 'A'),
  (10000006, 1000003, 'HOME', DATE('2020-05-10'), DATE('2021-05-10'), 1800.00, 'C'),
  (10000007, 1000004, 'AUTO', DATE('2025-04-01'), DATE('2026-04-01'), 1050.00, 'A'),
  (10000008, 1000005, 'LIFE', DATE('2024-07-01'), DATE('2034-07-01'), 600.00,  'A');

-- -----------------------------------------------
-- Claims
-- CLAIMSTS: O=Open  A=Approved  R=Rejected  P=Paid
-- -----------------------------------------------
INSERT INTO ESH101.CLAIMPF (CLAIMNO, POLID, CLAIMDT, CLAIMTYPE, AMOUNT, CLAIMSTS, DESCR) VALUES
  (20000001, 10000001, DATE('2024-08-15'), 'COLL', 3500.00, 'P', 'Rear-end collision on I-90'),
  (20000002, 10000001, DATE('2024-11-01'), 'LIAB', 1200.00, 'A', 'Third-party liability claim'),
  (20000003, 10000002, DATE('2024-09-20'), 'FIRE', 8500.00, 'O', 'Kitchen fire damage'),
  (20000004, 10000003, DATE('2024-06-05'), 'DISA', 5000.00, 'A', 'Short-term disability payout'),
  (20000005, 10000004, DATE('2022-09-10'), 'COLL', 4200.00, 'P', 'Parking lot collision'),
  (20000006, 10000005, DATE('2025-03-01'), 'HOSP', 12000.00,'O', 'Emergency hospitalisation'),
  (20000007, 10000005, DATE('2025-05-14'), 'DRUG',  450.00, 'A', 'Prescription reimbursement'),
  (20000008, 10000007, DATE('2025-07-22'), 'COLL', 2100.00, 'O', 'Side-swipe on highway'),
  (20000009, 10000007, DATE('2025-08-30'), 'WIND',  780.00, 'R', 'Hailstorm claim outside coverage'),
  (20000010, 10000008, DATE('2024-10-01'), 'DISA', 2500.00, 'P', 'Disability benefit paid');
