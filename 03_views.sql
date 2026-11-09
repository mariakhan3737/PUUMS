-- =====================================================================
-- 03_views.sql  (proposal section 2.9.5)
-- Derived values (bill total, balance, units used) are computed here,
-- not stored, which keeps the base tables in 3NF.
-- =====================================================================
USE puums;

-- Helper: each bill with total, amount paid and remaining balance
CREATE OR REPLACE VIEW vw_BillBalance AS
SELECT  b.billId,
        b.connectionId,
        b.billingMonth,
        b.dueDate,
        b.status,
        b.occVersion,
        (b.baseAmount + b.fpaAmount + b.gstAmount + b.tankerArrears)          AS totalAmount,
        COALESCE(pa.paid, 0)                                                   AS paidAmount,
        (b.baseAmount + b.fpaAmount + b.gstAmount + b.tankerArrears)
            - COALESCE(pa.paid, 0)                                             AS balanceDue
FROM Bill b
LEFT JOIN (SELECT billId, SUM(allocatedAmount) AS paid
             FROM PaymentAllocation GROUP BY billId) pa
       ON pa.billId = b.billId;

-- Screen 3 / 4: bill grid limited to the citizen's ACTIVE connections
CREATE OR REPLACE VIEW vw_CitizenActiveBills AS
SELECT  p.cnic,
        bb.billId,
        pr.utilityType                              AS utility,
        pr.providerName                             AS provider,
        sc.consumerNo,
        bb.billingMonth,
        bb.totalAmount,
        bb.balanceDue,
        bb.dueDate,
        bb.status,
        bb.occVersion
FROM vw_BillBalance bb
JOIN ServiceConnection sc ON sc.connectionId = bb.connectionId
JOIN Premise  p           ON p.premiseId     = sc.premiseId
JOIN Provider pr          ON pr.providerId   = sc.providerId
WHERE sc.status = 'Active';

-- Screen 14: invoice breakdown (header + line items)
CREATE OR REPLACE VIEW vw_BillLineItems AS
SELECT  b.billId,
        pr.providerName,
        pr.utilityType,
        sc.consumerNo,
        sc.meterNo,
        b.billingMonth,
        b.dueDate,
        b.status,
        mr.previousReading,
        mr.currentReading,
        (mr.currentReading - mr.previousReading)    AS unitsConsumed,
        li.itemNo,
        li.chargeDescription,
        li.units,
        li.unitRate,
        ROUND(li.units * li.unitRate, 2)            AS lineAmount
FROM Bill b
JOIN ServiceConnection sc ON sc.connectionId = b.connectionId
JOIN Provider pr          ON pr.providerId   = sc.providerId
JOIN BillLineItem li      ON li.billId       = b.billId
LEFT JOIN MeterReading mr ON mr.connectionId = b.connectionId
                         AND mr.readingMonth = b.billingMonth;

-- Screen 16: payment ledger with the bills each payment was allocated to
CREATE OR REPLACE VIEW vw_PaymentLedger AS
SELECT  pay.paymentId,
        CONCAT('TXN-', LPAD(pay.paymentId, 5, '0'))  AS transactionRef,
        pay.cnic,
        pay.paymentDate,
        pay.amountPaid,
        pay.paymentMethod,
        pay.transactionStatus,
        COALESCE(GROUP_CONCAT(CONCAT(pr.utilityType, ' ', DATE_FORMAT(b.billingMonth, '%b %Y'),
                              ' (Rs. ', pa.allocatedAmount, ')')
                              ORDER BY b.dueDate SEPARATOR '; '), '-') AS allocatedBills
FROM Payment pay
LEFT JOIN PaymentAllocation pa ON pa.paymentId    = pay.paymentId
LEFT JOIN Bill b               ON b.billId        = pa.billId
LEFT JOIN ServiceConnection sc ON sc.connectionId = b.connectionId
LEFT JOIN Provider pr          ON pr.providerId   = sc.providerId
GROUP BY pay.paymentId, pay.cnic, pay.paymentDate, pay.amountPaid,
         pay.paymentMethod, pay.transactionStatus;

