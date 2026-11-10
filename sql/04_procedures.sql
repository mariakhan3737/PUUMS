-- =====================================================================
-- 04_procedures.sql  (proposal section 2.9.4)
-- =====================================================================
USE puums;

DROP PROCEDURE IF EXISTS sp_CalculateCascadingTariff;
DROP PROCEDURE IF EXISTS sp_GenerateMonthlyBills;
DROP PROCEDURE IF EXISTS sp_ProcessPayment;
DROP PROCEDURE IF EXISTS sp_AssignTanker;
DROP PROCEDURE IF EXISTS sp_ProvisionEmployee;
DROP PROCEDURE IF EXISTS sp_RegisterCitizen;

DELIMITER $$

-- ---------------------------------------------------------------------
-- Cascading slab charge for N units, using the tariff version in force
-- on p_asOf for that provider + category.
--   units in slab = LEAST(units, maxUnits) - (minUnits - 1), floored at 0
-- ---------------------------------------------------------------------
CREATE PROCEDURE sp_CalculateCascadingTariff(
    IN  p_providerId INT,
    IN  p_category   VARCHAR(30),
    IN  p_asOf       DATE,
    IN  p_units      DECIMAL(12,2),
    OUT p_tariffId   INT,
    OUT p_charge     DECIMAL(12,2))
BEGIN
    SET p_tariffId = NULL;

    -- SET (subquery) form: returns NULL instead of raising NOT FOUND
    SET p_tariffId = (SELECT tariffId
                        FROM Tariff
                       WHERE providerId = p_providerId
                         AND consumerCategory = p_category
                         AND effectiveDate <= p_asOf
                       ORDER BY effectiveDate DESC
                       LIMIT 1);

    IF p_tariffId IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No tariff in force for this provider/category';
    END IF;

    SELECT COALESCE(SUM(
             GREATEST(0, LEAST(p_units, COALESCE(maxUnits, 999999999)) - GREATEST(minUnits - 1, 0))
             * ratePerUnit), 0)
      INTO p_charge
      FROM TariffSlab
     WHERE tariffId = p_tariffId;
END$$

-- ---------------------------------------------------------------------
-- Billing engine (Screen 18). p_providerId NULL = all providers.
-- Returns a log result set; OUT params carry the counts.
-- ---------------------------------------------------------------------
CREATE PROCEDURE sp_GenerateMonthlyBills(
    IN  p_month      DATE,
    IN  p_providerId INT,
    IN  p_runBy      VARCHAR(50),
    OUT p_generated  INT,
    OUT p_skipped    INT,
    OUT p_failed     INT)
