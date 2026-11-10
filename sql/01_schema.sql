-- =====================================================================
-- PUUMS - Pakistan Unified Utility Management System
-- 01_schema.sql : tables (follows the Group 2 Relation Schema Diagram)
-- Target: MySQL 8.0+ (also runs on MariaDB 10.6+)
-- =====================================================================
DROP DATABASE IF EXISTS puums;
CREATE DATABASE puums CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE puums;

-- ---------------------------------------------------------------------
-- Reference / configuration entities
-- ---------------------------------------------------------------------
CREATE TABLE Region (
    regionId    INT AUTO_INCREMENT PRIMARY KEY,
    regionName  VARCHAR(60) NOT NULL,
    city        VARCHAR(40) NOT NULL,
    province    VARCHAR(40) NOT NULL,
    CONSTRAINT uq_region UNIQUE (regionName, city)
);

CREATE TABLE Provider (
    providerId    INT AUTO_INCREMENT PRIMARY KEY,
    providerName  VARCHAR(60) NOT NULL UNIQUE,
    utilityType   VARCHAR(30) NOT NULL,
    contactPhone  VARCHAR(15),
    department    VARCHAR(60),
    CONSTRAINT chk_utility CHECK (utilityType IN ('Electricity','Gas','Piped Water'))
);

CREATE TABLE UserAccount (
    accountId     INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,      -- CNIC or email
    passwordHash  VARCHAR(255) NOT NULL,             -- SHA-256 hex
    role          VARCHAR(30)  NOT NULL,
    createdAt     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lastLogin     DATETIME     NULL,
    CONSTRAINT chk_role CHECK (role IN ('Citizen','Employee','Admin','Super-Admin'))
);

CREATE TABLE Citizen (
    cnic       CHAR(15)     PRIMARY KEY,             -- 42101-1234567-1
    firstName  VARCHAR(50)  NOT NULL,
    lastName   VARCHAR(50)  NOT NULL,
    phone      VARCHAR(15),
    email      VARCHAR(100) UNIQUE,
    accountId  INT          NOT NULL UNIQUE,
    CONSTRAINT fk_citizen_account FOREIGN KEY (accountId) REFERENCES UserAccount(accountId),
    CONSTRAINT chk_cnic CHECK (cnic REGEXP '^[0-9]{5}-[0-9]{7}-[0-9]$')
);

CREATE TABLE Employee (
    employeeId  INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    phone       VARCHAR(15),
    email       VARCHAR(100) UNIQUE,
    role        VARCHAR(30)  NOT NULL,               -- Meter Reader / Dispatcher / Driver / Admin
    department  VARCHAR(60),
    accountId   INT NULL UNIQUE,                     -- drivers may have no login
    providerId  INT NULL,
    regionId    INT NULL,
    CONSTRAINT fk_emp_account  FOREIGN KEY (accountId)  REFERENCES UserAccount(accountId),
    CONSTRAINT fk_emp_provider FOREIGN KEY (providerId) REFERENCES Provider(providerId),
    CONSTRAINT fk_emp_region   FOREIGN KEY (regionId)   REFERENCES Region(regionId)
);

-- ---------------------------------------------------------------------
-- Premises and service connections (Module 1)
-- ---------------------------------------------------------------------
CREATE TABLE Premise (
    premiseId    INT AUTO_INCREMENT PRIMARY KEY,
    address      VARCHAR(150),
    houseNo      VARCHAR(20)  NOT NULL,
    street       VARCHAR(60)  NOT NULL,
    area         VARCHAR(60)  NOT NULL,
    premiseType  VARCHAR(30)  NOT NULL DEFAULT 'Residential',
    cnic         CHAR(15)     NOT NULL,
    regionId     INT          NOT NULL,
    CONSTRAINT fk_premise_citizen FOREIGN KEY (cnic)     REFERENCES Citizen(cnic),
    CONSTRAINT fk_premise_region  FOREIGN KEY (regionId) REFERENCES Region(regionId),
    CONSTRAINT chk_premise_type CHECK (premiseType IN ('Residential','Commercial'))
);

