-- =====================================================================
-- 06_demo_queries.sql : the SQL behind each implemented screen.
-- Run statement-by-statement in MySQL Workbench (Ctrl+Enter) during the demo.
-- Section B statements are SUPPOSED to fail - they show the triggers and
-- constraints rejecting bad data.
-- =====================================================================
USE puums;

-- =========================== A. SCREEN QUERIES ========================

-- [Screen 1] Login: role is read from the database, not chosen by the user
SELECT accountId, username, role
FROM UserAccount
WHERE username = '42101-1234567-1' AND passwordHash = SHA2('pass123', 256);

-- [Screen 2] Registration: account + citizen + premise in one transaction
CALL sp_RegisterCitizen('42101-7777777-7','Ali','Hassan','0333-7777777','ali.h@mail.com',
                        'pass123','9','Street 1','Malir Cantt',6,'Residential');
SELECT c.cnic, c.firstName, u.role, p.address, r.regionName
FROM Citizen c JOIN UserAccount u ON u.accountId = c.accountId
JOIN Premise p ON p.cnic = c.cnic JOIN Region r ON r.regionId = p.regionId
WHERE c.cnic = '42101-7777777-7';

-- [Screen 3] Citizen dashboard: premises + active-connection bills
SELECT p.address, p.premiseType, r.regionName,
       COUNT(sc.connectionId) AS activeConnections
FROM Premise p
JOIN Region r ON r.regionId = p.regionId
LEFT JOIN ServiceConnection sc ON sc.premiseId = p.premiseId AND sc.status = 'Active'
WHERE p.cnic = '42101-1234567-1'
GROUP BY p.premiseId, p.address, p.premiseType, r.regionName;

SELECT utility, provider, DATE_FORMAT(billingMonth,'%b %Y') AS month,
       totalAmount, balanceDue, dueDate, status
FROM vw_CitizenActiveBills
WHERE cnic = '42101-1234567-1'
ORDER BY billingMonth DESC, utility;

-- [Screen 14] Bill breakdown: slab lines, FPA, GST from the view
SELECT itemNo, chargeDescription, units, unitRate, lineAmount,
       previousReading, currentReading, unitsConsumed
FROM vw_BillLineItems
WHERE billId = 10
ORDER BY itemNo;

-- [Screen 13] My utility connections
SELECT pr.providerName, pr.utilityType, sc.consumerNo, sc.meterNo,
       p.area AS premise, sc.status, sc.connectionDate
FROM ServiceConnection sc
JOIN Premise p   ON p.premiseId   = sc.premiseId
JOIN Provider pr ON pr.providerId = sc.providerId
WHERE p.cnic = '42101-1234567-1';

-- [Screen 4] TRANSACTION SCREEN: pay electricity + gas (Sep) in one go
SELECT billId, utility, balanceDue, occVersion            -- what the screen loads
FROM vw_CitizenActiveBills
WHERE cnic = '42101-1234567-1' AND balanceDue > 0;

CALL sp_ProcessPayment('42101-1234567-1',
     (SELECT JSON_ARRAYAGG(JSON_OBJECT('billId', billId, 'ver', occVersion))
        FROM Bill WHERE billId IN (10, 14)),
     3911.58, 'Card', FALSE, @pid, @msg);
SELECT @pid AS paymentId, @msg AS result;

-- [Screen 16] Transaction ledger
SELECT transactionRef, paymentDate, amountPaid, paymentMethod,
       allocatedBills, transactionStatus
FROM vw_PaymentLedger
WHERE cnic = '42101-1234567-1'
ORDER BY paymentDate DESC;

-- [Screen 7] Meter reading entry: look up connection, then insert
SELECT sc.connectionId, sc.consumerNo, sc.meterNo, pr.providerName,
       CONCAT(c.firstName,' ',c.lastName) AS customer,
       (SELECT currentReading FROM MeterReading m
         WHERE m.connectionId = sc.connectionId
         ORDER BY readingMonth DESC LIMIT 1) AS lastReading
FROM ServiceConnection sc
JOIN Provider pr ON pr.providerId = sc.providerId
JOIN Premise p   ON p.premiseId   = sc.premiseId
JOIN Citizen c   ON c.cnic        = p.cnic
WHERE sc.consumerNo = 'SG-7788-2210' OR sc.meterNo = 'SG-7788-2210';

INSERT INTO MeterReading (readingMonth, readingDate, currentReading, connectionId, employeeId)
VALUES ('2026-10-01', CURDATE(), 3335, 2, 3);           -- previousReading filled by trigger
SELECT readingMonth, previousReading, currentReading,
       currentReading - previousReading AS units
FROM MeterReading WHERE connectionId = 2 ORDER BY readingMonth;

