-- =====================================================================
-- 05_seed.sql : pilot-region (Karachi) demo data
-- All demo passwords: pass123   (Super-Admin: admin@puums.pk / admin123)
-- =====================================================================
USE puums;

-- Regions (Setup Screen 2)
INSERT INTO Region (regionName, city, province) VALUES
 ('Karachi East','Karachi','Sindh'), ('Karachi West','Karachi','Sindh'),
 ('Karachi South','Karachi','Sindh'), ('Karachi Central','Karachi','Sindh'),
 ('Korangi','Karachi','Sindh'), ('Malir','Karachi','Sindh'), ('Keamari','Karachi','Sindh');

-- Providers (Setup Screen 2)
INSERT INTO Provider (providerName, utilityType, contactPhone, department) VALUES
 ('K-Electric','Electricity','021-9901-2345','Electricity Dept'),
 ('SSGC','Gas','021-9902-3456','Gas Dept'),
 ('KWSC','Piped Water','021-9903-4567','Water Dept');

-- First Super-Admin is created by the setup script (proposal 2.2)
INSERT INTO UserAccount (username, passwordHash, role)
VALUES ('admin@puums.pk', SHA2('admin123', 256), 'Super-Admin');
INSERT INTO Employee (name, phone, email, role, department, accountId)
VALUES ('System Admin','0300-0000000','admin@puums.pk','Admin','IT', LAST_INSERT_ID());

-- Employees with logins, created through the provisioning procedure
CALL sp_ProvisionEmployee('Fatima Noor','0303-1122334','fatima.noor@puums.pk','Meter Reader','Electricity',1,1,'pass123','Employee',@e);
CALL sp_ProvisionEmployee('Usman Tariq','0304-5566778','usman.tariq@puums.pk','Meter Reader','Gas',2,1,'pass123','Employee',@e);
CALL sp_ProvisionEmployee('Ahmad Khan','0301-2345678','ahmad.khan@puums.pk','Dispatcher','Water',3,1,'pass123','Employee',@e);

-- Drivers (no login)
INSERT INTO Employee (name, phone, role, department, providerId, regionId) VALUES
 ('Imran Sheikh','0302-8765432','Driver','Water',3,1),
 ('Rashid Mehmood','0305-1239876','Driver','Water',3,1),
 ('Kashif Ali','0306-4561237','Driver','Water',3,4);

-- Citizens self-register (Screen 2) -> account + citizen + primary premise
CALL sp_RegisterCitizen('42101-1234567-1','Maria','Khan','0321-1111111','maria.khan@mail.com','pass123','12','Street 5','Gulshan-e-Iqbal',1,'Residential');
CALL sp_RegisterCitizen('42101-2345678-2','Bilal','Ahmed','0322-2222222','bilal.ahmed@mail.com','pass123','B-44','Block 13','Federal B Area',4,'Residential');
CALL sp_RegisterCitizen('42101-3456789-3','Sana','Raza','0323-3333333','sana.raza@mail.com','pass123','7','Street 2','Gulshan-e-Iqbal',1,'Residential');
CALL sp_RegisterCitizen('42301-4567890-4','Hamza','Siddiqui','0324-4444444','hamza.s@mail.com','pass123','Shop 3','Zaibunnisa St','Saddar',3,'Commercial');

-- Service connections (Screen 13)   premiseId 1..4 follow registration order
INSERT INTO ServiceConnection (consumerNo, meterNo, connectionDate, status, premiseId, providerId) VALUES
 ('KE-0412345','KE68689','2024-03-01','Active',1,1),
 ('SG-7788-2210','GM-204518','2024-03-01','Active',1,2),
 ('KW-55-0912','WM-33021','2024-03-01','Active',1,3),
 ('KE-0533001','KE70112','2023-06-15','Active',2,1),
 ('SG-7788-3301','GM-205990','2023-06-15','Active',2,2),
 ('KE-0611872','KE71555','2025-01-10','Active',3,1),
 ('KW-55-1408','WM-34110','2025-01-10','Active',3,3),
 ('KE-0900456','KE80001','2022-09-01','Active',4,1),
 ('SG-9900-0456','GM-300045','2022-09-01','Active',4,2);

-- Tariffs (Setup Screen 1). K-Electric residential gets a revision on 1 Oct
-- to show that historical rates are preserved by effectiveDate.
INSERT INTO Tariff (consumerCategory, fixedCharges, fpaRate, gstPercent, effectiveDate, providerId) VALUES
 ('Residential', 200, 2.00, 18, '2026-07-01', 1),   -- 1
 ('Commercial', 1000, 2.00, 18, '2026-07-01', 1),   -- 2
 ('Residential', 150, 0.00, 17, '2026-07-01', 2),   -- 3
 ('Commercial',  500, 0.00, 17, '2026-07-01', 2),   -- 4
 ('Residential', 300, 0.00,  0, '2026-07-01', 3),   -- 5
 ('Commercial',  800, 0.00,  0, '2026-07-01', 3),   -- 6
 ('Residential', 200, 2.50, 18, '2026-10-01', 1);   -- 7 (revision)