CREATE TABLE ServiceConnection (
    connectionId    INT AUTO_INCREMENT PRIMARY KEY,
    consumerNo      VARCHAR(20) NOT NULL UNIQUE,
    meterNo         VARCHAR(20) NOT NULL UNIQUE,
    connectionDate  DATE        NOT NULL,
    status          VARCHAR(30) NOT NULL DEFAULT 'Active',
    premiseId       INT         NOT NULL,
    providerId      INT         NOT NULL,
    CONSTRAINT fk_conn_premise  FOREIGN KEY (premiseId)  REFERENCES Premise(premiseId),
    CONSTRAINT fk_conn_provider FOREIGN KEY (providerId) REFERENCES Provider(providerId),
    CONSTRAINT uq_premise_provider UNIQUE (premiseId, providerId),   -- no overlapping accounts
    CONSTRAINT chk_conn_status CHECK (status IN ('Active','Inactive'))
);

-- ---------------------------------------------------------------------
-- Tariffs (Module 3 / Setup Screen 1)
-- ---------------------------------------------------------------------
CREATE TABLE Tariff (
    tariffId          INT AUTO_INCREMENT PRIMARY KEY,
    consumerCategory  VARCHAR(30)   NOT NULL,
    fixedCharges      DECIMAL(10,2) NOT NULL DEFAULT 0,
    fpaRate           DECIMAL(8,2)  NOT NULL DEFAULT 0,   -- Rs per unit
    gstPercent        DECIMAL(5,2)  NOT NULL DEFAULT 0,
    effectiveDate     DATE          NOT NULL,
    providerId        INT           NOT NULL,
    CONSTRAINT fk_tariff_provider FOREIGN KEY (providerId) REFERENCES Provider(providerId),
    CONSTRAINT chk_tariff_cat CHECK (consumerCategory IN ('Residential','Commercial')),
    CONSTRAINT chk_tariff_vals CHECK (fixedCharges >= 0 AND fpaRate >= 0 AND gstPercent BETWEEN 0 AND 100)
);

CREATE TABLE TariffSlab (                      -- weak entity of Tariff
    tariffId     INT          NOT NULL,
    slabNumber   INT          NOT NULL,
    minUnits     INT          NOT NULL,
    maxUnits     INT          NULL,             -- NULL = no upper limit
    ratePerUnit  DECIMAL(8,2) NOT NULL,
    PRIMARY KEY (tariffId, slabNumber),
    CONSTRAINT fk_slab_tariff FOREIGN KEY (tariffId) REFERENCES Tariff(tariffId) ON DELETE CASCADE,
    CONSTRAINT chk_slab CHECK (minUnits >= 0 AND (maxUnits IS NULL OR maxUnits >= minUnits) AND ratePerUnit >= 0)
);

-- ---------------------------------------------------------------------
-- Consumption (Module 2)
-- ---------------------------------------------------------------------
CREATE TABLE MeterReading (
    readingId        INT AUTO_INCREMENT PRIMARY KEY,
    readingMonth     DATE          NOT NULL,     -- always 1st of month
    readingDate      DATE          NOT NULL,
    previousReading  DECIMAL(12,2) NULL,          -- auto-filled by trigger
    currentReading   DECIMAL(12,2) NOT NULL,
    connectionId     INT           NOT NULL,
    employeeId       INT           NOT NULL,
    CONSTRAINT fk_reading_conn FOREIGN KEY (connectionId) REFERENCES ServiceConnection(connectionId),
    CONSTRAINT fk_reading_emp  FOREIGN KEY (employeeId)   REFERENCES Employee(employeeId),
    CONSTRAINT uq_one_reading_per_month UNIQUE (connectionId, readingMonth)
);