-- [Screen 10] Tariff management (history kept by effectiveDate)
SELECT pr.providerName, t.consumerCategory, s.slabNumber, s.minUnits, s.maxUnits,
       s.ratePerUnit, t.fixedCharges, t.fpaRate, t.gstPercent, t.effectiveDate
FROM Tariff t
JOIN TariffSlab s ON s.tariffId = t.tariffId
JOIN Provider pr  ON pr.providerId = t.providerId
ORDER BY pr.providerName, t.consumerCategory, t.effectiveDate, s.slabNumber;

-- Cascading tariff for 150 units of K-Electric residential in Sep vs Oct
CALL sp_CalculateCascadingTariff(1, 'Residential', '2026-09-01', 150, @t, @chg);
SELECT @t AS tariffUsed, @chg AS slabCharge;             -- 1000 + 750 = 1750
CALL sp_CalculateCascadingTariff(1, 'Residential', '2026-10-01', 150, @t, @chg);
SELECT @t AS tariffUsed, @chg AS slabCharge;             -- new Oct rates

-- [Screen 11] Providers and regions
SELECT providerId, providerName, utilityType, contactPhone, department FROM Provider;
SELECT regionId, regionName, city, province FROM Region;

-- [Screen 18] Monthly billing cycle for October (K-Electric only)
CALL sp_GenerateMonthlyBills('2026-10-01', 1, 'admin@puums.pk', @g, @s, @f);
SELECT @g AS billsGenerated, @s AS billsSkipped, @f AS billsFailed;
SELECT billingMonth, providerId, billsGenerated, billsSkipped, billsFailed, runBy, runAt
FROM BillingRun ORDER BY runAt DESC;

-- [Screen 9] Analytics (views)
SELECT * FROM vw_CollectionEfficiency ORDER BY billingMonth, providerName;
SELECT * FROM vw_OutstandingDebt;
SELECT * FROM vw_RegionalConsumption WHERE readingMonth = '2026-09-01';

-- [Screen 6] Employee task queue for Karachi East + KWSC
SELECT taskRef, taskType, customer, area, status
FROM vw_EmployeeTaskQueue
WHERE regionId = 1 AND providerId = 3;

-- ================== B. CONSTRAINT / TRIGGER / ACID DEMOS ==============
-- (each of these is expected to raise an error or roll back)

-- trg_validate_meter_reading: reading lower than previous
INSERT INTO MeterReading (readingMonth, readingDate, currentReading, connectionId, employeeId)
VALUES ('2026-10-01', CURDATE(), 100, 3, 4);

-- trg_validate_meter_reading: second reading for the same month
INSERT INTO MeterReading (readingMonth, readingDate, currentReading, connectionId, employeeId)
VALUES ('2026-09-01', CURDATE(), 99999, 1, 2);

-- trg_prevent_overpayment: allocate more than the bill's balance
INSERT INTO PaymentAllocation (paymentId, billId, allocatedAmount) VALUES (1, 12, 999999);

-- trg_prevent_overlapping_tariff: duplicate effective date
INSERT INTO Tariff (consumerCategory, fixedCharges, fpaRate, gstPercent, effectiveDate, providerId)
VALUES ('Residential', 200, 2, 18, '2026-07-01', 1);

-- CHECK constraint: malformed CNIC
INSERT INTO Citizen (cnic, firstName, lastName, accountId) VALUES ('123', 'X', 'Y', 1);

-- ACID: amount above outstanding -> ROLLBACK, failed attempt logged
CALL sp_ProcessPayment('42101-3456789-3',
     (SELECT JSON_ARRAYAGG(JSON_OBJECT('billId', billId, 'ver', occVersion)) FROM Bill WHERE billId = 12),
     999999, 'Card', FALSE, @pid, @msg);
SELECT @pid, @msg;

-- ACID: stale OCC version (screen loaded version 0, bill is already at 1+)
CALL sp_ProcessPayment('42101-1234567-1', '[{"billId": 1, "ver": 0}]', 100, 'Card', FALSE, @pid, @msg);
SELECT @pid, @msg;

-- ACID: simulated network drop after all 3 steps -> nothing persists
SELECT billId, balanceDue, status FROM vw_BillBalance WHERE billId = 12;
CALL sp_ProcessPayment('42101-3456789-3',
     (SELECT JSON_ARRAYAGG(JSON_OBJECT('billId', billId, 'ver', occVersion)) FROM Bill WHERE billId = 12),
     500, 'Card', TRUE, @pid, @msg);
SELECT @pid, @msg;
SELECT billId, balanceDue, status FROM vw_BillBalance WHERE billId = 12;   -- unchanged

-- Audit trail written by trg_complaint_status_log
SELECT * FROM ComplaintStatusLog ORDER BY changedAt;