BEGIN
    DECLARE v_done      INT DEFAULT 0;
    DECLARE v_conn      INT;
    DECLARE v_consumer  VARCHAR(20);
    DECLARE v_provider  INT;
    DECLARE v_utility   VARCHAR(30);
    DECLARE v_category  VARCHAR(30);
    DECLARE v_cnic      CHAR(15);

    DECLARE cur CURSOR FOR
        SELECT sc.connectionId, sc.consumerNo, sc.providerId, pr.utilityType,
               p.premiseType, p.cnic
          FROM ServiceConnection sc
          JOIN Premise  p  ON p.premiseId   = sc.premiseId
          JOIN Provider pr ON pr.providerId = sc.providerId
         WHERE sc.status = 'Active'
           AND (p_providerId IS NULL OR sc.providerId = p_providerId)
         ORDER BY sc.providerId, sc.connectionId;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    SET p_month = DATE_FORMAT(p_month, '%Y-%m-01');
    SET p_generated = 0; SET p_skipped = 0; SET p_failed = 0;

    DROP TEMPORARY TABLE IF EXISTS tmp_billing_log;
    CREATE TEMPORARY TABLE tmp_billing_log (lineNo INT AUTO_INCREMENT PRIMARY KEY, message VARCHAR(255));

    OPEN cur;
    bill_loop: LOOP
        FETCH cur INTO v_conn, v_consumer, v_provider, v_utility, v_category, v_cnic;
        IF v_done = 1 THEN LEAVE bill_loop; END IF;

        -- one inner block per connection so a failure only affects that bill
        conn_block: BEGIN
            DECLARE v_units    DECIMAL(12,2) DEFAULT NULL;
            DECLARE v_tariff   INT;
            DECLARE v_energy   DECIMAL(12,2);
            DECLARE v_fixed    DECIMAL(10,2);
            DECLARE v_fpaRate  DECIMAL(8,2);
            DECLARE v_gstPct   DECIMAL(5,2);
            DECLARE v_fpa      DECIMAL(12,2);
            DECLARE v_gst      DECIMAL(12,2);
            DECLARE v_arrears  DECIMAL(12,2) DEFAULT 0;
            DECLARE v_bill     INT;
            DECLARE v_item     INT;
            DECLARE v_err      VARCHAR(255);
            DECLARE EXIT HANDLER FOR SQLEXCEPTION
            BEGIN
                GET DIAGNOSTICS CONDITION 1 v_err = MESSAGE_TEXT;
                ROLLBACK;
                SET p_failed = p_failed + 1;
                INSERT INTO tmp_billing_log (message) VALUES (CONCAT(v_consumer, ': FAILED, ', v_err));
            END;

            IF EXISTS (SELECT 1 FROM Bill WHERE connectionId = v_conn AND billingMonth = p_month) THEN
                SET p_skipped = p_skipped + 1;
                INSERT INTO tmp_billing_log (message) VALUES (CONCAT(v_consumer, ': SKIPPED, already billed'));
                LEAVE conn_block;
            END IF;

            -- SET (subquery) form so a missing reading does not fire the cursor's NOT FOUND handler
            SET v_units = (SELECT currentReading - previousReading
                             FROM MeterReading WHERE connectionId = v_conn AND readingMonth = p_month);

            IF v_units IS NULL THEN
                SET p_skipped = p_skipped + 1;
                INSERT INTO tmp_billing_log (message) VALUES (CONCAT(v_consumer, ': SKIPPED, no reading'));
                LEAVE conn_block;
            END IF;

            START TRANSACTION;

            CALL sp_CalculateCascadingTariff(v_provider, v_category, p_month, v_units, v_tariff, v_energy);

            SELECT fixedCharges, fpaRate, gstPercent INTO v_fixed, v_fpaRate, v_gstPct
              FROM Tariff WHERE tariffId = v_tariff;

            SET v_fpa = ROUND(v_units * v_fpaRate, 2);
            SET v_gst = ROUND((v_energy + v_fixed + v_fpa) * v_gstPct / 100, 2);

            -- water tanker deliveries that month roll into the citizen's first KWSC bill
            IF v_utility = 'Piped Water' AND v_conn = (
                   SELECT MIN(sc2.connectionId)
                     FROM ServiceConnection sc2
                     JOIN Premise p2 ON p2.premiseId = sc2.premiseId
                    WHERE p2.cnic = v_cnic AND sc2.providerId = v_provider AND sc2.status = 'Active') THEN
                SELECT COALESCE(SUM(cost), 0) INTO v_arrears
                  FROM TankerRequest
                 WHERE cnic = v_cnic AND status = 'Delivered'
                   AND DATE_FORMAT(deliveryDate, '%Y-%m-01') = p_month;
            END IF;

            INSERT INTO Bill (billingMonth, issueDate, dueDate, baseAmount, fpaAmount,
                              gstAmount, tankerArrears, status, connectionId)
            VALUES (p_month,
                    LAST_DAY(p_month) + INTERVAL 1 DAY,
                    LAST_DAY(p_month) + INTERVAL 21 DAY,
                    v_energy + v_fixed, v_fpa, v_gst, v_arrears, 'Unpaid', v_conn);
            SET v_bill = LAST_INSERT_ID();

            -- one line item per slab actually used
            INSERT INTO BillLineItem (billId, itemNo, chargeDescription, units, unitRate)
            SELECT v_bill,
                   ROW_NUMBER() OVER (ORDER BY slabNumber),
                   CONCAT('Slab ', slabNumber, ' (', minUnits, '-', COALESCE(maxUnits, '+'), ')'),
                   GREATEST(0, LEAST(v_units, COALESCE(maxUnits, 999999999)) - GREATEST(minUnits - 1, 0)),
                   ratePerUnit
              FROM TariffSlab
             WHERE tariffId = v_tariff
               AND GREATEST(0, LEAST(v_units, COALESCE(maxUnits, 999999999)) - GREATEST(minUnits - 1, 0)) > 0;

            SELECT COUNT(*) INTO v_item FROM BillLineItem WHERE billId = v_bill;

            IF v_fixed > 0 THEN
                SET v_item = v_item + 1;
                INSERT INTO BillLineItem VALUES (v_bill, v_item, 'Fixed charges', 1, v_fixed);
            END IF;
            IF v_fpa > 0 THEN
                SET v_item = v_item + 1;
                INSERT INTO BillLineItem VALUES (v_bill, v_item, 'Fuel price adjustment (FPA)', v_units, v_fpaRate);
            END IF;
            IF v_gst > 0 THEN
                SET v_item = v_item + 1;
                INSERT INTO BillLineItem VALUES (v_bill, v_item, CONCAT('GST ', v_gstPct, '%'), 1, v_gst);
            END IF;
            IF v_arrears > 0 THEN
                SET v_item = v_item + 1;
                INSERT INTO BillLineItem VALUES (v_bill, v_item, 'Water tanker charges', 1, v_arrears);
            END IF;

            COMMIT;
            SET p_generated = p_generated + 1;
            INSERT INTO tmp_billing_log (message)
            VALUES (CONCAT(v_consumer, ': OK, Rs. ', FORMAT(v_energy + v_fixed + v_fpa + v_gst + v_arrears, 0)));
        END conn_block;
    END LOOP;
    CLOSE cur;

    INSERT INTO BillingRun (billingMonth, providerId, billsGenerated, billsSkipped, billsFailed, runBy)
    VALUES (p_month, p_providerId, p_generated, p_skipped, p_failed, p_runBy);

    INSERT INTO tmp_billing_log (message)
    VALUES (CONCAT('Summary: ', p_generated, ' generated, ', p_skipped, ' skipped, ', p_failed, ' failed'));

    SELECT message FROM tmp_billing_log ORDER BY lineNo;