INSERT INTO TariffSlab (tariffId, slabNumber, minUnits, maxUnits, ratePerUnit) VALUES
 (1,1,0,100,10.00),(1,2,101,150,15.00),(1,3,151,300,22.00),(1,4,301,NULL,30.00),
 (2,1,0,500,28.00),(2,2,501,NULL,35.00),
 (3,1,0,100,12.00),(3,2,101,200,20.00),(3,3,201,NULL,35.00),
 (4,1,0,NULL,40.00),
 (5,1,0,20,25.00),(5,2,21,40,35.00),(5,3,41,NULL,50.00),
 (6,1,0,NULL,60.00),
 (7,1,0,100,11.00),(7,2,101,150,16.50),(7,3,151,300,24.00),(7,4,301,NULL,32.00);

-- Meter readings (Screen 7). July = baseline; Aug & Sep billed below;
-- Oct only for K-Electric so the rest can be entered live in the demo.
-- previousReading is left NULL: trg_validate_meter_reading fills it.
INSERT INTO MeterReading (readingMonth, readingDate, currentReading, connectionId, employeeId) VALUES
 ('2026-07-01','2026-07-28',12040,1,2),('2026-07-01','2026-07-28',3100,2,3),('2026-07-01','2026-07-28',880,3,4),
 ('2026-07-01','2026-07-28',20500,4,2),('2026-07-01','2026-07-28',5400,5,3),('2026-07-01','2026-07-28',9800,6,2),
 ('2026-07-01','2026-07-28',410,7,4),('2026-07-01','2026-07-28',51000,8,2),('2026-07-01','2026-07-28',7700,9,3);
INSERT INTO MeterReading (readingMonth, readingDate, currentReading, connectionId, employeeId) VALUES
 ('2026-08-01','2026-08-28',12210,1,2),('2026-08-01','2026-08-28',3185,2,3),('2026-08-01','2026-08-28',912,3,4),
 ('2026-08-01','2026-08-28',20820,4,2),('2026-08-01','2026-08-28',5530,5,3),('2026-08-01','2026-08-28',9915,6,2),
 ('2026-08-01','2026-08-28',438,7,4),('2026-08-01','2026-08-28',51720,8,2),('2026-08-01','2026-08-28',7960,9,3);
INSERT INTO MeterReading (readingMonth, readingDate, currentReading, connectionId, employeeId) VALUES
 ('2026-09-01','2026-09-28',12360,1,2),('2026-09-01','2026-09-28',3262,2,3),('2026-09-01','2026-09-28',940,3,4),
 ('2026-09-01','2026-09-28',21090,4,2),('2026-09-01','2026-09-28',5640,5,3),('2026-09-01','2026-09-28',10040,6,2),
 ('2026-09-01','2026-09-28',461,7,4),('2026-09-01','2026-09-28',52380,8,2),('2026-09-01','2026-09-28',8190,9,3);
INSERT INTO MeterReading (readingMonth, readingDate, currentReading, connectionId, employeeId) VALUES
 ('2026-10-01','2026-10-28',12490,1,2),('2026-10-01','2026-10-28',21300,4,2),
 ('2026-10-01','2026-10-28',10160,6,2),('2026-10-01','2026-10-28',53010,8,2);

-- Tanker pricing (Screen 17) and fleet (Setup Screen 3)
INSERT INTO TankerRate (capacityTier, baseFlatRate, urgencySurcharge, effectiveDate) VALUES
 (1000,1500,300,'2026-10-01'),(2000,2500,500,'2026-10-01'),(5000,5500,1000,'2026-10-01');
INSERT INTO Tanker (vehicleNo, capacityLiters, status, lastMaintenanceDate, capacityTier, driverId) VALUES
 ('TK-201',5000,'Available','2026-09-15',5000,5),
 ('TK-188',2000,'Available','2026-08-20',2000,6),
 ('TK-210',2000,'Available','2026-09-30',2000,7),
 ('TK-175',1000,'Maintenance','2026-11-01',1000,NULL);

-- Tanker requests (Screen 5)
INSERT INTO TankerRequest (deliveryDate, urgency, deliveryAddress, status, cnic, vehicleNo, capacityTier, cost) VALUES
 ('2026-10-02','Standard','House 12, Street 5, Gulshan-e-Iqbal','Delivered','42101-1234567-1','TK-188',2000,2500),
 ('2026-11-12','Standard','House 12, Street 5, Gulshan-e-Iqbal','Pending','42101-1234567-1',NULL,5000,5500),
 ('2026-11-10','Urgent','House B-44, Block 13, Federal B Area','Pending','42101-2345678-2',NULL,2000,3000);
