-- =====================================================================
-- 02_triggers.sql  (proposal section 2.9.3)
-- =====================================================================
USE puums;

DROP TRIGGER IF EXISTS trg_prevent_overpayment;
DROP TRIGGER IF EXISTS trg_validate_meter_reading;
DROP TRIGGER IF EXISTS trg_validate_meter_reading_upd;
DROP TRIGGER IF EXISTS trg_prevent_overlapping_tariff;
DROP TRIGGER IF EXISTS trg_prevent_overlapping_tariff_upd;
DROP TRIGGER IF EXISTS trg_tanker_status_sync;
DROP TRIGGER IF EXISTS trg_complaint_status_log;

DELIMITER $$

-- 1. Reject an allocation larger than what is still owed on the bill
CREATE TRIGGER trg_prevent_overpayment
BEFORE INSERT ON PaymentAllocation
FOR EACH ROW
BEGIN
    DECLARE v_total DECIMAL(12,2);
    DECLARE v_paid  DECIMAL(12,2);

    SELECT baseAmount + fpaAmount + gstAmount + tankerArrears
      INTO v_total
      FROM Bill WHERE billId = NEW.billId;

    SELECT COALESCE(SUM(allocatedAmount), 0)
      INTO v_paid
      FROM PaymentAllocation WHERE billId = NEW.billId;

    IF NEW.allocatedAmount > v_total - v_paid THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Overpayment: allocation exceeds remaining bill balance';
    END IF;
END$$

-- 2. Meter reading validation (INSERT): auto-fill previous reading,
--    current >= previous, one reading per connection per month
CREATE TRIGGER trg_validate_meter_reading
BEFORE INSERT ON MeterReading
FOR EACH ROW
BEGIN
    DECLARE v_prev DECIMAL(12,2);
    SET NEW.readingMonth = DATE_FORMAT(NEW.readingMonth, '%Y-%m-01');

    IF EXISTS (SELECT 1 FROM MeterReading
               WHERE connectionId = NEW.connectionId
                 AND readingMonth = NEW.readingMonth) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'A reading already exists for this connection and month';
    END IF;

    IF NEW.previousReading IS NULL THEN
        SET v_prev = (SELECT currentReading
                        FROM MeterReading
                       WHERE connectionId = NEW.connectionId
                         AND readingMonth < NEW.readingMonth
                       ORDER BY readingMonth DESC LIMIT 1);
        SET NEW.previousReading = COALESCE(v_prev, 0);
    END IF;

    IF NEW.currentReading < NEW.previousReading THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Current reading cannot be below previous reading';
    END IF;
END$$

-- 2b. Same validation on UPDATE (MySQL needs one trigger per event)
CREATE TRIGGER trg_validate_meter_reading_upd
BEFORE UPDATE ON MeterReading
FOR EACH ROW
BEGIN
    IF NEW.currentReading < NEW.previousReading THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Current reading cannot be below previous reading';
    END IF;
END$$

-- 3. One tariff version per provider + category + effective date
CREATE TRIGGER trg_prevent_overlapping_tariff
BEFORE INSERT ON Tariff
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT 1 FROM Tariff
               WHERE providerId = NEW.providerId
                 AND consumerCategory = NEW.consumerCategory
                 AND effectiveDate = NEW.effectiveDate) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'A tariff for this provider/category already starts on this date';
    END IF;
END$$

CREATE TRIGGER trg_prevent_overlapping_tariff_upd
BEFORE UPDATE ON Tariff
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT 1 FROM Tariff
               WHERE providerId = NEW.providerId
                 AND consumerCategory = NEW.consumerCategory
                 AND effectiveDate = NEW.effectiveDate
                 AND tariffId <> NEW.tariffId) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'A tariff for this provider/category already starts on this date';
    END IF;
END$$

-- 4. Keep tanker availability in sync with request status
CREATE TRIGGER trg_tanker_status_sync
AFTER UPDATE ON TankerRequest
FOR EACH ROW
BEGIN
    IF NEW.vehicleNo IS NOT NULL AND NEW.status <> OLD.status THEN
        IF NEW.status = 'Dispatched' THEN
            UPDATE Tanker SET status = 'Busy' WHERE vehicleNo = NEW.vehicleNo;
        ELSEIF NEW.status IN ('Delivered','Cancelled') THEN
            UPDATE Tanker SET status = 'Available' WHERE vehicleNo = NEW.vehicleNo;
        END IF;
    END IF;
END$$

-- 5. Audit every complaint status change
CREATE TRIGGER trg_complaint_status_log
AFTER UPDATE ON Complaint
FOR EACH ROW
BEGIN
    IF NEW.status <> OLD.status THEN
        INSERT INTO ComplaintStatusLog (ticketId, oldStatus, newStatus)
        VALUES (NEW.ticketId, OLD.status, NEW.status);
    END IF;
END$$

DELIMITER ;