END$$

-- ---------------------------------------------------------------------
-- TRANSACTION SCREEN (Screen 4): consolidated multi-bill payment
-- p_bills is JSON: [{"billId": 7, "ver": 0}, {"billId": 8, "ver": 1}]
-- "ver" is the occVersion the screen loaded -> optimistic concurrency.
-- ---------------------------------------------------------------------
CREATE PROCEDURE sp_ProcessPayment(
    IN  p_cnic             CHAR(15),
    IN  p_bills            JSON,
    IN  p_amount           DECIMAL(12,2),
    IN  p_method           VARCHAR(30),
    IN  p_simulateFailure  BOOLEAN,
    OUT p_paymentId        INT,
    OUT p_message          VARCHAR(255))
BEGIN
    DECLARE v_done        INT DEFAULT 0;
    DECLARE v_selected    INT;
    DECLARE v_valid       INT;
    DECLARE v_outstanding DECIMAL(12,2);
    DECLARE v_remaining   DECIMAL(12,2);
    DECLARE v_bill        INT;
    DECLARE v_ver         INT;
    DECLARE v_due         DECIMAL(12,2);
    DECLARE v_alloc       DECIMAL(12,2);
    DECLARE v_err         VARCHAR(255);

    -- oldest due date first
    DECLARE cur CURSOR FOR
        SELECT t.billId, t.ver, bb.balanceDue
          FROM tmp_selected_bills t
          JOIN vw_BillBalance bb ON bb.billId = t.billId
         ORDER BY bb.dueDate, t.billId;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 v_err = MESSAGE_TEXT;
        ROLLBACK;                                          -- undo every step
        -- record the failed attempt in the ledger (outside the rolled-back txn)
        INSERT INTO Payment (amountPaid, paymentMethod, transactionStatus, cnic)
        VALUES (GREATEST(p_amount, 0.01), p_method, 'Failed', p_cnic);
        SET p_paymentId = NULL;
        SET p_message   = CONCAT('ROLLBACK: ', v_err);
    END;

    DROP TEMPORARY TABLE IF EXISTS tmp_selected_bills;
    CREATE TEMPORARY TABLE tmp_selected_bills AS
        SELECT jt.billId, jt.ver
          FROM JSON_TABLE(p_bills, '$[*]' COLUMNS (
                   billId INT PATH '$.billId',
                   ver    INT PATH '$.ver')) AS jt;

    START TRANSACTION;

    SELECT COUNT(*) INTO v_selected FROM tmp_selected_bills;
    IF v_selected = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No bills selected';
    END IF;

    -- every selected bill must belong to this citizen, be unpaid and unchanged
    SELECT COUNT(*) INTO v_valid
      FROM tmp_selected_bills t
      JOIN Bill b               ON b.billId        = t.billId
      JOIN ServiceConnection sc ON sc.connectionId = b.connectionId
      JOIN Premise p            ON p.premiseId     = sc.premiseId
     WHERE p.cnic = p_cnic AND b.status <> 'Paid' AND b.occVersion = t.ver;
    IF v_valid <> v_selected THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'OCC check failed: a selected bill changed since it was loaded';
    END IF;

    SELECT SUM(bb.balanceDue) INTO v_outstanding
      FROM tmp_selected_bills t JOIN vw_BillBalance bb ON bb.billId = t.billId;
    IF p_amount <= 0 OR p_amount > v_outstanding THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Amount must be > 0 and cannot exceed the selected outstanding balance';
    END IF;

    -- Step 1: payment record
    INSERT INTO Payment (amountPaid, paymentMethod, transactionStatus, cnic)
    VALUES (p_amount, p_method, 'Successful', p_cnic);
    SET p_paymentId = LAST_INSERT_ID();

    -- Step 2: allocate across bills, oldest due first
    SET v_remaining = p_amount;
    OPEN cur;
    alloc_loop: LOOP
        FETCH cur INTO v_bill, v_ver, v_due;
        IF v_done = 1 OR v_remaining <= 0 THEN LEAVE alloc_loop; END IF;

        SET v_alloc = LEAST(v_remaining, v_due);
        INSERT INTO PaymentAllocation (paymentId, billId, allocatedAmount)
        VALUES (p_paymentId, v_bill, v_alloc);                 -- trg_prevent_overpayment fires

        UPDATE Bill
           SET status     = IF(v_alloc >= v_due, 'Paid', 'Partially Paid'),
               occVersion = occVersion + 1
         WHERE billId = v_bill AND occVersion = v_ver;         -- OCC write
        IF ROW_COUNT() = 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'OCC conflict while updating bill';
        END IF;

        SET v_remaining = v_remaining - v_alloc;
    END LOOP;
    CLOSE cur;

    -- Step 3: ledger balance is derived (vw_PaymentLedger / vw_BillBalance),
    -- so it is up to date as soon as the allocations commit.

    IF p_simulateFailure THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Simulated network drop before COMMIT';
    END IF;

    COMMIT;
    SET p_message = CONCAT('COMMIT: TXN-', LPAD(p_paymentId, 5, '0'), ' successful');