-- ---------------------------------------------------------------------
-- Billing (Module 3)
-- ---------------------------------------------------------------------
CREATE TABLE Bill (
    billId         INT AUTO_INCREMENT PRIMARY KEY,
    billingMonth   DATE          NOT NULL,
    issueDate      DATE          NOT NULL,
    dueDate        DATE          NOT NULL,
    baseAmount     DECIMAL(12,2) NOT NULL DEFAULT 0,   -- slab charges + fixed charges
    fpaAmount      DECIMAL(12,2) NOT NULL DEFAULT 0,
    gstAmount      DECIMAL(12,2) NOT NULL DEFAULT 0,
    tankerArrears  DECIMAL(12,2) NOT NULL DEFAULT 0,
    status         VARCHAR(30)   NOT NULL DEFAULT 'Unpaid',
    occVersion     INT           NOT NULL DEFAULT 0,   -- optimistic concurrency control
    connectionId   INT           NOT NULL,
    CONSTRAINT fk_bill_conn FOREIGN KEY (connectionId) REFERENCES ServiceConnection(connectionId),
    CONSTRAINT uq_bill_per_month UNIQUE (connectionId, billingMonth),
    CONSTRAINT chk_bill_status CHECK (status IN ('Unpaid','Partially Paid','Paid'))
);

