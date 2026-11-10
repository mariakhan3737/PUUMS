# PUUMS – Systems Engineering Implementation & Gap Specification
**Pakistan Unified Utility Management System**  
*Document Type:* Systems Engineering Verification, Implementation Baseline & Gap Analysis Document  
*Course:* CS/CE 355/373 – Database Systems, Habib University (Fall 2026)  
*Authors:* Maria Khan (`mk10000`), Basil Saeed Bari (`bb09892`) – Group 2 (Section L6, Batch 2028)  
*Project Baseline:* Interim Milestone Evaluation  

---

## 1. Systems Engineering Framework & Document Purpose

This document provides a **complete, exhaustive, and mathematically traceable systems engineering specification** of the PUUMS software platform. It inventories every functional requirement, UI screen, database artifact, concurrency control mechanism, and validation gate.

Every component is evaluated under two strict classifications:
1. **IMPLEMENTED (As-Built Baseline):** Components fully operational, tested against MySQL 8.0, and interactive in the desktop application.
2. **NOT IMPLEMENTED / PLANNED FOR FINAL MILESTONE (Delta & Gap Specification):** Components whose database structures exist, but whose UI frontends, integrations, or operational workflows are scheduled for the 40% final submission.

---

## 2. Requirements Traceability Matrix (RTM)

The system adheres to the Accreditation Board for Engineering and Technology (ABET) and course project criteria requiring:
- Minimum of 5 core functional modules.
- Minimum of 1 complex ACID transaction processing screen.
- Minimum of 3 configuration setup screens.
- Strict Role-Based Access Control (RBAC) across three distinct privilege tiers.

| Req ID | Requirement Category & Description | Course Rubric Mapping | System Implementation Target | Status | Implementation Evidence |
|---|---|---|---|---|---|
| **FR-01** | **Unified Citizen Identity & Multi-Premise Management** | Module 1 | Premise registration, CNIC primary key binding, multi-premise linking. | **IMPLEMENTED** | `sp_RegisterCitizen`, `Premise`, `Citizen`, Screen 2, Screen 13. |
| **FR-02** | **Service Connection & Anti-Collision Mapping** | Module 1 | Linking premises to utilities with `UNIQUE(premiseId, providerId)`. | **IMPLEMENTED** | `ServiceConnection` table, Screen 13, Screen 7. |
| **FR-03** | **Manual Consumption Logging & Validation** | Module 2 | Monthly meter reading with historical sanity checks and monotonicity. | **IMPLEMENTED** | `MeterReading` table, `trg_validate_meter_reading`, Screen 7. |
| **FR-04** | **Cascading Tier Billing Engine** | Module 3 | Dynamic slab pricing, FPA, GST, cross-service tanker arrear rolls. | **IMPLEMENTED** | `sp_CalculateCascadingTariff`, `sp_GenerateMonthlyBills`, Screen 18. |
| **FR-05** | **ACID Consolidated Payment Settlement** | Module 5 / **Rubric #1** | Multi-bill, multi-utility payment with OCC, atomic commit/rollback. | **IMPLEMENTED** | `sp_ProcessPayment`, `PaymentAllocation`, `Bill.occVersion`, Screen 4. |
| **FR-06** | **Operational Reporting & Heatmaps** | Module 6 | Receivables, debt aging, collection efficiency %, consumption heatmap. | **IMPLEMENTED** | `vw_CollectionEfficiency`, `vw_OutstandingDebt`, `vw_RegionalConsumption`, Screen 9. |
| **FR-07** | **Regulatory Tariff Schedule Setup** | Module 3 / **Rubric #2** | CRUD for NEPRA/OGRA tiered slabs with effective-date versioning. | **IMPLEMENTED** | `Tariff`, `TariffSlab`, `trg_prevent_overlapping_tariff`, Screen 10. |
| **FR-08** | **Provider & Jurisdictional Region Setup** | Module 1 / **Rubric #2** | Administrative management of utility entities and geographic sectors. | **IMPLEMENTED** | `Provider`, `Region` tables, Screen 11. |
| **FR-09** | **Fleet & Staff Provisioning Setup** | Module 4 / **Rubric #2** | Water tanker fleet registry and employee account creation. | **PARTIALLY IMPLEMENTED** | DB Procedures & Tables Ready (`sp_ProvisionEmployee`, `Tanker`); UI Screen 12 pending. |
| **FR-10** | **On-Demand Water Tanker Booking** | Module 4 | Citizen booking with capacity-tier pricing and delivery tracking. | **PARTIALLY IMPLEMENTED** | DB Engine Ready (`TankerRequest`, `TankerRate`); UI Screen 5 pending. |
| **FR-11** | **Tanker Dispatch & Driver Logistics** | Module 4 | Vehicle assignment, pessimistic reservation locks, status sync. | **PARTIALLY IMPLEMENTED** | DB Ready (`sp_AssignTanker`, `trg_tanker_status_sync`); UI Screen 8 pending. |
| **FR-12** | **Utility Complaints & Lifecycle Auditing** | Module 4 | Ticket logging, status progression, trigger-driven audit logging. | **PARTIALLY IMPLEMENTED** | DB Ready (`Complaint`, `ComplaintStatusLog`, `trg_complaint_status_log`); UI Screen 15 pending. |
| **FR-13** | **Tanker Rate Pricing Setup** | Module 4 | Base rates and urgency surcharges per capacity tier. | **PARTIALLY IMPLEMENTED** | DB Ready (`TankerRate` table); UI Screen 17 pending. |
| **NFR-01** | **Database Normalization (3NF)** | Systems Architecture | Eliminating partial and transitive dependencies, zero stored derived metrics. | **IMPLEMENTED** | Schema decomposition, 8 dynamic SQL Views deriving balances. |
| **NFR-02** | **Role-Based Access Control (RBAC)** | Security Architecture | Zero role dropdowns, SHA-256 hashing, geographic/departmental scoping. | **IMPLEMENTED** | `UserAccount`, `login_window.py`, parameter-bound queries in portals. |
| **NFR-03** | **Real-Time SQL Execution Audit** | Pedagogical / Viva Tool | Transparent GUI logging of all executed SQL statements with parameters. | **IMPLEMENTED** | `db.py` (`on_sql`), `ui_common.py` (`SqlLogDock`), bottom dock on all portals. |
| **NFR-04** | **Zero-Dependency Portable Distribution** | Deployment / Release | Standalone Windows `.exe` packaged without dev pollution. | **IMPLEMENTED** | Isolated `packaging/` suite (`build_exe.py`, `build.bat`, `run_exe.py`). |