CALL sp_AssignTanker(3, 'TK-188', @msg);          -- Bilal's urgent order -> Dispatched, TK-188 Busy

-- Complaints (Screen 15) + status moves so the audit trigger logs them
INSERT INTO Complaint (category, filingDate, description, status, cnic, premiseId, providerId) VALUES
 ('Outage','2026-09-28 10:15:00','No electricity since morning in our lane.','Open','42101-1234567-1',1,1),
 ('Leakage','2026-10-15 09:40:00','Water leakage near main valve.','Open','42101-1234567-1',1,3),
 ('Outage','2026-11-02 18:05:00','Frequent tripping in the evening.','Open','42101-3456789-3',3,1);
UPDATE Complaint SET status='In Progress', employeeId=2 WHERE ticketId=1;
UPDATE Complaint SET status='Resolved', resolutionNotes='Feeder fault repaired.' WHERE ticketId=1;
UPDATE Complaint SET status='In Progress', employeeId=4 WHERE ticketId=2;

-- Billing runs for Aug and Sep (Screen 18)
CALL sp_GenerateMonthlyBills('2026-08-01', NULL, 'admin@puums.pk', @g, @s, @f);
CALL sp_GenerateMonthlyBills('2026-09-01', NULL, 'admin@puums.pk', @g, @s, @f);
UPDATE BillingRun SET runAt = '2026-09-02 09:15:00' WHERE billingMonth = '2026-08-01';
UPDATE BillingRun SET runAt = '2026-10-02 09:15:00' WHERE billingMonth = '2026-09-01';

-- Payments (Screen 4): pay every August bill in full, one consolidated
-- payment per citizen, through the real transaction procedure.
SET @c = '42101-1234567-1';
SET @j = (SELECT JSON_ARRAYAGG(JSON_OBJECT('billId', billId, 'ver', occVersion)) FROM vw_CitizenActiveBills WHERE cnic=@c AND billingMonth='2026-08-01');
SET @a = (SELECT SUM(balanceDue) FROM vw_CitizenActiveBills WHERE cnic=@c AND billingMonth='2026-08-01');
CALL sp_ProcessPayment(@c, @j, @a, 'Card', FALSE, @p, @m);
UPDATE Payment SET paymentDate='2026-09-12 14:20:00' WHERE paymentId=@p;
UPDATE PaymentAllocation SET allocationDate='2026-09-12 14:20:00' WHERE paymentId=@p;

SET @c = '42101-2345678-2';
SET @j = (SELECT JSON_ARRAYAGG(JSON_OBJECT('billId', billId, 'ver', occVersion)) FROM vw_CitizenActiveBills WHERE cnic=@c AND billingMonth='2026-08-01');
SET @a = (SELECT SUM(balanceDue) FROM vw_CitizenActiveBills WHERE cnic=@c AND billingMonth='2026-08-01');
CALL sp_ProcessPayment(@c, @j, @a, 'JazzCash', FALSE, @p, @m);
UPDATE Payment SET paymentDate='2026-09-18 11:05:00' WHERE paymentId=@p;

SET @c = '42301-4567890-4';
SET @j = (SELECT JSON_ARRAYAGG(JSON_OBJECT('billId', billId, 'ver', occVersion)) FROM vw_CitizenActiveBills WHERE cnic=@c AND billingMonth='2026-08-01');
SET @a = (SELECT SUM(balanceDue) FROM vw_CitizenActiveBills WHERE cnic=@c AND billingMonth='2026-08-01');
CALL sp_ProcessPayment(@c, @j, @a, 'Bank Transfer', FALSE, @p, @m);
UPDATE Payment SET paymentDate='2026-09-20 16:45:00' WHERE paymentId=@p;

-- Sana pays only part of August -> Partially Paid
SET @c = '42101-3456789-3';
SET @j = (SELECT JSON_ARRAYAGG(JSON_OBJECT('billId', billId, 'ver', occVersion)) FROM vw_CitizenActiveBills WHERE cnic=@c AND billingMonth='2026-08-01');
CALL sp_ProcessPayment(@c, @j, 2000, 'EasyPaisa', FALSE, @p, @m);
UPDATE Payment SET paymentDate='2026-09-25 10:00:00' WHERE paymentId=@p;

-- Maria pays her September water bill only
SET @b = (SELECT billId FROM vw_CitizenActiveBills WHERE cnic='42101-1234567-1' AND billingMonth='2026-09-01' AND utility='Piped Water');
SET @j = (SELECT JSON_ARRAY(JSON_OBJECT('billId', billId, 'ver', occVersion)) FROM Bill WHERE billId=@b);
SET @a = (SELECT balanceDue FROM vw_BillBalance WHERE billId=@b);
CALL sp_ProcessPayment('42101-1234567-1', @j, @a, 'Card', FALSE, @p, @m);
UPDATE Payment SET paymentDate='2026-10-16 12:30:00' WHERE paymentId=@p;