CREATE TABLE BillLineItem (                     -- weak entity of Bill
    billId             INT           NOT NULL,
    itemNo             INT           NOT NULL,
    chargeDescription  VARCHAR(100)  NOT NULL,
    units              DECIMAL(12,2) NOT NULL DEFAULT 1,
    unitRate           DECIMAL(8,2)  NOT NULL,
    PRIMARY KEY (billId, itemNo),
    CONSTRAINT fk_item_bill FOREIGN KEY (billId) REFERENCES Bill(billId) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- Payments (Module 5 / Transaction screen)
-- ---------------------------------------------------------------------
CREATE TABLE Payment (
    paymentId          INT AUTO_INCREMENT PRIMARY KEY,
    paymentDate        DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amountPaid         DECIMAL(12,2) NOT NULL,
    paymentMethod      VARCHAR(30)   NOT NULL,
    transactionStatus  VARCHAR(30)   NOT NULL DEFAULT 'Successful',
    cnic               CHAR(15)      NOT NULL,
    CONSTRAINT fk_payment_citizen FOREIGN KEY (cnic) REFERENCES Citizen(cnic),
    CONSTRAINT chk_amount CHECK (amountPaid > 0),
    CONSTRAINT chk_method CHECK (paymentMethod IN ('Card','Bank Transfer','JazzCash','EasyPaisa','Cash'))
);

CREATE TABLE PaymentAllocation (
    allocationId     INT AUTO_INCREMENT PRIMARY KEY,
    paymentId        INT           NOT NULL,
    billId           INT           NOT NULL,
    allocatedAmount  DECIMAL(12,2) NOT NULL,
    allocationDate   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_alloc_payment FOREIGN KEY (paymentId) REFERENCES Payment(paymentId),
    CONSTRAINT fk_alloc_bill    FOREIGN KEY (billId)    REFERENCES Bill(billId),
    CONSTRAINT uq_alloc UNIQUE (paymentId, billId),
    CONSTRAINT chk_alloc CHECK (allocatedAmount > 0)
);

-- ---------------------------------------------------------------------
-- Tankers (Module 4)
-- ---------------------------------------------------------------------
CREATE TABLE TankerRate (
    capacityTier      INT           PRIMARY KEY,      -- litres: 1000 / 2000 / 5000
    baseFlatRate      DECIMAL(10,2) NOT NULL,
    urgencySurcharge  DECIMAL(10,2) NOT NULL DEFAULT 0,
    effectiveDate     DATE          NOT NULL
);

CREATE TABLE Tanker (
    vehicleNo              VARCHAR(15) PRIMARY KEY,
    capacityLiters         INT         NOT NULL,
    status                 VARCHAR(30) NOT NULL DEFAULT 'Available',
    lastMaintenanceDate    DATE,
    capacityTier           INT         NOT NULL,
    driverId               INT         NULL,
    CONSTRAINT fk_tanker_tier   FOREIGN KEY (capacityTier) REFERENCES TankerRate(capacityTier),
    CONSTRAINT fk_tanker_driver FOREIGN KEY (driverId)     REFERENCES Employee(employeeId),
    CONSTRAINT chk_tanker_status CHECK (status IN ('Available','Busy','Maintenance'))
);

CREATE TABLE TankerRequest (
    requestId        INT AUTO_INCREMENT PRIMARY KEY,
    deliveryDate     DATE          NOT NULL,
    urgency          VARCHAR(30)   NOT NULL DEFAULT 'Standard',
    deliveryAddress  VARCHAR(150)  NOT NULL,
    status           VARCHAR(30)   NOT NULL DEFAULT 'Pending',
    cnic             CHAR(15)      NOT NULL,
    vehicleNo        VARCHAR(15)   NULL,
    -- additions (see README "Schema additions"):
    capacityTier     INT           NOT NULL,           -- what the citizen ordered
    cost             DECIMAL(10,2) NOT NULL,           -- price snapshot at booking time
    CONSTRAINT fk_req_citizen FOREIGN KEY (cnic)         REFERENCES Citizen(cnic),
    CONSTRAINT fk_req_tanker  FOREIGN KEY (vehicleNo)    REFERENCES Tanker(vehicleNo),
    CONSTRAINT fk_req_tier    FOREIGN KEY (capacityTier) REFERENCES TankerRate(capacityTier),
    CONSTRAINT chk_req_status CHECK (status IN ('Pending','Dispatched','Delivered','Cancelled')),
    CONSTRAINT chk_urgency CHECK (urgency IN ('Standard','Urgent'))
);

-- ---------------------------------------------------------------------
-- Complaints (Module 4)
-- ---------------------------------------------------------------------
CREATE TABLE Complaint (
    ticketId         INT AUTO_INCREMENT PRIMARY KEY,
    category         VARCHAR(30) NOT NULL,
    filingDate       DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description      TEXT,
    status           VARCHAR(30) NOT NULL DEFAULT 'Open',
    resolutionNotes  TEXT,
    cnic             CHAR(15)    NOT NULL,
    premiseId        INT         NOT NULL,
    employeeId       INT         NULL,
    providerId       INT         NULL,                 -- addition: which utility
    CONSTRAINT fk_cmp_citizen  FOREIGN KEY (cnic)       REFERENCES Citizen(cnic),
    CONSTRAINT fk_cmp_premise  FOREIGN KEY (premiseId)  REFERENCES Premise(premiseId),
    CONSTRAINT fk_cmp_employee FOREIGN KEY (employeeId) REFERENCES Employee(employeeId),
    CONSTRAINT fk_cmp_provider FOREIGN KEY (providerId) REFERENCES Provider(providerId),
    CONSTRAINT chk_cmp_cat CHECK (category IN ('Outage','Billing Error','Meter Fault','Leakage')),
    CONSTRAINT chk_cmp_status CHECK (status IN ('Open','In Progress','Resolved'))
);

-- Audit table written by trg_complaint_status_log (proposal 2.9.3)
CREATE TABLE ComplaintStatusLog (
    logId      INT AUTO_INCREMENT PRIMARY KEY,
    ticketId   INT         NOT NULL,
    oldStatus  VARCHAR(30),
    newStatus  VARCHAR(30) NOT NULL,
    changedAt  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_log_ticket FOREIGN KEY (ticketId) REFERENCES Complaint(ticketId)
);

-- History of billing runs shown on Screen 18
CREATE TABLE BillingRun (
    runId         INT AUTO_INCREMENT PRIMARY KEY,
    billingMonth  DATE        NOT NULL,
    providerId    INT         NULL,                    -- NULL = all providers
    billsGenerated INT        NOT NULL DEFAULT 0,
    billsSkipped  INT         NOT NULL DEFAULT 0,
    billsFailed   INT         NOT NULL DEFAULT 0,
    runBy         VARCHAR(50),
    runAt         DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_run_provider FOREIGN KEY (providerId) REFERENCES Provider(providerId)
);

-- Helpful indexes for the screens' lookups
CREATE INDEX idx_premise_cnic   ON Premise(cnic);
CREATE INDEX idx_bill_status    ON Bill(status, dueDate);
CREATE INDEX idx_payment_cnic   ON Payment(cnic, paymentDate);
CREATE INDEX idx_tariff_lookup  ON Tariff(providerId, consumerCategory, effectiveDate);