---

## 3. Exhaustive Screen-by-Screen Engineering Breakdown (All 18 Screens)

### Overview Summary
- **Total Screens in System Specification:** 18
- **Fully Implemented & Interactive Screens:** 12 (Screens 1, 2, 3, 4, 6, 7, 9, 10, 11, 13, 14, 16, 18) $\rightarrow$ **66.7% (Exceeds 50% Interim Goal)**
- **Screens with Complete DB Objects but Pending UI:** 5 (Screens 5, 8, 12, 15, 17) $\rightarrow$ Scheduled for Final Milestone.
- *(Note: Screen 14 is a modal dialog and Screen 18 is an admin tab, bringing total interactive view units to 13).*

---

### SCREEN 1: Login & Access Control
- **User Role:** All Roles (Citizen, Employee, Admin, Super-Admin).
- **Physical File:** `login_window.py` (Class `LoginWindow`, Page 0 of `QStackedWidget`).
- **Implementation Status:** **FULLY IMPLEMENTED (100%)**
- **UI Architecture:**
  - `QLineEdit` for `username` (CNIC or Email) with placeholder text.
  - `QLineEdit` for `password` with `EchoMode = Password` and returnPressed signal hook.
  - `QPushButton` ("LOGIN") triggering `do_login()`.
  - `QPushButton` ("Don't have an account? Register") toggling `QStackedWidget` to Page 1.
- **Backend & Database Logic:**
  - Query executed:
    ```sql
    SELECT accountId, username, role FROM UserAccount
    WHERE username = %s AND passwordHash = SHA2(%s, 256);
    ```
  - Upon credential verification: executes `UPDATE UserAccount SET lastLogin = NOW() WHERE accountId = %s`.
  - Conditional profile resolution:
    - If `role == 'Citizen'`: queries `Citizen` for `(cnic, firstName, lastName)`.
    - If `role in ('Employee', 'Admin', 'Super-Admin')`: queries `Employee` for `(employeeId, name, role, providerId, regionId)`.
  - Emits `logged_in` PyQt signal passing user dictionary to `main.py`, which instantiates the appropriate portal (`CitizenPortal`, `EmployeePortal`, or `AdminPortal`).
- **What is NOT Implemented:**
  - Multi-factor authentication (MFA / SMS OTP).
  - Account lockout after $N$ failed attempts.
  - "Forgot Password" self-service token recovery.

---

### SCREEN 2: Citizen Self-Registration
- **User Role:** Unauthenticated Public / New Citizen.
- **Physical File:** `login_window.py` (Class `LoginWindow`, Page 1 of `QStackedWidget`).
- **Implementation Status:** **FULLY IMPLEMENTED (100%)**
- **UI Architecture:**
  - Personal Details Group: First Name, Last Name, CNIC (with strict input mask `99999-9999999-9;_`), Phone, Email, Password.
  - Primary Address Group: House No, Street, Area, Region (`QComboBox` populated dynamically from `Region`), Premise Type (`QComboBox`: Residential / Commercial).
  - Navigation: "Create Account" (`QPushButton`) and "Back To Login" (`QPushButton`).
- **Backend & Database Logic:**
  - Input validation: verifies non-empty name, CNIC, password, address, and valid region.
  - Calls atomic stored procedure:
    ```sql
    CALL sp_RegisterCitizen(p_cnic, p_firstName, p_lastName, p_phone, p_email,
                            p_password, p_houseNo, p_street, p_area, p_regionId, p_premiseType);
    ```
  - Procedure executes an atomic transaction inserting into `UserAccount` (`role = 'Citizen'`), `Citizen`, and `Premise` in sequence.