END$$

-- ---------------------------------------------------------------------
-- Assign an available tanker of the requested capacity (Screen 8)
-- ---------------------------------------------------------------------
CREATE PROCEDURE sp_AssignTanker(
    IN  p_requestId INT,
    IN  p_vehicleNo VARCHAR(15),
    OUT p_message   VARCHAR(255))
BEGIN
    DECLARE v_err VARCHAR(255);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 v_err = MESSAGE_TEXT;
        ROLLBACK;
        SET p_message = CONCAT('ROLLBACK: ', v_err);
    END;

    START TRANSACTION;
    IF NOT EXISTS (SELECT 1 FROM TankerRequest WHERE requestId = p_requestId AND status = 'Pending' FOR UPDATE) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Request is not pending';
    END IF;
    IF NOT EXISTS (SELECT 1
                     FROM Tanker t JOIN TankerRequest r ON r.requestId = p_requestId
                    WHERE t.vehicleNo = p_vehicleNo AND t.status = 'Available'
                      AND t.capacityTier = r.capacityTier AND t.driverId IS NOT NULL) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Tanker not available, has no driver, or wrong capacity';
    END IF;

    UPDATE TankerRequest SET vehicleNo = p_vehicleNo, status = 'Dispatched'
     WHERE requestId = p_requestId;                        -- trg_tanker_status_sync -> Busy
    COMMIT;
    SET p_message = 'Dispatched';