-- Screen 9: unpaid / partially paid bills by provider and region
CREATE OR REPLACE VIEW vw_OutstandingDebt AS
SELECT  pr.providerName,
        r.regionName,
        COUNT(*)                 AS unpaidBills,
        SUM(bb.balanceDue)       AS amountOutstanding,
        MIN(bb.dueDate)          AS oldestDueDate
FROM vw_BillBalance bb
JOIN ServiceConnection sc ON sc.connectionId = bb.connectionId
JOIN Premise p            ON p.premiseId     = sc.premiseId
JOIN Region r             ON r.regionId      = p.regionId
JOIN Provider pr          ON pr.providerId   = sc.providerId
WHERE bb.balanceDue > 0
GROUP BY pr.providerName, r.regionName;

-- Screen 9: collection efficiency per billing month and provider
CREATE OR REPLACE VIEW vw_CollectionEfficiency AS
SELECT  bb.billingMonth,
        pr.providerName,
        SUM(bb.totalAmount)                                       AS amountBilled,
        SUM(bb.paidAmount)                                        AS amountCollected,
        ROUND(100 * SUM(bb.paidAmount) / NULLIF(SUM(bb.totalAmount), 0), 1) AS efficiencyPct
FROM vw_BillBalance bb
JOIN ServiceConnection sc ON sc.connectionId = bb.connectionId
JOIN Provider pr          ON pr.providerId   = sc.providerId
GROUP BY bb.billingMonth, pr.providerName;

-- Screen 9 heatmap: units consumed per region and utility
CREATE OR REPLACE VIEW vw_RegionalConsumption AS
SELECT  mr.readingMonth,
        r.regionName,
        SUM(CASE WHEN pr.utilityType = 'Electricity' THEN mr.currentReading - mr.previousReading ELSE 0 END) AS electricityUnits,
        SUM(CASE WHEN pr.utilityType = 'Gas'         THEN mr.currentReading - mr.previousReading ELSE 0 END) AS gasUnits,
        SUM(CASE WHEN pr.utilityType = 'Piped Water' THEN mr.currentReading - mr.previousReading ELSE 0 END) AS waterUnits
FROM MeterReading mr
JOIN ServiceConnection sc ON sc.connectionId = mr.connectionId
JOIN Premise p            ON p.premiseId     = sc.premiseId
JOIN Region r             ON r.regionId      = p.regionId
JOIN Provider pr          ON pr.providerId   = sc.providerId
GROUP BY mr.readingMonth, r.regionName;

-- Screen 6: open work for an employee's region + provider
CREATE OR REPLACE VIEW vw_EmployeeTaskQueue AS
SELECT  CONCAT('CMP-', c.ticketId)              AS taskRef,
        'Complaint'                              AS taskType,
        CONCAT(ci.firstName, ' ', ci.lastName)   AS customer,
        p.area,
        c.status,
        p.regionId,
        c.providerId,
        c.filingDate                             AS taskDate
FROM Complaint c
JOIN Citizen ci ON ci.cnic     = c.cnic
JOIN Premise p  ON p.premiseId = c.premiseId
WHERE c.status <> 'Resolved'
UNION ALL
SELECT  CONCAT('T-', tr.requestId),
        'Water Tanker',
        CONCAT(ci.firstName, ' ', ci.lastName),
        tr.deliveryAddress,
        tr.status,
        (SELECT MIN(p2.regionId) FROM Premise p2 WHERE p2.cnic = tr.cnic),
        (SELECT providerId FROM Provider WHERE utilityType = 'Piped Water' LIMIT 1),
        tr.deliveryDate
FROM TankerRequest tr
JOIN Citizen ci ON ci.cnic = tr.cnic
WHERE tr.status IN ('Pending','Dispatched');