- **What is NOT Implemented:**
  - NADRA CNIC online verification API integration.
  - Document/utility bill upload for identity proof.

---

### SCREEN 3: Citizen Dashboard & Bills
- **User Role:** Citizen.
- **Physical File:** `citizen_portal.py` (Class `DashboardTab`).
- **Implementation Status:** **FULLY IMPLEMENTED (100%)**
- **UI Architecture:**
  - Header Banner: Displays citizen full name, CNIC, phone, and email.
  - Registered Premises Table (`QTableWidget`): Displays Address, Premise Type, Region, and count of Active Service Connections.
  - Dynamic Bills Grid (`QTableWidget`): Displays Bill #, Utility Type, Provider, Month, Total Amount (Rs.), Balance Due (Rs.), Due Date, Status.
  - Action Controls: "View Bill" button (opens Screen 14) and "Pay Bill" button (navigates directly to Screen 4 preselecting the bill). Double-click on row opens Screen 14.
- **Backend & Database Logic:**
  - Premises query:
    ```sql
    SELECT p.address, p.premiseType, r.regionName, COUNT(sc.connectionId) AS activeConnections
    FROM Premise p JOIN Region r ON r.regionId = p.regionId
    LEFT JOIN ServiceConnection sc ON sc.premiseId = p.premiseId AND sc.status = 'Active'
    WHERE p.cnic = %s GROUP BY p.premiseId, p.address, p.premiseType, r.regionName;
    ```
  - Bills query:
    ```sql
    SELECT billId, utility, provider, DATE_FORMAT(billingMonth, '%b %Y'),
           totalAmount, balanceDue, dueDate, status
    FROM vw_CitizenActiveBills WHERE cnic = %s ORDER BY billingMonth DESC, utility;
    ```
- **What is NOT Implemented:**
  - Historical consumption trend chart (QtChart line graph).
  - Inactive / past disconnected premise archive view.

---

### SCREEN 4: Consolidated Bill Payment (Transaction Screen – Rubric #1)
- **User Role:** Citizen.
- **Physical File:** `citizen_portal.py` (Class `PaymentTab`).
- **Implementation Status:** **FULLY IMPLEMENTED (100%)**
- **UI Architecture:**
  - Selectable Bills Table (`QTableWidget`): Checkboxes on every unpaid bill row allowing multi-selection across different utilities.
  - Dynamic Calculation Row: Displays live "Selected outstanding: Rs. X" dynamically recalculated as checkboxes are toggled.
  - Amount Control (`QDoubleSpinBox`): Defaults to total selected outstanding balance; automatically capped to selected balance.
  - Payment Method (`QComboBox`): Options include Card, Bank Transfer, JazzCash, EasyPaisa, Cash.
  - Failure Simulation Box (`QGroupBox` with two `QCheckBox`es):
    - *Simulate network drop before COMMIT* (triggers rollback after all steps).
    - *Simulate another session editing a bill* (forces OCC version mismatch).
  - Execution Control: "Process Payment" button and "View Receipt" button (enabled on commit).
- **Backend & Database Logic:**
  - Packs selected bills into a JSON array: `[{"billId": 10, "ver": 0}, {"billId": 14, "ver": 0}]`.
  - Calls transaction procedure:
    ```sql
    CALL sp_ProcessPayment(p_cnic, p_bills_json, p_amount, p_method, p_simDrop, @pid, @msg);
    ```
  - Procedure validates bills via `JSON_TABLE()`, executes OCC version checks, inserts into `Payment`, allocates payment oldest-due-date first into `PaymentAllocation`, updates `Bill.status` and increments `Bill.occVersion`, with atomic `COMMIT` or `ROLLBACK`.
- **What is NOT Implemented:**
  - Actual external payment gateway API webhooks (Stripe / 1Link / PayFast).
  - Partial payment split controls per bill (system currently uses standard oldest-due allocation).

---

### SCREEN 5: On-Demand Water Tanker Booking
- **User Role:** Citizen.
- **Physical File:** `citizen_portal.py` (Tab 5 - Currently instantiated as `PlaceholderTab(5, "Tanker Booking", ...)`).
- **Implementation Status:** **PENDING FINAL MILESTONE (Backend 100% Implemented, UI 0%)**
- **What IS Implemented in Database:**
  - `TankerRate` table containing pricing tiers (1,000L = Rs. 1,500; 2,000L = Rs. 2,500; 5,000L = Rs. 5,500; plus urgency surcharges).
  - `TankerRequest` table with fields `(requestId, deliveryDate, urgency, deliveryAddress, status, cnic, vehicleNo, capacityTier, cost)`.
  - Price snapshotting logic: `cost` is recorded at order creation time.
  - Monthly billing integration: `sp_GenerateMonthlyBills` automatically queries delivered requests from `TankerRequest` and rolls them into KWSC piped water bills.
