# PUUMS – Interim Demo (CS355, Group 2)

MySQL schema built from our Relation Schema Diagram + PyQt5 desktop app.
Tested on **MySQL 8.0** and MariaDB 10.11, Python 3.10+.

## 1. Setup on Windows (5 min)

```bat
pip install -r requirements.txt
```
1. Open `config.py` and put your MySQL root password in `DB_PASSWORD`.
2. Build the database (drops and recreates `puums`, then loads demo data):
   ```bat
   python setup_db.py
   ```
3. Run the app:
   ```bat
   python app\main.py
   ```
Re-run `setup_db.py` right before the demo to start from clean data.

Alternative: run `sql/01` → `05` in MySQL Workbench in order (the DELIMITER blocks work there too).

## 2. Demo logins (password `pass123` unless noted)

| Role | Username | Opens |
|---|---|---|
| Citizen | `42101-1234567-1` (Maria Khan) | Customer Portal |
| Citizen | `42101-3456789-3` (Sana Raza, partly paid) | Customer Portal |
| Employee – K-Electric meter reader | `fatima.noor@puums.pk` | Employee Portal |
| Employee – SSGC meter reader | `usman.tariq@puums.pk` | Employee Portal |
| Employee – KWSC dispatcher/water readings | `ahmad.khan@puums.pk` | Employee Portal |
| Super-Admin | `admin@puums.pk` / `admin123` | Admin Portal |

No role dropdown: the portal is chosen from `UserAccount.role`.

## 3. Implementation progress: 12 of 18 screens (67%)

| # | Screen | Status | Main SQL |
|---|---|---|---|
| 1 | Login | Done | `UserAccount` lookup with `SHA2()` |
| 2 | Citizen Registration | Done | `sp_RegisterCitizen` (3 inserts, one transaction) |
| 3 | Citizen Dashboard & Bills | Done | `vw_CitizenActiveBills` |
| 4 | **Consolidated Bill Payment (transaction screen)** | Done | `sp_ProcessPayment` (OCC, COMMIT/ROLLBACK) |
| 6 | Employee Operations Queue | Done | `vw_EmployeeTaskQueue` |
| 7 | Meter Reading Entry | Done | `INSERT MeterReading` + `trg_validate_meter_reading` |
| 9 | Operational Analytics | Done | `vw_CollectionEfficiency`, `vw_OutstandingDebt`, `vw_RegionalConsumption` |
| 10 | **Tariff Management (setup 1)** | Done | CRUD `Tariff`/`TariffSlab` in a transaction, `trg_prevent_overlapping_tariff` |
| 11 | **Provider & Region Setup (setup 2)** | Done | CRUD `Provider`, `Region` |
| 13 | My Utility Connections | Done | CRUD `ServiceConnection`, `Premise` |
| 14 | Detailed Bill Breakdown | Done | `vw_BillLineItems` |
| 16 | Transaction Ledger & Receipts | Done | `vw_PaymentLedger` |
| 18 | Monthly Billing Cycle | Done | `sp_GenerateMonthlyBills` → `sp_CalculateCascadingTariff` |
| 5, 8, 12, 15, 17 | Tanker booking, dispatch, fleet & staff, complaints, tanker rates | UI pending (final) | Tables, triggers and `sp_AssignTanker` / `sp_ProvisionEmployee` already built and used by the seed |

Backend: all 5 triggers, 5 stored procedures and 7 views from proposal §2.9 are implemented (plus `sp_RegisterCitizen`, `vw_BillBalance`).

The **"SQL executed by this screen"** panel at the bottom of every portal prints each query the app runs, with real parameter values – use it to answer "show the query behind this screen".

## 4. Suggested 20-minute demo order

1. **ERD (3 min)** – show the ERD/relation schema; point out weak entities `TariffSlab` and `BillLineItem` (composite PKs), and that totals/balances/units are derived in views (3NF).
2. **Login + Register (2 min)** – register a new citizen, then log in with the CNIC.
3. **Citizen – Maria (5 min)**
   - Dashboard → *View Bill* on Sep Electricity: Rs. 2,655 = 100×10 + 50×15 + 200 fixed + 300 FPA + 405 GST.
   - Consolidated Payment: tick Electricity + Gas →
     a) tick *Simulate network drop* → ROLLBACK, nothing changes;
     b) tick *Simulate another session…* → OCC ROLLBACK;
     c) pay normally → COMMIT, *View Receipt*.
   - Ledger shows the successful payment and the two failed (rolled-back) attempts.
4. **Employee – Usman (3 min)** – search `SG-7788-2210`; try a reading below the previous one (trigger rejects it); enter **3335** for Oct 2026 (saves; previous is auto-filled). Optionally log in as Ahmad and enter `KW-55-0912` = **965** for Oct.
5. **Admin (5 min)**
   - Monthly Billing Cycle: Oct 2026, All → generated/skipped log (connections with no reading are skipped). If you entered Maria's water reading, her Oct KWSC bill includes the Rs. 2,500 tanker delivery from 2 Oct.
   - Tariff Management: show the K-Electric revision effective 1 Oct (history preserved); try ADD on an existing date → trigger blocks it.
   - Provider & Region: try deleting K-Electric → foreign key blocks it.
   - Analytics: KPIs, heatmap, outstanding debt.
6. **SQL (2 min)** – open `sql/06_demo_queries.sql` in Workbench; Section B shows every trigger/constraint rejecting bad data.

## 5. Schema additions vs the submitted ERD (update the ERD before the final)

| Change | Why |
|---|---|
| `TankerRequest.capacityTier` (FK → TankerRate), `TankerRequest.cost` | A pending request has no tanker yet, so its size and price must be stored on the request; cost is a snapshot so later rate changes don't alter old orders |
| `Complaint.providerId` (FK → Provider) | Screen 15 records *which utility* a complaint is about |
| `ComplaintStatusLog` table | Target of `trg_complaint_status_log` (proposal §2.9.3) |
| `BillingRun` table | "Billing History" grid on Screen 18; skipped/failed counts can't be derived later |
| `BillingRun` count columns named `billsGenerated/Skipped/Failed` | `generated` is a reserved word in MySQL 8 |

Interpretation choices worth knowing if asked:
- `ServiceConnection` has `UNIQUE(premiseId, providerId)` – one account per utility per premise.
- `trg_prevent_overlapping_tariff`: the ERD has only `effectiveDate` (no end date), so a version runs until the next one starts; the trigger blocks two versions starting on the same date.
- "Update ledger balance" (proposal §2.4 step 3) has no stored column: the balance is derived from `PaymentAllocation` in `vw_BillBalance`, so it is correct the moment the transaction commits.
- Unpaid/delivered tanker charges in a month are added to that month's KWSC bill as a `Water tanker charges` line item.
- Passwords are SHA-256 via `SHA2()` (fine for a demo; a real system would use a salted hash such as bcrypt).

## 6. Files

```
config.py              MySQL connection settings
setup_db.py            builds the database (handles DELIMITER)
sql/01_schema.sql      20 tables
sql/02_triggers.sql    triggers
sql/03_views.sql       views
sql/04_procedures.sql  stored procedures
sql/05_seed.sql        Karachi pilot data (Aug & Sep billed, Oct partly read)
sql/06_demo_queries.sql queries per screen + constraint/ACID demos
app/main.py            start here
app/*_portal.py        Citizen / Employee / Admin portals
```