END$$

-- ---------------------------------------------------------------------
-- Admin creates login + employee row atomically (Screen 12)
-- ---------------------------------------------------------------------
CREATE PROCEDURE sp_ProvisionEmployee(
    IN  p_name       VARCHAR(100),
    IN  p_phone      VARCHAR(15),
    IN  p_email      VARCHAR(100),
    IN  p_role       VARCHAR(30),
    IN  p_department VARCHAR(60),
    IN  p_providerId INT,
    IN  p_regionId   INT,
    IN  p_password   VARCHAR(100),
    IN  p_accountRole VARCHAR(30),       -- 'Employee' or 'Admin'
    OUT p_employeeId INT)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
    INSERT INTO UserAccount (username, passwordHash, role)
    VALUES (p_email, SHA2(p_password, 256), p_accountRole);

    INSERT INTO Employee (name, phone, email, role, department, accountId, providerId, regionId)
    VALUES (p_name, p_phone, p_email, p_role, p_department, LAST_INSERT_ID(), p_providerId, p_regionId);
    SET p_employeeId = LAST_INSERT_ID();
    COMMIT;
END$$

-- ---------------------------------------------------------------------
-- Citizen self-registration: account + citizen + primary premise (Screen 2)
-- ---------------------------------------------------------------------
CREATE PROCEDURE sp_RegisterCitizen(
    IN p_cnic        CHAR(15),
    IN p_firstName   VARCHAR(50),
    IN p_lastName    VARCHAR(50),
    IN p_phone       VARCHAR(15),
    IN p_email       VARCHAR(100),
    IN p_password    VARCHAR(100),
    IN p_houseNo     VARCHAR(20),
    IN p_street      VARCHAR(60),
    IN p_area        VARCHAR(60),
    IN p_regionId    INT,
    IN p_premiseType VARCHAR(30))
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
    INSERT INTO UserAccount (username, passwordHash, role)
    VALUES (p_cnic, SHA2(p_password, 256), 'Citizen');          -- role is fixed: no dropdown

    INSERT INTO Citizen (cnic, firstName, lastName, phone, email, accountId)
    VALUES (p_cnic, p_firstName, p_lastName, p_phone, p_email, LAST_INSERT_ID());

    INSERT INTO Premise (address, houseNo, street, area, premiseType, cnic, regionId)
    VALUES (CONCAT('House ', p_houseNo, ', ', p_street, ', ', p_area),
            p_houseNo, p_street, p_area, p_premiseType, p_cnic, p_regionId);
    COMMIT;
END$$

DELIMITER ;