- **What is NOT Implemented (Engineering Gap for Final Milestone):**
  - UI Dialog / Tab with:
    - Capacity tier selection (`QComboBox`: 1000L, 2000L, 5000L) with live price update.
    - Delivery Date picker (`QDateEdit`).
    - Urgency selector (`QRadioButton`: Standard / Urgent).
    - Delivery Address field (`QLineEdit` pre-filled with citizen's primary premise).
    - "Book Tanker" button executing `INSERT INTO TankerRequest`.
    - Active Requests tracking grid showing status (`Pending`, `Dispatched`, `Delivered`).

---

### SCREEN 6: Employee Operations Queue
- **User Role:** Employee / Power User (Meter Reader, Dispatcher, Driver).
- **Physical File:** `employee_portal.py` (Class `TaskQueueTab`).
- **Implementation Status:** **FULLY IMPLEMENTED (100%)**
- **UI Architecture:**
  - Subheader displaying employee name, designation, assigned provider, and assigned region.
  - KPI Summary Cards (`kpi_card`):
    - Open / in-progress complaints count.
    - Pending tanker requests count.
    - Tankers dispatched count.
  - Operations Task Grid (`QTableWidget`): Columns for ID, Customer Name, Request Type, Premise/Area, Status, Task Date.
- **Backend & Database Logic:**
  - Scoped strictly by employee region and provider:
    ```sql
    SELECT taskRef, customer, taskType, area, status, taskDate
    FROM vw_EmployeeTaskQueue
    WHERE regionId = %s AND providerId = %s ORDER BY taskDate;
    ```
- **What is NOT Implemented:**
  - Inline action buttons directly on the grid to change status without switching screens.
  - Priority flag filtering (High / Normal / Urgent).

---

### SCREEN 7: Manual Meter Reading Entry
- **User Role:** Employee (Meter Reader).
- **Physical File:** `employee_portal.py` (Class `MeterReadingTab`).
- **Implementation Status:** **FULLY IMPLEMENTED (100%)**
- **UI Architecture:**
  - Search Header: `QLineEdit` accepting Consumer Number or Meter Number with "Search" button.
  - Connection Details Box (`QGroupBox`): Displays Customer, Provider, Meter #, Premise Address, and Last Reading.
  - Entry Form (`QFormLayout`):
    - Reading Month picker (`QDateEdit` formatted as `MMM yyyy`, defaulting to subsequent unread month).
    - Current Reading spinner (`QDoubleSpinBox` up to 99,999,999.00).
    - "Save Reading" button (`QPushButton`).
  - Historical Readings Table (`QTableWidget`): Displays Month, Entry Date, Previous Reading, Current Reading, Units Consumed, Entered By.
- **Backend & Database Logic:**
  - Lookup query:
    ```sql
    SELECT sc.connectionId, CONCAT(c.firstName, ' ', c.lastName), pr.providerName,
           sc.consumerNo, sc.meterNo, p.address,
           (SELECT currentReading FROM MeterReading m WHERE m.connectionId = sc.connectionId ORDER BY readingMonth DESC LIMIT 1),
           (SELECT readingMonth FROM MeterReading m WHERE m.connectionId = sc.connectionId ORDER BY readingMonth DESC LIMIT 1)
    FROM ServiceConnection sc JOIN Provider pr ON pr.providerId = sc.providerId
    JOIN Premise p ON p.premiseId = sc.premiseId JOIN Citizen c ON c.cnic = p.cnic
    WHERE (sc.consumerNo = %s OR sc.meterNo = %s)
      AND sc.providerId = %s AND p.regionId = %s AND sc.status = 'Active';
    ```
  - Insertion query:
    ```sql
    INSERT INTO MeterReading (readingMonth, readingDate, currentReading, connectionId, employeeId)
    VALUES (%s, CURDATE(), %s, %s, %s);
    ```
  - Database enforcement: `trg_validate_meter_reading` fires automatically, verifying non-backward readings and auto-filling `previousReading`.
- **What is NOT Implemented:**
  - Image attachment of physical meter dial for optical OCR proof.
  - Batch CSV / bulk meter reading import.

---

### SCREEN 8: Request & Dispatch Update
- **User Role:** Employee / Dispatcher.
- **Physical File:** `employee_portal.py` (Tab 3 - Currently instantiated as `PlaceholderTab(8, "Request & Dispatch Update", ...)`).
- **Implementation Status:** **PENDING FINAL MILESTONE (Backend 100% Implemented, UI 0%)**
- **What IS Implemented in Database:**
  - Stored procedure `sp_AssignTanker(p_requestId, p_vehicleNo, @msg)` with pessimistic locking (`FOR UPDATE`), availability verification, capacity tier check, and transaction rollback.
  - Trigger `trg_tanker_status_sync` synchronizing `Tanker.status = 'Busy'` upon dispatch and `'Available'` upon delivery.
  - Trigger `trg_complaint_status_log` logging every complaint transition.
- **What is NOT Implemented (Engineering Gap for Final Milestone):**
  - UI Tab featuring:
    - Splitter layout: Top half for Tanker Dispatch, Bottom half for Complaint Resolution.
    - Tanker Dispatch controls: Pending request selector, vehicle/driver combo box filtered by matching capacity tier and `status = 'Available'`, and "Dispatch Tanker" button calling `sp_AssignTanker`.
    - Complaint Resolution controls: Open complaints selector, resolution notes `QPlainTextEdit`, and status dropdown (`In Progress` / `Resolved`).

---

### SCREEN 9: Operational Analytics Dashboard
- **User Role:** Admin / Super-Admin.
- **Physical File:** `admin_portal.py` (Class `AnalyticsTab`).
- **Implementation Status:** **FULLY IMPLEMENTED (100%)**
- **UI Architecture:**
  - Billing Month selector (`QDateEdit`).
  - Four Core KPI Metric Cards (`kpi_card`):
    - Total Amount Billed (Rs.).
    - Total Revenue Collected (Rs.).
    - Collection Efficiency Percentage (%).
    - Total Outstanding Receivables (Rs. across all months).
  - Vertical Splitter containing:
    - **Regional Consumption Heatmap (`QTableWidget`):** Rows for all 7 regions; columns for Electricity, Gas, Piped Water units consumed; cells programmatically colored with variable alpha intensity based on consumption magnitude.
    - **Outstanding Debt by Provider & Region (`QTableWidget`):** Columns for Provider, Region, Unpaid Bills count, Total Outstanding (Rs.), and Oldest Due Date.
- **Backend & Database Logic:**
  - KPI metrics queried from `vw_CollectionEfficiency` and `vw_OutstandingDebt`.
  - Heatmap queried from `vw_RegionalConsumption`.
- **What is NOT Implemented:**
  - Interactive drill-down from heatmap cells to individual premise lists.
  - CSV / Excel export button for executive reports.

---

### SCREEN 10: Regulatory Tariff Management (Setup Screen 1 – Rubric #2)
- **User Role:** Admin.
- **Physical File:** `admin_portal.py` (Class `TariffTab`).
- **Implementation Status:** **FULLY IMPLEMENTED (100%)**
- **UI Architecture:**
  - Master-Detail Horizontal Splitter:
    - *Left Panel:* Provider filter dropdown and full master table of all configured tariffs with their effective dates and slab numbers.
    - *Right Panel:* Editable detail form containing Provider dropdown, Category (Residential/Commercial), Effective Date picker, Fixed Charges (Rs.), FPA Rate (Rs./unit), and GST Percentage (%).
    - *Dynamic Slabs Editor Table:* Allows adding (`+ slab`) or removing (`- slab`) rows specifying `Min units`, `Max units`, and `Rate (Rs./unit)`.
  - CRUD Command Buttons: `ADD`, `UPDATE`, `DELETE`, `Clear`.
- **Backend & Database Logic:**
  - Operations execute inside atomic database transactions (`Database.transaction()`):
    ```sql
    INSERT INTO Tariff (...) VALUES (...);
    INSERT INTO TariffSlab (tariffId, slabNumber, minUnits, maxUnits, ratePerUnit) VALUES (...);
    ```
  - Database enforcement: `trg_prevent_overlapping_tariff` prevents conflicting tariffs starting on the same date. Cascade deletion (`ON DELETE CASCADE`) ensures clean cleanup of slabs.
- **What is NOT Implemented:**
  - Visual graphical preview of the tariff stair-step curve.

---

### SCREEN 11: Utility Provider & Region Setup (Setup Screen 2 – Rubric #2)
- **User Role:** Admin.
- **Physical File:** `admin_portal.py` (Class `ProviderRegionTab`).
- **Implementation Status:** **FULLY IMPLEMENTED (100%)**
- **UI Architecture:**
  - Dual Group Layout:
    - *Utility Providers Group:* Form fields for Provider Name, Utility Type (`QComboBox`: Electricity, Gas, Piped Water), Contact Phone, and Department. CRUD buttons (`ADD`, `UPDATE`, `DELETE`) and live table showing ID, Provider, Utility, Contact, Department, and Active Connections count.
    - *Operating Regions Group:* Form fields for Region Name, City, Province. CRUD buttons (`ADD`, `UPDATE`, `DELETE`) and live table showing ID, Region, City, Province, and Associated Premises count.
- **Backend & Database Logic:**
  - Executes direct parameterized SQL queries (`INSERT`, `UPDATE`, `DELETE`).
  - Referential Integrity Demonstration: Attempting to delete a provider with active connections or tariffs triggers an explicit foreign key constraint rejection, captured and reported via `DBError`.
- **What is NOT Implemented:**
  - Geographic boundary polygon / GIS coordinate mapping for regions.

---

### SCREEN 12: Fleet & Staff Configuration (Setup Screen 3 – Rubric #2)
- **User Role:** Admin.
- **Physical File:** `admin_portal.py` (Tab 4 - Currently instantiated as `PlaceholderTab(12, "Fleet & Staff Configuration", ...)`).
- **Implementation Status:** **PENDING FINAL MILESTONE (Backend 100% Implemented, UI 0%)**
- **What IS Implemented in Database:**
  - `sp_ProvisionEmployee` stored procedure creating `UserAccount` and `Employee` in one atomic transaction with `SHA2(password, 256)`.
  - `Tanker` table with fields `(vehicleNo, capacityLiters, status, lastMaintenanceDate, capacityTier, driverId)`.
  - Foreign keys linking tankers to capacity tiers and drivers.
- **What is NOT Implemented (Engineering Gap for Final Milestone):**
  - UI Tab featuring:
    - *Fleet Management Section:* Input fields for Vehicle No (Plate), Capacity Liters, Capacity Tier dropdown, Driver assignment dropdown, and Maintenance Date picker. CRUD table for tankers.
    - *Staff Provisioning Section:* Input fields for Employee Name, Phone, Email, Role dropdown (Meter Reader, Dispatcher, Driver, Admin), Department, Assigned Provider, Assigned Region, and Password. "Provision Staff" button invoking `sp_ProvisionEmployee`.

---

### SCREEN 13: My Utility Connections
- **User Role:** Citizen.
- **Physical File:** `citizen_portal.py` (Class `ConnectionsTab`).
- **Implementation Status:** **FULLY IMPLEMENTED (100%)**
- **UI Architecture:**
  - Top Action Bar: "Add Premise" button and "Add Connection" button.
  - Connections Table (`QTableWidget`): Displays ID, Provider Name, Utility Type, Consumer No, Meter No, Premise Area, Connection Status, and Connection Date.
  - Bottom Action Bar: "Deactivate" and "Reactivate" buttons.
  - Modals:
    - `Add Premise Dialog`: Input fields for House No, Street, Area, Region dropdown, Premise Type dropdown.
    - `Add Connection Dialog`: Premise dropdown, Provider dropdown, Consumer / Account No input, Meter No input.
- **Backend & Database Logic:**
  - Database enforcement: `UNIQUE(premiseId, providerId)` prevents duplicate connections for the same utility at a single premise.
  - Direct execution of `INSERT INTO Premise` and `INSERT INTO ServiceConnection`.
- **What is NOT Implemented:**
  - Disconnection / re-metering fee calculation.
  - Digital ownership deed document attachment.

---

### SCREEN 14: Detailed Bill Breakdown Dialog
- **User Role:** Citizen.
- **Physical File:** `citizen_portal.py` (Class `BillBreakdownDialog`, opened from Screen 3).
- **Implementation Status:** **FULLY IMPLEMENTED (100%)**
- **UI Architecture:**
  - Bill Header Box: Bill Reference #, Provider & Utility Type, Consumer #, Meter #, Billing Month, Due Date, Previous Reading, Current Reading, Units Consumed, Status.
  - Itemized Line Items Table (`QTableWidget`): #, Charge Description, Units Billed, Rate (Rs.), Amount (Rs.).
  - Summary Footer: Total Bill (Rs.), Amount Paid (Rs.), and Outstanding Balance Due (Rs.).
  - Action Controls: "Pay This Bill" button (transfers context to Screen 4) and "Close" button.
- **Backend & Database Logic:**
  - Queries `vw_BillLineItems` and `vw_BillBalance` using `billId`.
  - Displays dynamic breakdown of individual slabs, fixed charges, FPA, GST, and rolled-over tanker arrears.
- **What is NOT Implemented:**
  - Direct PDF export / invoice print generation (e.g. via `reportlab` or Qt print engine).

---

### SCREEN 15: Helpdesk & Customer Complaints
- **User Role:** Citizen.
- **Physical File:** `citizen_portal.py` (Tab 6 - Currently instantiated as `PlaceholderTab(15, "Helpdesk & Complaints", ...)`).
- **Implementation Status:** **PENDING FINAL MILESTONE (Backend 100% Implemented, UI 0%)**
- **What IS Implemented in Database:**
  - `Complaint` table storing tickets with `(ticketId, category, filingDate, description, status, resolutionNotes, cnic, premiseId, employeeId, providerId)`.
  - `ComplaintStatusLog` table capturing full state transitions.
  - `trg_complaint_status_log` audit trigger firing on every update.
  - Check constraints restricting `category IN ('Outage','Billing Error','Meter Fault','Leakage')` and `status IN ('Open','In Progress','Resolved')`.
- **What is NOT Implemented (Engineering Gap for Final Milestone):**
  - UI Tab featuring:
    - "Lodge New Complaint" Form: Premise dropdown, Utility dropdown, Category selector (`QComboBox`), Description text box (`QPlainTextEdit`), and "Submit Complaint" button.
    - "My Complaints History" Table: Columns for Ticket #, Date, Utility, Category, Status, Resolution Notes.

---

### SCREEN 16: Transaction Ledger & Receipts
- **User Role:** Citizen.
- **Physical File:** `citizen_portal.py` (Class `LedgerTab`).
- **Implementation Status:** **FULLY IMPLEMENTED (100%)**
- **UI Architecture:**
  - Filter Bar: Date From (`QDateEdit`), Date To (`QDateEdit`), Status selector (`QComboBox`: All, Successful, Failed).
  - Summary KPI Ribbon: Displays "Paid in selected period: Rs. X" and "Current total outstanding debt: Rs. Y".
  - Transactions Ledger Table (`QTableWidget`): Columns for Transaction Reference (`TXN-0000X`), Payment Date, Amount Paid (Rs.), Payment Method, Allocated Bills summary, Status. Double-click opens receipt modal.
  - "View Receipt" button opening `ReceiptDialog` displaying itemized allocations.
- **Backend & Database Logic:**
  - Queries `vw_PaymentLedger` filtered by `cnic`, date bounds, and status.
  - `ReceiptDialog` queries `PaymentAllocation` joined with `Bill` to prove payment distribution.
- **What is NOT Implemented:**
  - Formal bank transaction reconciliation statement export.

---

### SCREEN 17: Tanker Rate Configuration
- **User Role:** Admin.
- **Physical File:** `admin_portal.py` (Tab 5 - Currently instantiated as `PlaceholderTab(17, "Tanker Rate Configuration", ...)`).
- **Implementation Status:** **PENDING FINAL MILESTONE (Backend 100% Implemented, UI 0%)**
- **What IS Implemented in Database:**
  - `TankerRate` table with columns `(capacityTier, baseFlatRate, urgencySurcharge, effectiveDate)`.
  - Pre-seeded tiers (1000L, 2000L, 5000L).
- **What is NOT Implemented (Engineering Gap for Final Milestone):**
  - UI Tab featuring:
    - Tier selection dropdown (1000L, 2000L, 5000L).
    - Base Flat Rate input spinner (`QDoubleSpinBox`).
    - Urgency Surcharge input spinner (`QDoubleSpinBox`).
    - Effective Date picker (`QDateEdit`).
    - "Update Logistics Pricing" button executing `UPDATE TankerRate`.
    - Live table showing current pricing schedule.

---

### SCREEN 18: Monthly Billing Cycle Execution
- **User Role:** Admin.
- **Physical File:** `admin_portal.py` (Class `BillingTab`).
- **Implementation Status:** **FULLY IMPLEMENTED (100%)**
- **UI Architecture:**
  - Control Bar: Month picker (`QDateEdit` formatted `MMM yyyy`), Provider selector (`QComboBox` with "All providers" option), and "Execute Billing Procedure" button (`QPushButton`).
  - Real-Time Progress Bar (`QProgressBar`).
  - Live Execution Log Window (`QPlainTextEdit`): Prints connection-by-connection processing results (e.g., `KE-0412345: OK, Rs. 2,655`, `SG-7788-2210: SKIPPED, already billed`, `Summary: 2 generated, 1 skipped, 0 failed`).
  - Historical Billing Runs Grid (`QTableWidget`): Displays Month, Provider, Bills Generated, Bills Skipped, Bills Failed, Run By, Run At timestamp.
- **Backend & Database Logic:**
  - Calls stored procedure:
    ```sql
    CALL sp_GenerateMonthlyBills(p_month, p_providerId, p_runBy, @g, @s, @f);
    ```
  - Traverses active connections via cursor, calculates cascading tariffs, rolls over unpaid delivered water tanker fees, writes `Bill` and `BillLineItem` rows, and persists execution history in `BillingRun`.
- **What is NOT Implemented:**
  - Multi-threaded / asynchronous background worker thread (GUI briefly freezes during thousands of bill calculations; fine for demo, but needs `QThread` for 10,000+ accounts).

---

## 4. Comprehensive Systems Delta & Gap Matrix

| Architectural Layer | Component / Feature | As-Built Implementation (Current Baseline) | Gap / What is NOT Yet Implemented | Planned Resolution Phase |
|---|---|---|---|---|
| **User Interface (UI)** | **Screen 5 (Tanker Booking)** | Active placeholder tab documenting DB backend objects. | Complete booking dialog, capacity dropdown, cost estimator, live tracking table. | Final Milestone |
| **User Interface (UI)** | **Screen 8 (Dispatch Update)** | Active placeholder tab documenting DB backend objects. | Splitter view with tanker assignment combo box and complaint status resolution editor. | Final Milestone |
| **User Interface (UI)** | **Screen 12 (Fleet & Staff)** | Active placeholder tab documenting DB backend objects. | Tanker asset registration form and employee provisioning UI invoking `sp_ProvisionEmployee`. | Final Milestone |
| **User Interface (UI)** | **Screen 15 (Complaints)** | Active placeholder tab documenting DB backend objects. | Citizen ticket lodging form and my complaints tracking table. | Final Milestone |
| **User Interface (UI)** | **Screen 17 (Tanker Rates)** | Active placeholder tab documenting DB backend objects. | Form editor for updating `baseFlatRate` and `urgencySurcharge` in `TankerRate`. | Final Milestone |
| **Database Schema** | **ERD Graphical Diagram** | Initial submitted ERD covers core schema entities. | Graphical diagram lacks the 5 additions (`ComplaintStatusLog`, `BillingRun`, `capacityTier`, `cost`, `providerId`). | Final Milestone (Update PDF) |
| **Database Security** | **Password Hashing** | Unsalted SHA-256 via MySQL native `SHA2(password, 256)`. | Salted cryptographic hashing (e.g., `bcrypt` or `argon2`) with per-user salt. | Final Milestone (Production Hardening) |
| **Reporting / Export** | **Document Generation** | Itemized on-screen breakdown via `BillBreakdownDialog`. | Export to formatted printable PDF receipt / invoice via Python `reportlab` or Qt print engine. | Final Milestone |
| **Performance** | **Batch Billing Execution** | Synchronous execution on main UI thread via `sp_GenerateMonthlyBills`. | Decoupled background task queue (`QThread` / worker thread) with asynchronous event emitter. | Final Milestone |
| **Distribution** | **Standalone Windows Exe** | Isolated builder in `packaging/` (`build_exe.py`, `build.bat`, dynamic `config.py` loading). | Fully implemented and verified. | Baseline Complete |

---

## 5. Architectural Verification: Concurrency, Integrity & Constraints

### 5.1 Concurrency Verification Matrix (Screen 4 OCC Check)
The system prevents lost updates and double-settlements through Optimistic Concurrency Control:

| Concurrency Scenario | Test Input / Action | Database Mechanism | Expected System Response | Verification Status |
|---|---|---|---|---|
| **Normal Payment** | Citizen pays Rs. 3,911.58 on bills 10 & 14 (`ver = 0`). | `sp_ProcessPayment` increments `occVersion = 1`, inserts allocations. | Transaction commits, receipt `TXN-0000X` generated, bills marked `'Paid'`. | **VERIFIED & OPERATIONAL** |
| **Simulated Network Drop** | Citizen ticks "Simulate network drop before COMMIT". | Procedure triggers conditional `SIGNAL SQLSTATE '45000'`. | Entire transaction rolls back. Ledger logs a `'Failed'` attempt. Bill balances unchanged. | **VERIFIED & OPERATIONAL** |
| **Concurrent Mutation (Stale Version)** | Citizen ticks "Simulate another session editing a bill". | GUI deliberately increments `Bill.occVersion = occVersion + 1` prior to call. | Procedure detects `v_valid <> v_selected`. Throws `"OCC check failed: a selected bill changed"`. Immediate rollback. | **VERIFIED & OPERATIONAL** |
| **Overpayment Attempt** | User attempts to allocate more than the bill balance. | `trg_prevent_overpayment` fires on `BEFORE INSERT ON PaymentAllocation`. | Trigger raises SQLSTATE '45000' (`"Overpayment: allocation exceeds remaining bill balance"`). | **VERIFIED & OPERATIONAL** |

### 5.2 Negative Constraint Validation Matrix
The system protects domain invariants through strict MySQL engine rejection:

| Invariant Tested | Offending SQL Operation | Constraining Object | Engine Response | Verification Status |
|---|---|---|---|---|
| **Meter Reading Monotonicity** | Enter reading $3,100$ when previous reading was $3,185$. | `trg_validate_meter_reading` | Rejected: `"Current reading cannot be below previous reading"`. | **VERIFIED & OPERATIONAL** |
| **Duplicate Monthly Reading** | Enter two readings for same meter in same calendar month. | `trg_validate_meter_reading` + `uq_one_reading_per_month` | Rejected: `"A reading already exists for this connection and month"`. | **VERIFIED & OPERATIONAL** |
| **Conflicting Tariff Dates** | Insert tariff for same provider and category starting on same date. | `trg_prevent_overlapping_tariff` | Rejected: `"A tariff for this provider/category already starts on this date"`. | **VERIFIED & OPERATIONAL** |
| **Malformed CNIC Format** | Insert Citizen with CNIC `'123-ABC'`. | `chk_cnic` CHECK constraint | Rejected: Regex check fails (`'^[0-9]{5}-[0-9]{7}-[0-9]$'`). | **VERIFIED & OPERATIONAL** |
| **Cascade Integrity on Provider** | Attempt to delete `K-Electric` while connections exist. | `fk_conn_provider` Foreign Key | Rejected: Cannot delete or update parent row (foreign key constraint fails). | **VERIFIED & OPERATIONAL** |
| **Overlapping Utility Accounts** | Create 2nd electricity connection for same premise. | `uq_premise_provider` Unique constraint | Rejected: Duplicate entry for key `'uq_premise_provider'`. | **VERIFIED & OPERATIONAL** |

---

## 6. Systems Engineering Sign-Off & Viva Readiness Summary

1. **Compliance with Course Mandate:**
   - 12 of 18 screens functional (**66.7% vs 50% interim threshold**).
   - Core transaction processing screen (Screen 4) fully functional with OCC and rollback demonstrations.
   - 2 of 3 setup screens (Tariff, Provider/Region) fully functional; 3rd setup screen (Fleet/Staff) has backend database procedures and tables built.
2. **Database Engine Purity:**
   - All business logic, constraints, audit logging, and calculations reside inside MySQL 8.0 DDL, triggers, and procedures.
   - The desktop GUI acts as an educational and operational presentation layer equipped with a live SQL execution logger.
3. **Distribution Readiness:**
   - Pure Python execution remains the standard development and demonstration method.
   - The standalone executable build step (`packaging/`) provides isolated, portable deployment whenever distribution to non-Python environments is required.
