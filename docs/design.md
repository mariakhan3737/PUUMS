# PUUMS – Comprehensive UI/UX Design & Layout Specification
**Pakistan Unified Utility Management System**  
*Document Type:* UI/UX Design System, Screen Architecture & Recreation Manual  
*Course:* CS/CE 355/373 – Database Systems, Habib University  
*Authors:* Maria Khan (`mk10000`), Basil Saeed Bari (`bb09892`) – Group 2 (Section L6, Batch 2028)  

---

## 1. Executive Design Philosophy & Design System

The PUUMS user interface is engineered as an enterprise-grade utility management desktop client. It merges modern flat UI aesthetics with strict database operational visibility. The interface is built programmatically using Python and PyQt5, reproducing and refining the original Qt Designer (`.ui`) wireframes.

---

### 1.1 Global Color Palette & Semantics

| Palette Token | Hex Code | Visual Swatch | Semantic Usage & Placement |
|---|---|---|---|
| **Primary Brand** | `#4a2a6b` | Deep Royal Eggplant / Purple | Active tab labels, window titles, primary action buttons, KPI values, table header accents. |
| **Primary Hover** | `#5d3a85` | Medium Violet Purple | Hover state on all primary action buttons (`QPushButton:hover`). |
| **Primary Disabled** | `#b8adc6` | Muted Lavender Gray | Inactive / disabled buttons (`QPushButton:disabled`). |
| **Selection Highlight** | `#e7dcf3` | Soft Pastel Lavender | Selected row in tables (`QTableWidget` selection background). |
| **Window Background** | `#f5f6f8` | Off-White / Crisp Light Gray | Canvas background for `QMainWindow`, `QDialog`, and main viewports. |
| **Card / Surface** | `#ffffff` | Pure White | Background for content cards, data tables, group boxes, inputs, and active tab panes. |
| **Border / Divider** | `#d9dde3` | Light Slate Gray | Borders for input controls, group boxes, card frames, and tab pane boundaries. |
| **Table Gridline** | `#e5e7eb` | Subtle Gray | Gridlines separating cells inside all `QTableWidget`s. |
| **Header Fill** | `#eef0f3` | Cool Neutral Gray | Table header background (`QHeaderView::section`). |
| **Body Text** | `#1f2933` | Deep Slate / Charcoal | Default text color across all widgets, form labels, and table cells. |
| **Muted Text** | `#6b7280` | Cool Medium Gray | Subtitles, helper text, KPI captions, placeholder text (`#muted`). |
| **Secondary Button** | `#e9ecf0` | Light Surface Gray | Secondary buttons ("View Bill", "Hide SQL", "Back To Login", "Deactivate"). |
| **Success State** | `#166534` | Forest Green | Successful payment messages, active connection badges. |
| **Danger / Rollback** | `#b91c1c` | Crimson Red | Failed payment alerts, OCC rollback warnings, database constraint rejection banners. |
| **Heatmap Gradient** | `rgba(74, 42, 107, α)` | Alpha-weighted Royal Purple | Dynamic cell backgrounds in Screen 9 Regional Heatmap ($\alpha \in [40, 200]$). |

---

### 1.2 Typography & Sizing Standards

- **Font Family Stack:** `'Segoe UI', 'Noto Sans', Arial, sans-serif`
- **Default Base Font:** `10pt`, Regular (`weight: 400`), Color: `#1f2933`
- **Screen Title (`QLabel#title`):** `15pt`, Bold (`weight: 700`), Color: `#4a2a6b`
- **KPI Metric Numbers (`QLabel#kpi`):** `16pt`, Bold (`weight: 700`), Color: `#4a2a6b`
- **Section Headers / Group Titles (`QGroupBox::title`):** `10pt`, Bold (`weight: 600`), Color: `#1f2933`
- **Muted Subtitles & Descriptions (`QLabel#muted`):** `9.5pt` - `10pt`, Regular (`weight: 400`), Color: `#6b7280`
- **Button Typography:** `10pt`, Semi-Bold (`weight: 600`), Color: `#ffffff` (Primary) or `#1f2933` (Secondary)

---

### 1.3 Component Sizing, Padding & Border Radii

- **Corner Radii:**
  - Standard Inputs (`QLineEdit`, `QComboBox`, `QSpinBox`): `border-radius: 4px`
  - Push Buttons (`QPushButton`): `border-radius: 4px`
  - Group Boxes (`QGroupBox`): `border-radius: 4px`
  - KPI Cards & Containers (`QFrame#card`): `border-radius: 6px`
- **Padding:**
  - Inputs & Combos: `padding: 5px 8px`
  - Buttons: `padding: 7px 14px`
  - Tab Bar Tabs: `padding: 8px 14px`
  - Table Header Sections: `padding: 5px 8px`
  - Table Cells: `padding: 4px 6px`
- **Global Spacing:**
  - Layout margins: `15px` to `20px`
  - Spacing between consecutive form elements: `8px` to `12px`

---

### 1.4 Complete Qt Style Sheet (QSS) Reference

```css
QWidget {
    font-family: 'Segoe UI', 'Noto Sans', Arial;
    font-size: 10pt;
    color: #1f2933;
}
QMainWindow, QDialog {
    background: #f5f6f8;
}
QTabWidget::pane {
    border: 1px solid #d9dde3;
    background: white;
    border-radius: 4px;
}
QTabBar::tab {
    padding: 8px 14px;
    background: #e9ecf0;
    border: 1px solid #d9dde3;
    border-bottom: none;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: white;
    color: #4a2a6b;
    font-weight: 600;
}
QLabel#title {
    font-size: 15pt;
    font-weight: 700;
    color: #4a2a6b;
}
QLabel#kpi {
    font-size: 16pt;
    font-weight: 700;
    color: #4a2a6b;
}
QLabel#muted {
    color: #6b7280;
}
QPushButton {
    background: #4a2a6b;
    color: white;
    border: none;
    padding: 7px 14px;
    border-radius: 4px;
    font-weight: 600;
}
QPushButton:hover {
    background: #5d3a85;
}
QPushButton:disabled {
    background: #b8adc6;
}
QPushButton[secondary="true"] {
    background: #e9ecf0;
    color: #1f2933;
    font-weight: normal;
}
QPushButton[secondary="true"]:hover {
    background: #dde1e7;
}
QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox, QPlainTextEdit {
    padding: 5px;
    border: 1px solid #c9ced6;
    border-radius: 4px;
    background: white;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus {
    border: 1px solid #4a2a6b;
}
QTableWidget {
    gridline-color: #e5e7eb;
    background: white;
    selection-background-color: #e7dcf3;
    selection-color: #1f2933;
}
QHeaderView::section {
    background: #eef0f3;
    padding: 5px;
    border: none;
    border-bottom: 1px solid #d9dde3;
    font-weight: 600;
}
QGroupBox {
    font-weight: 600;
    border: 1px solid #d9dde3;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 12px;
    background: white;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}
QFrame#card {
    background: white;
    border: 1px solid #d9dde3;
    border-radius: 6px;
}
```

---

## 2. Window Shell & Structural Layout Standards

### 2.1 Window Geometry Matrix
- **Authentication Window (`LoginWindow`):** Fixed dimension `520 x 640 px`, non-resizable by default.
- **Main Portals (`CustomerPortal`, `EmployeePortal`, `AdminPortal`):** `1280 x 860 px`, minimum size `1024 x 700 px`, fully resizable.
- **Detailed Bill Breakdown Dialog (`BillBreakdownDialog`):** `760 x 620 px`, modal dialog.
- **Payment Receipt Dialog (`ReceiptDialog`):** `620 x 360 px`, modal dialog.
- **Add Premise Dialog:** `480 x 320 px`, modal dialog.
- **Add Service Connection Dialog:** `500 x 300 px`, modal dialog.

---

### 2.2 Global Portal Shell Architecture (`PortalWindow`)

Every authenticated portal derives from `PortalWindow` (`portal_base.py`), which enforces a rigid tripartite layout:

```
+-----------------------------------------------------------------------------------+
|  [PUUMS · Portal Name]             [User Full Name (Role)]  [Hide SQL]  [Log out] |  <- Top Bar
+-----------------------------------------------------------------------------------+
|  [ Tab 1 ] [ Tab 2 ] [ Tab 3 ] [ Tab 4 ] [ Tab 5 (Final) ] [ Tab 6 (Final) ]      |  <- Tab Bar
| +-------------------------------------------------------------------------------+ |
| |                                                                               | |
| |                         ACTIVE TAB VIEWPORT CONTENT                           | |
| |                                                                               | |
| +-------------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------------+
|  v SQL executed by this screen (Bottom QDockWidget, Height: 220px)                |  <- SQL Dock
|  +-----------------------------------------------------------------------------+  |
|  | -- 22:50:12                                                                 |  |
|  | SELECT * FROM vw_CitizenActiveBills WHERE cnic = '42101-1234567-1';         |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

1. **Top Header Bar (`QHBoxLayout`):**
   - Brand mark: `QLabel("<b>PUUMS</b> &nbsp;·&nbsp; {portal_name}")` (Left aligned).
   - Horizontal stretch spacer.
   - User profile identity: `QLabel("{name} ({role})")` with `objectName = "muted"`.
   - Secondary button: `QPushButton("Hide SQL")` (toggles the bottom dock visibility).
   - Secondary button: `QPushButton("Log out")` (emits `logout` signal, closes portal, returns to login window).
2. **Central Workspace (`QTabWidget`):**
   - Renders the operational screens for that specific user role.
   - Listens to `currentChanged(idx)`: whenever a tab is switched, triggers `refresh()` on the newly selected tab widget to re-query MySQL.
3. **Bottom SQL Execution Dock (`SqlLogDock` deriving from `QDockWidget`):**
   - Dock title: `"SQL executed by this screen"`.
   - Contains a dark-themed or styled `QPlainTextEdit` displaying executed statements in real-time.
   - Attached to `Qt.BottomDockWidgetArea` with initial height `220px`.

---

## 3. Screen-by-Screen Detailed Design & Recreation Manual

---

### SCREEN 1: Login & Access Control
- **Container Window:** `LoginWindow` (`login_window.py`), Page Index 0 of `QStackedWidget`.
- **Window Size:** `520 x 640 px`.

#### Visual Layout Wireframe
```
+-------------------------------------------------------------+
|                                                             |
|                          PUUMS                              |  <- #title (15pt bold purple)
|        Pakistan Unified Utility Management System           |  <- #muted (10pt gray)
|                   Pilot region: Karachi                     |
|                                                             |
|         +-----------------------------------------+         |
|         | CNIC / Email:  [______________________] |         |  <- QLineEdit
|         | Password:      [••••••••••••••••••••••] |         |  <- QLineEdit (Password)
|         +-----------------------------------------+         |
|                                                             |
|         +-----------------------------------------+         |
|         |               [ LOGIN ]                 |         |  <- QPushButton (Purple)
|         +-----------------------------------------+         |
|         |   [Don't have an account? Register]     |         |  <- QPushButton (Secondary)
|         +-----------------------------------------+         |
|                                                             |
|     No role dropdown: the portal is chosen from database   |  <- #muted note
|                                                             |
+-------------------------------------------------------------+
```

#### Recreation Component Recipe
1. Outer layout: `QVBoxLayout` with margins `(50, 40, 50, 40)`.
2. Top stretch spacer (`addStretch()`).
3. Title header: `QLabel("PUUMS")`, `objectName="title"`, alignment `Qt.AlignCenter`.
4. Subtitle: `QLabel("Pakistan Unified Utility Management System\nPilot region: Karachi")`, `objectName="muted"`, alignment `Qt.AlignCenter`.
5. Spacing: `addSpacing(30)`.
6. Form layout: `QFormLayout` containing:
   - Row 1: `"CNIC / Email"` $\rightarrow$ `QLineEdit` with placeholder `"42101-1234567-1  or  name@puums.pk"`.
   - Row 2: `"Password"` $\rightarrow$ `QLineEdit` with `setEchoMode(QLineEdit.Password)`.
7. Spacing: `addSpacing(10)`.
8. Login button: `QPushButton("LOGIN")`, height $\approx 36\text{px}$, color `#4a2a6b`, triggers `do_login()`.
9. Register button: `QPushButton("Don't have an account? Register")`, secondary styling (`secondary="true"`), switches stack index to 1.
10. Footer hint: `QLabel("No role dropdown: the portal is chosen from UserAccount.role")`, `objectName="muted"`.
11. Bottom stretch spacer (`addStretch()`).

#### Discrepancies vs Original Wireframe
- *Proposal Mockup (`LoginWindow.ui` page 6):* Standard Windows 98/Classic Qt gray form with raw text inputs and a very small login button.
- *As-Built Python Implementation:* Modern centered card layout with generous whitespace, purple brand accents, and dynamic enter-key submission (`returnPressed`).

---

### SCREEN 2: Citizen Self-Registration
- **Container Window:** `LoginWindow` (`login_window.py`), Page Index 1 of `QStackedWidget`.
- **Window Size:** `520 x 640 px`.

#### Visual Layout Wireframe
```
+-------------------------------------------------------------+
|                          REGISTER                           |  <- #title
|                                                             |
| +-- Enter Details ----------------------------------------+ |
| | First Name:    [___________________]                    | |
| | Last Name:     [___________________]                    | |
| | CNIC:          [_____-_______-_    ] (Masked)           | |
| | Phone Number:  [___________________]                    | |
| | Email:         [___________________]                    | |
| | Password:      [•••••••••••••••••••]                    | |
| +---------------------------------------------------------+ |
|                                                             |
| +-- Enter Address (primary premise) ----------------------+ |
| | House No:      [___________________]                    | |
| | Street:        [___________________]                    | |
| | Area:          [___________________]                    | |
| | Region:        [ Karachi East    v ]                    | |
| | Premise Type:  [ Residential     v ]                    | |
| +---------------------------------------------------------+ |
|                                                             |
| [ Back To Login ]                       [ Create Account ]  |
+-------------------------------------------------------------+
```

#### Recreation Component Recipe
1. Outer layout: `QVBoxLayout` with margins `(40, 20, 40, 20)`.
2. Title: `QLabel("REGISTER")`, `objectName="title"`, alignment `Qt.AlignCenter`.
3. Personal Details Group: `QGroupBox("Enter Details")` with `QFormLayout`:
   - First Name (`QLineEdit`), Last Name (`QLineEdit`).
   - CNIC (`QLineEdit` with `setInputMask("99999-9999999-9;_")`).
   - Phone (`QLineEdit` with placeholder `"0300-1234567"`).
   - Email (`QLineEdit`), Password (`QLineEdit`, `EchoMode.Password`).
4. Address Group: `QGroupBox("Enter Address (primary premise)")` with `QFormLayout`:
   - House No (`QLineEdit`), Street (`QLineEdit`), Area (`QLineEdit`).
   - Region (`QComboBox` populated dynamically from `SELECT regionId, regionName FROM Region`).
   - Premise Type (`QComboBox`: `"Residential"`, `"Commercial"`).
5. Navigation Row (`QHBoxLayout`):
   - Left: `QPushButton("Back To Login")` (secondary style, sets stack index 0).
   - Spacer: `addStretch()`.
   - Right: `QPushButton("Create Account")` (primary purple, triggers `do_register()`).

#### Discrepancies vs Original Wireframe
- *Proposal Mockup (page 7):* Showed address fields with an ambiguous generic "Address" field plus House No, Street, Area. Lacked Region and Premise Type.
- *As-Built Python Implementation:* Added `Region` and `Premise Type` comboboxes, and combined House/Street/Area into `address = CONCAT('House ', houseNo, ', ', street, ', ', area)` to satisfy 3NF relational mapping.

---

### SCREEN 3: Citizen Dashboard & Bills
- **Parent Portal:** `CitizenPortal` (`citizen_portal.py`), Tab Index 0 (`DashboardTab`).
- **Window Size:** Inherits `1280 x 860 px`.

#### Visual Layout Wireframe
```
+-----------------------------------------------------------------------------------+
| Citizen Dashboard & Bills                                                         |  <- #title
| Maria Khan   ·   CNIC 42101-1234567-1   ·   0321-1111111   ·   maria.khan@mail.com   |  <- Profile banner
|                                                                                   |
| Registered Premises                                                               |
| +-------------------------------------------------------------------------------+ |
| | Address               | Premise Type | Region         | Active Connections    | | <- Premises table
| | House 12, Street 5... | Residential  | Karachi East   | 3                     | |    (max height 140)
| +-------------------------------------------------------------------------------+ |
|                                                                                   |
| Bills (active connections only)                                                   |
| +-------------------------------------------------------------------------------+ |
| | Bill # | Utility     | Provider   | Billing Month | Amount | Balance | Due  | St| | <- Bills table
| | 10     | Electricity | K-Electric | Sep 2026      | 2,655  | 2,655   | 25...| Un| |    (stretched)
| | 14     | Gas         | SSGC       | Sep 2026      | 1,430  | 1,430   | 20...| Un| |
| | 18     | Piped Water | KWSC       | Sep 2026      | 850    | 0       | 22...| Pd| |
| +-------------------------------------------------------------------------------+ |
|                                                                                   |
|                                                 [ View Bill ]     [ Pay Bill ]    | <- Action row
+-----------------------------------------------------------------------------------+
```

#### Recreation Component Recipe
1. Outer layout: `QVBoxLayout`.
2. Title header: `title("Citizen Dashboard & Bills")`.
3. Profile banner: `QLabel` with `#muted` style displaying citizen name, CNIC, phone, email.
4. Section 1 header: `QLabel("<b>Registered Premises</b>")`.
5. Premises Table: `make_table()` with columns `["Address", "Premise Type", "Region", "Active Connections"]`. Set `setMaximumHeight(140)`.
6. Section 2 header: `QLabel("<b>Bills (active connections only)</b>")`.
7. Bills Table: `make_table()` with columns `["Bill #", "Utility", "Provider", "Billing Month", "Amount (Rs.)", "Balance (Rs.)", "Due Date", "Status"]`.
   - Double-click signal hooked to `view_bill()`.
8. Button Action Row (`QHBoxLayout`):
   - Spacer: `addStretch()`.
   - `QPushButton("View Bill")`: Secondary style, calls `view_bill()` (opens Screen 14).
   - `QPushButton("Pay Bill")`: Primary purple, calls `pay_bill()` (redirects to Screen 4 pre-selecting bill).

#### Discrepancies vs Original Wireframe
- *Proposal Mockup (page 8):* Static layout where clicking "Pay Bill" was visually disconnected from the payment flow.
- *As-Built Python Implementation:* Added seamless cross-tab state transfer: selecting a bill on Dashboard and clicking "Pay Bill" activates the Consolidated Payment tab and automatically checks that bill.

---

### SCREEN 4: Consolidated Bill Payment (Transaction Screen)
- **Parent Portal:** `CitizenPortal` (`citizen_portal.py`), Tab Index 2 (`PaymentTab`).
- **Window Size:** Inherits `1280 x 860 px`.

#### Visual Layout Wireframe
```
+-----------------------------------------------------------------------------------+
| BILL PAYMENT                                                                      |  <- #title
| Tick bills across utilities, pay once. Runs sp_ProcessPayment: OCC check → ...    |  <- #muted
|                                                                                   |
| +-------------------------------------------------------------------------------+ |
| | [x] Bill # | Utility     | Provider   | Month    | Due Date  | Balance | OCC  | | <- Selectable table
| | [x] 10     | Electricity | K-Electric | Sep 2026 | 25 Sep... | 2,655   | 0    | |    (Qt.ItemIsUser
| | [x] 14     | Gas         | SSGC       | Sep 2026 | 20 Sep... | 1,430   | 0    | |     Checkable)
| +-------------------------------------------------------------------------------+ |
|                                                                                   |
| Selected outstanding: Rs. 4,085             Amount: [Rs. 4,085.00]  Method: [Card v] <- Dynamic calculation
|                                                                                   |
| +-- Failure demos (to show ROLLBACK) -------------------------------------------+ |
| | [ ] Simulate network drop before COMMIT   [ ] Simulate another session editing| | <- ACID demo toggles
| +-------------------------------------------------------------------------------+ |
|                                                                                   |
| [                          Process Payment                                    ]   | <- Full-width button
|                                                                                   |
| COMMIT: TXN-00004 successful                                                      | <- Result banner
| Bills: Electricity Sep 2026; Gas Sep 2026                                         |
|                                                                                   |
| [ View Receipt ]                                                                  | <- Enabled on success
+-----------------------------------------------------------------------------------+
```

#### Recreation Component Recipe
1. Outer layout: `QVBoxLayout`.
2. Title: `title("BILL PAYMENT", "Tick bills across utilities, pay once. Runs sp_ProcessPayment: OCC check → Payment → PaymentAllocation → COMMIT / ROLLBACK")`.
3. Selectable Bills Table: `make_table()`.
   - Columns: `["Bill #", "Utility", "Provider", "Month", "Due Date", "Balance Due (Rs.)", "OCC ver."]`.
   - On row creation: `item.setFlags(item.flags() | Qt.ItemIsUserCheckable)`, default `Qt.Unchecked`.
   - Signal: `itemChanged.connect(self._recalc)`.
4. Payment Calculation Row (`QHBoxLayout`):
   - `selected_total`: `QLabel("Selected outstanding: Rs. 0")`.
   - Horizontal stretch spacer.
   - `QLabel("Amount")` $\rightarrow$ `amount`: `QDoubleSpinBox` (Range: 0 to 10,000,000, prefix `"Rs. "`).
   - `QLabel("Method")` $\rightarrow$ `method`: `QComboBox` (`["Card", "Bank Transfer", "JazzCash", "EasyPaisa", "Cash"]`).
5. Failure Simulation Box: `QGroupBox("Failure demos (to show ROLLBACK)")` with `QHBoxLayout`:
   - `sim_drop`: `QCheckBox("Simulate network drop before COMMIT")`.
   - `sim_occ`: `QCheckBox("Simulate another session editing a bill (stale OCC version)")`.
6. Submit Button: `QPushButton("Process Payment")` (large purple button, executes `process()`).
7. Result Label: `QLabel()` with `wordWrap=True`, selectable text.
8. Receipt Button: `QPushButton("View Receipt")` (secondary style, disabled by default, enabled when payment commits).

#### Discrepancies vs Original Wireframe
- *Proposal Mockup (page 11):* Plain table with no multi-select checkboxes. Required typing bill IDs manually.
- *As-Built Python Implementation:* Professional enterprise multi-select checkbox table with automatic balance calculation, dynamic maximum amount bounding, and course-demo failure injection checkboxes.

---

### SCREEN 7: Manual Meter Reading Entry
- **Parent Portal:** `EmployeePortal` (`employee_portal.py`), Tab Index 1 (`MeterReadingTab`).
- **Window Size:** Inherits `1280 x 860 px`.

#### Visual Layout Wireframe
```
+-----------------------------------------------------------------------------------+
| Meter Reading Entry                                                               |  <- #title
| Only connections for SSGC (Gas) · Karachi East can be found                       |  <- Scope subtitle
|                                                                                   |
| [ Consumer No. / Meter No.   e.g. SG-7788-2210             ]  [ Search ]          |  <- Search bar
|                                                                                   |
| +-- Connection -----------------------------------------------------------------+ |
| | Customer:         Maria Khan                                                  | |
| | Provider:         SSGC (Gas)                                                  | |
| | Consumer / Meter: SG-7788-2210  /  GM-204518                                  | |
| | Premise:          House 12, Street 5, Gulshan-e-Iqbal                         | |
| | Last reading:     3262 (Sep 2026)                                             | |
| +-------------------------------------------------------------------------------+ |
|                                                                                   |
| +-- New reading ----------------------------------------------------------------+ |
| | Reading month:   [ Oct 2026    v ]                                            | |
| | Current reading: [       3335.00 ]                                            | |
| | [ Save Reading ]                                                              | |
| +-------------------------------------------------------------------------------+ |
|                                                                                   |
| Reading history for this connection (previous reading auto-filled by trigger)    |
| +-------------------------------------------------------------------------------+ |
| | Month    | Entered     | Previous | Current  | Units | Entered by             | |
| | Sep 2026 | 28 Sep 2026 | 3185     | 3262     | 77    | Usman Tariq            | |
| | Aug 2026 | 28 Aug 2026 | 3100     | 3185     | 85    | Usman Tariq            | |
| +-------------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------------+
```

#### Recreation Component Recipe
1. Outer layout: `QVBoxLayout`.
2. Title: `title("Meter Reading Entry", "Only connections for {scope} can be found (water tankers are not metered)")`.
3. Search Bar (`QHBoxLayout`):
   - `search`: `QLineEdit` with placeholder `"Consumer No. / Meter No.   e.g. SG-7788-2210"`.
   - `btn`: `QPushButton("Search")` hooked to `lookup()`.
4. Connection Details Group: `QGroupBox("Connection")` with `QFormLayout` displaying read-only labels for Customer, Provider, Consumer/Meter, Premise, Last Reading.
5. Entry Group: `QGroupBox("New reading")` with `QFormLayout`:
   - `month`: `QDateEdit` with `displayFormat="MMM yyyy"`, calendar popup.
   - `value`: `QDoubleSpinBox` (Range: 0 to 99,999,999).
   - `save_btn`: `QPushButton("Save Reading")` (disabled until search succeeds).
6. History Table: `make_table()` with columns `["Month", "Entered", "Previous", "Current", "Units", "Entered by"]`.

#### Discrepancies vs Original Wireframe
- *Proposal Mockup (page 16):* Showed only the search bar, connection labels, and empty text box without showing previous reading context.
- *As-Built Python Implementation:* Added a complete historical readings audit grid at the bottom, proving that `trg_validate_meter_reading` auto-fills previous readings and validates non-backward entries.

---

### SCREEN 9: Operational Analytics Dashboard
- **Parent Portal:** `AdminPortal` (`admin_portal.py`), Tab Index 0 (`AnalyticsTab`).
- **Window Size:** Inherits `1280 x 860 px`.

#### Visual Layout Wireframe
```
+-----------------------------------------------------------------------------------+
| Operational Analytics Dashboard                                                   |  <- #title
| All figures come from SQL views: vw_CollectionEfficiency, vw_OutstandingDebt...   |  <- #muted
|                                                                                   |
| Billing month: [ Sep 2026    v ]                                                  |  <- Month picker
|                                                                                   |
| +-----------------+ +-----------------+ +-----------------+ +-----------------+ |
| | Rs. 4,935,000   | | Rs. 4,240,000   | | 85.9%           | | Rs. 812,400     | | <- 4 KPI cards
| | Amount billed   | | Revenue collect | | Collection eff% | | Outstanding rec | |
| +-----------------+ +-----------------+ +-----------------+ +-----------------+ |
|                                                                                   |
| Regional consumption heatmap (units)                                              |
| +-------------------------------------------------------------------------------+ |
| | Region          | Electricity       | Gas               | Piped Water         | | <- Heatmap table
| | Karachi East    | 124,500 [Purple]  | 88,200 [Purple]   | 41,100 [Purple]     | |    (intensity alpha)
| | Karachi West    | 98,700  [Purple]  | 55,100 [Purple]   | 33,800 [Purple]     | |
| +-------------------------------------------------------------------------------+ |
|                                                                                   |
| Outstanding debt by provider and region                                           |
| +-------------------------------------------------------------------------------+ |
| | Provider   | Region       | Unpaid Bills | Amount Outstanding | Oldest Due    | | <- Debt aging table
| | K-Electric | Karachi East | 12           | Rs. 418,600        | 25 Aug 2026   | |
| | SSGC       | Karachi East | 8            | Rs. 239,800        | 20 Aug 2026   | |
| +-------------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------------+
```

#### Recreation Component Recipe
1. Outer layout: `QVBoxLayout`.
2. Title: `title("Operational Analytics Dashboard", "All figures come from SQL views...")`.
3. Filter row: `QLabel("Billing month")` $\rightarrow$ `QDateEdit` with `displayFormat="MMM yyyy"`.
4. KPI Grid (`QGridLayout`): 4 instances of `kpi_card()`:
   - Card 1: Amount billed (Rs.)
   - Card 2: Revenue collected (Rs.)
   - Card 3: Collection efficiency (%)
   - Card 4: Outstanding receivables (Rs.)
5. Vertical Splitter (`QSplitter(Qt.Vertical)`):
   - Upper Widget: Section header and `heat`: `make_table(["Region", "Electricity", "Gas", "Piped Water"])`. Cells dynamically styled with `setBackground(QColor(74, 42, 107, a))`.
   - Lower Widget: Section header and `debt`: `make_table(["Provider", "Region", "Unpaid Bills", "Amount Outstanding (Rs.)", "Oldest Due Date"])`.

#### Discrepancies vs Original Wireframe
- *Proposal Mockup (page 17):* Wireframe showed 6 small stat cards crammed into one row.
- *As-Built Python Implementation:* Consolidated into 4 high-contrast KPI cards and placed the Heatmap and Debt Aging tables inside an adjustable `QSplitter`, drastically improving readability.

---

### SCREEN 10: Regulatory Tariff Management (Setup Screen 1)
- **Parent Portal:** `AdminPortal` (`admin_portal.py`), Tab Index 1 (`TariffTab`).
- **Window Size:** Inherits `1280 x 860 px`.

#### Visual Layout Wireframe
```
+-----------------------------------------------------------------------------------+
| Tariff Management                                                                 |  <- #title
| NEPRA-style slab tariffs per provider + category; effective date versioning       |  <- #muted
|                                                                                   |
| +-- LEFT: All Tariffs ------------------+ +-- RIGHT: Tariff Editor -------------+ |
| | Filter: [ All providers            v ]| | Provider:       [ K-Electric      v ] |
| |                                       | | Category:       [ Residential     v ] |
| | Tariff | Provider | Cat | S# | Min|Max| | Effective Date: [ 01 Oct 2026     v ] |
| | 1      | K-Electr | Res | 1  | 0  |100| | Fixed Charges:  [         200.00    ] |
| | 1      | K-Electr | Res | 2  | 101|150| | FPA (Rs/unit):  [           2.50    ] |
| | 7 (Rev)| K-Electr | Res | 1  | 0  |100| | GST %:          [          18.00    ] |
| |                                       | |                                     | |
| |                                       | | +-- Slabs ------------------------+ | |
| |                                       | | | Min  | Max  | Rate (Rs/unit)    | | |
| |                                       | | | 0    | 100  | 11.00             | | |
| |                                       | | | 101  | 150  | 16.50             | | |
| |                                       | | +---------------------------------+ | |
| |                                       | | [+ slab]  [- slab]                  | |
| |                                       | |                                     | |
| |                                       | | [ ADD ] [ UPDATE ] [ DELETE ] [Clr] | |
| +---------------------------------------+ +-------------------------------------+ |
+-----------------------------------------------------------------------------------+
```

#### Recreation Component Recipe
1. Outer layout: `QVBoxLayout`.
2. Title: `title("Tariff Management", "NEPRA-style slab tariffs per provider + category...")`.
3. Horizontal Splitter (`QSplitter(Qt.Horizontal)`):
   - Left Panel (Master List): `filter`: `QComboBox` ("All providers") + `table`: `make_table(["Tariff", "Provider", "Category", "Slab", "Min", "Max", "Rate", "Fixed", "FPA", "GST %", "Effective"])`.
   - Right Panel (Detail Editor):
     - Form: Provider (`QComboBox`), Category (`QComboBox`), Effective Date (`QDateEdit`), Fixed Charges (`QDoubleSpinBox`), FPA (`QDoubleSpinBox`), GST (`QDoubleSpinBox`).
     - Slabs Group Box: `QTableWidget` with 3 editable columns: `"Min units"`, `"Max units"`, `"Rate (Rs./unit)"`. Buttons `+ slab` (`insertRow`) and `- slab` (`removeRow`).
     - Action Buttons (`QHBoxLayout`): `ADD`, `UPDATE`, `DELETE`, `Clear`.

#### Discrepancies vs Original Wireframe
- *Proposal Mockup (page 17):* Flat, static table with simple ADD/UPDATE/DELETE buttons at the top; had no concept of how slabs were added.
- *As-Built Python Implementation:* Master-Detail Splitter architecture with an embedded, dynamic sub-table for `TariffSlab` rows, guaranteeing atomic multi-table transaction commits.

---

### SCREEN 11: Utility Provider & Region Setup (Setup Screen 2)
- **Parent Portal:** `AdminPortal` (`admin_portal.py`), Tab Index 2 (`ProviderRegionTab`).
- **Window Size:** Inherits `1280 x 860 px`.

#### Visual Layout Wireframe
```
+-----------------------------------------------------------------------------------+
| Provider & Region Setup                                                           |  <- #title
|                                                                                   |
| +-- Utility providers ----------------------------------------------------------+ |
| | [ Provider name ] [ Electricity v ] [ Contact phone ] [ Department          ] | | <- Input bar
| | [ ADD ]  [ UPDATE ]  [ DELETE ]                                               | | <- Actions
| | +---------------------------------------------------------------------------+ | |
| | | ID | Provider   | Utility     | Contact       | Department  | Connections | | | <- Table
| | | 1  | K-Electric | Electricity | 021-9901-2345 | Electricity | 4           | | |
| | | 2  | SSGC       | Gas         | 021-9902-3456 | Gas Dept    | 3           | | |
| | +---------------------------------------------------------------------------+ | |
| +-------------------------------------------------------------------------------+ |
|                                                                                   |
| +-- Operating regions ----------------------------------------------------------+ |
| | [ Region name     ] [ Karachi         ] [ Sindh           ]                   | | <- Input bar
| | [ ADD ]  [ UPDATE ]  [ DELETE ]                                               | | <- Actions
| | +---------------------------------------------------------------------------+ | |
| | | ID | Region        | City    | Province | Associated Premises             | | | <- Table
| | | 1  | Karachi East  | Karachi | Sindh    | 2                               | | |
| | +---------------------------------------------------------------------------+ | |
| +-------------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------------+
```

#### Recreation Component Recipe
1. Outer layout: `QVBoxLayout`.
2. Title: `title("Provider & Region Setup")`.
3. Upper Box: `QGroupBox("Utility providers")`:
   - Form inputs row (`QHBoxLayout`): `p_name` (`QLineEdit`), `p_type` (`QComboBox`: Electricity, Gas, Piped Water), `p_phone` (`QLineEdit`), `p_dept` (`QLineEdit`).
   - Button row: `ADD`, `UPDATE`, `DELETE`.
   - Table: `make_table(["ID", "Provider", "Utility", "Contact", "Department", "Connections"])`. Selection changes hook to `pick_provider()`.
4. Lower Box: `QGroupBox("Operating regions")`:
   - Form inputs row (`QHBoxLayout`): `r_name` (`QLineEdit`), `r_city` (`QLineEdit`, default `"Karachi"`), `r_prov` (`QLineEdit`, default `"Sindh"`).
   - Button row: `ADD`, `UPDATE`, `DELETE`.
   - Table: `make_table(["ID", "Region", "City", "Province", "Premises"])`. Selection changes hook to `pick_region()`.

#### Discrepancies vs Original Wireframe
- *Proposal Mockup (page 18):* Showed inputs directly above tables without grouping, using identical unlabeled boxes.
- *As-Built Python Implementation:* Structured into two clean, separate `QGroupBox`es with field auto-filling upon row selection and explicit connection/premise reference count columns.

---

### SCREEN 14: Detailed Bill Breakdown Dialog
- **Parent Portal:** Opened as a modal `QDialog` from Screen 3.
- **Window Size:** `760 x 620 px`.

#### Visual Layout Wireframe
```
+-----------------------------------------------------------------------------+
| Detailed Bill Breakdown                                                     |  <- #title
|                                                                             |
| +-- Bill header ----------------------------------------------------------+ |
| | Bill No:          BILL-000010       Provider:         K-Electric (Elect)| |
| | Consumer No:      KE-0412345        Meter No:         KE68689           | |
| | Billing Month:    Sep 2026          Due Date:         25 Sep 2026       | |
| | Previous Reading: 12,210            Current Reading:  12,360            | |
| | Units Consumed:   150               Status:           Unpaid            | |
| +-------------------------------------------------------------------------+ |
|                                                                             |
| +-------------------------------------------------------------------------+ |
| | # | Charge                                 | Units | Rate (Rs.) | Amount| |
| | 1 | Slab 1 (0-100)                         | 100   | 10.00      | 1,000 | |
| | 2 | Slab 2 (101-150)                       | 50    | 15.00      | 750   | |
| | 3 | Fixed charges                          | 1     | 200.00     | 200   | |
| | 4 | Fuel price adjustment (FPA)            | 150   | 2.00       | 300   | |
| | 5 | GST 18%                                | 1     | 405.00     | 405   | |
| +-------------------------------------------------------------------------+ |
|                                                                             |
|              Total: Rs. 2,655    Paid: Rs. 0    Balance due: Rs. 2,655      |  <- Totals row
|                                                                             |
|                                       [ Pay This Bill ]         [ Close ]   |  <- Action row
+-----------------------------------------------------------------------------+
```

#### Recreation Component Recipe
1. Dialog class: `QDialog` with layout `QVBoxLayout`.
2. Title: `title("Detailed Bill Breakdown")`.
3. Header Group: `QGroupBox("Bill header")` with `QGridLayout` displaying 5 rows $\times$ 4 columns of key-value pairs (gray muted keys, bold black values).
4. Line Items Table: `make_table(["#", "Charge", "Units", "Rate (Rs.)", "Amount (Rs.)"])`.
5. Summary Label: `QLabel` right-aligned with bold total, paid, and balance due values.
6. Action Row (`QHBoxLayout`):
   - `QPushButton("Pay This Bill")`: Disabled if balance $\le 0$, closes modal and opens Screen 4.
   - `QPushButton("Close")`: Secondary style, closes modal.

#### Discrepancies vs Original Wireframe
- *Proposal Mockup (page 9):* Scattered labels with misaligned boxes and missing grid alignment.
- *As-Built Python Implementation:* Clean, aligned 2-column key-value grid for the header, formatted currency numbers, and integrated "Pay This Bill" action.

---

### SCREEN 18: Monthly Billing Cycle Execution
- **Parent Portal:** `AdminPortal` (`admin_portal.py`), Tab Index 5 (`BillingTab`).
- **Window Size:** Inherits `1280 x 860 px`.

#### Visual Layout Wireframe
```
+-----------------------------------------------------------------------------------+
| Execute Monthly Billing Cycle                                                     |  <- #title
| CALL sp_GenerateMonthlyBills → sp_CalculateCascadingTariff per connection         |  <- #muted
|                                                                                   |
| Month: [ Oct 2026    v ]  Provider: [ All providers    v ]  [ Execute Billing ]   |  <- Control bar
|                                                                                   |
| [================================== 100% =======================================] |  <- Progress bar
|                                                                                   |
| +-- Live Execution Log ---------------------------------------------------------+ |
| | KE-0412345: OK, Rs. 2,655                                                     | | <- QPlainTextEdit
| | SG-7788-2210: SKIPPED, no reading                                             | |    (read-only log)
| | KW-55-0912: SKIPPED, no reading                                               | |
| | Summary: 1 generated, 2 skipped, 0 failed                                     | |
| +-------------------------------------------------------------------------------+ |
|                                                                                   |
| Billing history                                                                   |
| +-------------------------------------------------------------------------------+ |
| | Month    | Provider | Generated | Skipped | Failed | Run By        | Run At   | | <- History table
| | Sep 2026 | All      | 9         | 0       | 0      | admin@puums.pk| 02 Oct...| |
| | Aug 2026 | All      | 9         | 0       | 0      | admin@puums.pk| 02 Sep...| |
| +-------------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------------+
```

#### Recreation Component Recipe
1. Outer layout: `QVBoxLayout`.
2. Title: `title("Execute Monthly Billing Cycle", "CALL sp_GenerateMonthlyBills...")`.
3. Control Bar (`QHBoxLayout`):
   - `month`: `QDateEdit` (`MMM yyyy`).
   - `provider`: `QComboBox` ("All", followed by individual providers).
   - `run`: `QPushButton("Execute Billing Procedure")` (purple, triggers `run()`).
4. Progress Bar: `QProgressBar` (0 to 100%).
5. Log Viewer: `QPlainTextEdit` with `setReadOnly(True)`, maximum height $220\text{px}$.
6. History Table: `make_table(["Month", "Provider", "Generated", "Skipped", "Failed", "Run By", "Run At"])`.

#### Discrepancies vs Original Wireframe
- *Proposal Mockup (page 20):* Showed green progress bar and text box, but lacked column headers for the history grid.
- *As-Built Python Implementation:* Added fully structured `BillingRun` table audit integration, dynamically logging runs and execution timestamps.

---

## 4. Pending Final Milestone Screens: Wireframe & Recreation Blueprints

These blueprints provide the exact implementation specifications for the 5 screens scheduled for the final milestone.

---

### SCREEN 5: On-Demand Water Tanker Booking
- **Role:** Citizen (`CitizenPortal`, Tab 4).

#### Blueprint Wireframe
```
+-----------------------------------------------------------------------------------+
| On-Demand Water Tanker Booking                                                    |
| Order domestic or commercial water tankers at government-regulated flat rates     |
|                                                                                   |
| +-- Book New Delivery ----------------------------------------------------------+ |
| | Capacity:         [ 2000 Litres (Rs. 2,500)                               v ] | |
| | Urgency:          (o) Standard Delivery      ( ) Urgent (+ Rs. 500)           | |
| | Delivery Date:    [ 12 Nov 2026          v ]                                  | |
| | Delivery Address: [ House 12, Street 5, Gulshan-e-Iqbal                     ] | |
| | Estimated Cost:   Rs. 2,500                                                   | |
| | [ Book Water Tanker ]                                                         | |
| +-------------------------------------------------------------------------------+ |
|                                                                                   |
| My Tanker Requests                                                                |
| +-------------------------------------------------------------------------------+ |
| | Request # | Date        | Capacity | Urgency  | Cost      | Status            | |
| | T-104     | 12 Nov 2026 | 2000 L   | Standard | Rs. 2,500 | Pending           | |
| | T-091     | 02 Oct 2026 | 2000 L   | Standard | Rs. 2,500 | Delivered         | |
| +-------------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------------+
```

#### Step-by-Step Implementation Instructions
1. Replace `PlaceholderTab(5, ...)` in `citizen_portal.py` with `TankerBookingTab(QWidget)`.
2. Form layout:
   - `capacity`: `QComboBox` populated from `TankerRate` (`1000L`, `2000L`, `5000L`).
   - `urgency`: `QRadioButton` for Standard, `QRadioButton` for Urgent.
   - `date`: `QDateEdit` defaulting to `QDate.currentDate().addDays(1)`.
   - `address`: `QLineEdit` pre-populated with citizen's primary premise address.
   - `cost_lbl`: `QLabel("Estimated Cost: Rs. X")` auto-updating when capacity or urgency changes.
3. On Click "Book Water Tanker":
   - Execute:
     ```sql
     INSERT INTO TankerRequest (deliveryDate, urgency, deliveryAddress, status, cnic, capacityTier, cost)
     VALUES (%s, %s, %s, 'Pending', %s, %s, %s);
     ```
4. History table: Populate from `SELECT requestId, deliveryDate, capacityTier, urgency, cost, status FROM TankerRequest WHERE cnic = %s ORDER BY deliveryDate DESC`.

---

### SCREEN 8: Request & Dispatch Update
- **Role:** Employee / Dispatcher (`EmployeePortal`, Tab 2).

#### Blueprint Wireframe
```
+-----------------------------------------------------------------------------------+
| Request & Dispatch Operations                                                     |
| Assign tankers to pending orders and update complaint resolution statuses         |
|                                                                                   |
| Pending Water Tanker Orders                                                       |
| +-------------------------------------------------------------------------------+ |
| | Order # | Customer   | Address           | Capacity | Urgency  | Status       | |
| | T-104   | Maria Khan | House 12, St 5... | 2000 L   | Standard | Pending      | |
| +-------------------------------------------------------------------------------+ |
| Assign Tanker: [ TK-188 (2000L, Driver: Rashid Mehmood) v ]  [ Dispatch Tanker ]  |
|                                                                                   |
| Open Utility Complaints                                                           |
| +-------------------------------------------------------------------------------+ |
| | Ticket # | Customer   | Premise       | Category | Description                | |
| | CMP-2104 | Maria Khan | House 12...   | Leakage  | Main pipe valve leaking... | |
| +-------------------------------------------------------------------------------+ |
| Resolution Notes: [ Valve replaced by line maintenance team.                 ]   |
| Status: [ Resolved v ]   [ Update Complaint ]                                     |
+-----------------------------------------------------------------------------------+
```

#### Step-by-Step Implementation Instructions
1. Replace `PlaceholderTab(8, ...)` in `employee_portal.py` with `DispatchUpdateTab(QWidget)`.
2. Layout: `QSplitter(Qt.Vertical)` dividing Tanker Dispatch (top) and Complaint Resolution (bottom).
3. Tanker Section:
   - Table of pending orders filtered by employee region.
   - Combobox populated dynamically:
     ```sql
     SELECT t.vehicleNo, CONCAT(t.vehicleNo, ' (', t.capacityTier, 'L, Driver: ', e.name, ')')
     FROM Tanker t JOIN Employee e ON e.employeeId = t.driverId
     WHERE t.status = 'Available' AND t.capacityTier = %s;
     ```
   - "Dispatch Tanker" button invokes `CALL sp_AssignTanker(p_requestId, p_vehicleNo, @msg)`.
4. Complaint Section:
   - Table of open/in-progress complaints filtered by region and provider.
   - `resolution_notes`: `QLineEdit` or `QPlainTextEdit`.
   - `status`: `QComboBox` (`"In Progress"`, `"Resolved"`).
   - "Update Complaint" button executes:
     ```sql
     UPDATE Complaint SET status = %s, resolutionNotes = %s, employeeId = %s WHERE ticketId = %s;
     ```
     *(Trigger `trg_complaint_status_log` fires automatically).*

---

### SCREEN 12: Fleet & Staff Configuration (Setup Screen 3)
- **Role:** Admin (`AdminPortal`, Tab 3).

#### Blueprint Wireframe
```
+-----------------------------------------------------------------------------------+
| Fleet & Staff Configuration                                                       |
| Manage water tanker fleet inventory and provision employee/admin user accounts   |
|                                                                                   |
| +-- Water Tanker Fleet Registry ------------------------------------------------+ |
| | Vehicle Plate: [ TK-220    ]  Capacity: [ 5000 Litres v ]  Driver: [ Imran v ]| |
| | Status:        [ Available v ]  [ ADD TANKER ]  [ UPDATE ]  [ DELETE ]        | |
| | +---------------------------------------------------------------------------+ | |
| | | Plate   | Capacity | Tier   | Status    | Assigned Driver | Maint Date    | | |
| | | TK-201  | 5000 L   | 5000 L | Available | Imran Sheikh    | 15 Sep 2026   | | |
| | +---------------------------------------------------------------------------+ | |
| +-------------------------------------------------------------------------------+ |
|                                                                                   |
| +-- Provision New Staff Account ------------------------------------------------+ |
| | Name:     [ Fatima Noor         ]  Phone:    [ 0303-1122334      ]            | |
| | Email:    [ fatima.n@puums.pk   ]  Password: [ ••••••••••••••••  ]            | |
| | Role:     [ Meter Reader      v ]  Dept:     [ Electricity Dept  ]            | |
| | Provider: [ K-Electric        v ]  Region:   [ Karachi East    v ]            | |
| | Account:  [ Employee          v ]  [ PROVISION STAFF ACCOUNT ]                | |
| +-------------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------------+
```

#### Step-by-Step Implementation Instructions
1. Replace `PlaceholderTab(12, ...)` in `admin_portal.py` with `FleetStaffTab(QWidget)`.
2. Upper Box: Tanker Fleet Registry (`QGroupBox`):
   - Input fields: Plate No, Capacity Tier dropdown, Driver dropdown (filtered from `Employee WHERE role = 'Driver'`), Status dropdown (`Available`, `Busy`, `Maintenance`).
   - Table displaying all tankers with direct SQL CRUD.
3. Lower Box: Staff Provisioning (`QGroupBox`):
   - Input fields: Name, Phone, Email, Password, Designation Role, Department, Provider dropdown, Region dropdown, Account Role (`Employee` vs `Admin`).
   - "Provision Staff Account" button invokes atomic procedure:
     ```sql
     CALL sp_ProvisionEmployee(p_name, p_phone, p_email, p_role, p_department,
                               p_providerId, p_regionId, p_password, p_accountRole, @empId);
     ```

---

### SCREEN 15: Helpdesk & Customer Complaints
- **Role:** Citizen (`CitizenPortal`, Tab 5).

#### Blueprint Wireframe
```
+-----------------------------------------------------------------------------------+
| Helpdesk & Customer Complaints                                                    |
| Lodge technical, billing, or outage complaints directly with your utility provider|
|                                                                                   |
| +-- Lodge New Complaint --------------------------------------------------------+ |
| | Premise:  [ House 12, Street 5, Gulshan-e-Iqbal                             v ]| |
| | Utility:  [ K-Electric (Electricity)                                        v ]| |
| | Category: [ Outage                                                          v ]| |
| | Description:                                                                  | |
| | [ No electricity in our residential lane since 10:00 AM. Transformers tripped ]| |
| | [ Submit Complaint ]                                                          | |
| +-------------------------------------------------------------------------------+ |
|                                                                                   |
| My Complaints History                                                             |
| +-------------------------------------------------------------------------------+ |
| | Ticket # | Date        | Utility    | Category | Status      | Resolution Notes   | |
| | CMP-2104 | 15 Oct 2026 | Water      | Leakage  | In Progress | Assigned to line...| |
| | CMP-1877 | 28 Sep 2026 | Electric   | Outage   | Resolved    | Feeder repaired.   | |
| +-------------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------------+
```

#### Step-by-Step Implementation Instructions
1. Replace `PlaceholderTab(15, ...)` in `citizen_portal.py` with `ComplaintsTab(QWidget)`.
2. Form layout:
   - Premise dropdown populated from citizen's registered premises.
   - Provider dropdown populated from active providers serving that premise.
   - Category dropdown: `['Outage', 'Billing Error', 'Meter Fault', 'Leakage']`.
   - Description: `QPlainTextEdit` (height $80\text{px}$).
   - Submit button executes:
     ```sql
     INSERT INTO Complaint (category, description, status, cnic, premiseId, providerId)
     VALUES (%s, %s, 'Open', %s, %s, %s);
     ```
3. History table: Populates from `SELECT ticketId, filingDate, category, status, resolutionNotes FROM Complaint WHERE cnic = %s ORDER BY filingDate DESC`.

---

### SCREEN 17: Tanker Rate Configuration
- **Role:** Admin (`AdminPortal`, Tab 4).

#### Blueprint Wireframe
```
+-----------------------------------------------------------------------------------+
| Configure Logistics & Tanker Pricing                                              |
| Update flat rates and emergency delivery surcharges per water tanker capacity tier|
|                                                                                   |
| +-- Update Capacity Rate -------------------------------------------------------+ |
| | Capacity Tier:         [ 2000 Litres                                        v ]| |
| | Base Flat Rate:        [ Rs. 2,500.00                                         ]| |
| | Urgency Surcharge:     [ Rs.   500.00                                         ]| |
| | Effective Date:        [ 01 Oct 2026                                        v ]| |
| | [ Update Pricing Schedule ]                                                   | |
| +-------------------------------------------------------------------------------+ |
|                                                                                   |
| Current Rate Schedule                                                             |
| +-------------------------------------------------------------------------------+ |
| | Capacity Tier | Base Flat Rate (Rs.) | Urgency Surcharge (Rs.) | Effective Date | |
| | 1000 Litres   | 1,500.00             | 300.00                  | 01 Oct 2026    | |
| | 2000 Litres   | 2,500.00             | 500.00                  | 01 Oct 2026    | |
| | 5000 Litres   | 5,500.00             | 1,000.00                | 01 Oct 2026    | |
| +-------------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------------+
```

#### Step-by-Step Implementation Instructions
1. Replace `PlaceholderTab(17, ...)` in `admin_portal.py` with `TankerRateTab(QWidget)`.
2. Form layout:
   - Capacity Tier dropdown: `[1000, 2000, 5000]`.
   - Base Flat Rate: `QDoubleSpinBox` (prefix `"Rs. "`, max 100,000).
   - Urgency Surcharge: `QDoubleSpinBox` (prefix `"Rs. "`, max 50,000).
   - Effective Date: `QDateEdit`.
3. Submit button executes:
   ```sql
   UPDATE TankerRate
   SET baseFlatRate = %s, urgencySurcharge = %s, effectiveDate = %s
   WHERE capacityTier = %s;
   ```
4. Schedule table: Populates from `SELECT capacityTier, baseFlatRate, urgencySurcharge, effectiveDate FROM TankerRate ORDER BY capacityTier`.

---

## 5. Visual Discrepancy & Ergonomic Audit (Current vs Desired)

| Screen / Feature | Proposal Wireframe Mockup | Current As-Built Python State | Identified Discrepancy & Action Required |
|---|---|---|---|
| **Login Window** | Plain gray window, no borders or card hierarchy. | Clean card layout with purple branding. | **Improved:** Current implementation looks substantially more modern than original mockup. |
| **Registration Form** | Lacked Region and Premise Type inputs. | Included Region & Premise Type dropdowns. | **Required for DB:** Must keep current implementation; database requires `Premise.regionId` and `premiseType`. |
| **Payment Flow** | Showed payment screen with single amount box, no checkboxes. | Multi-bill checkbox selection with live calculation. | **Major Upgrade:** Current implementation matches real-world utility billing aggregators. |
| **ACID Rollback Demos** | Not present in proposal wireframe. | Checkboxes for network drop and OCC collision simulation. | **Interim Demo Asset:** Essential for proving ACID compliance to evaluators; keep present. |
| **Meter Reading** | Showed only entry boxes without context. | Included complete historical readings grid. | **Improved:** Proves trigger monotonicity validation live during entry. |
| **Admin Analytics** | 6 stat cards crammed across top. | 4 large KPI cards with high-contrast text. | **Layout Polish:** Could optionally add 2 more cards (Active Connections count, Open Complaints count) for final submission. |
| **Tariff Setup** | Flat table with no slab breakdown mechanism. | Master-Detail Splitter with dynamic editable slab table. | **Major Upgrade:** Solves the relational representation of weak entity `TariffSlab`. |
| **Provider / Region Setup**| Two plain tables without clear grouping. | Two clean `QGroupBox`es with form input rows. | **Improved:** Form layout makes CRUD operations intuitive. |
| **Monthly Billing** | Single progress bar and raw text log. | Progress bar, formatted text log, and `BillingRun` history table. | **Improved:** Retains historical record of billing batches. |
| **Screens 5, 8, 12, 15, 17** | Basic mockups shown in proposal PDF. | Displaying `PlaceholderTab` with listed DB artifacts. | **Final Milestone Delta:** Implement full UI using the blueprints provided in Section 4. |

---

## 6. Practical Guide: Updating Colors, Fonts & Layouts

To customize the visual style or brand theme, edit the following key files:

### 1. Modifying the Global Color Theme
Open [`ui_common.py`](ui_common.py) and modify lines 14–39:
- To change the **Primary Purple Brand Color**, find `#4a2a6b` and replace it with your preferred brand color (e.g. `#1e3a8a` for Deep Navy Blue or `#0f766e` for Emerald Green).
- To change the **Button Hover Color**, replace `#5d3a85` with a slightly lighter/darker shade of your brand color.
- To change the **Selection Color**, replace `#e7dcf3` with a soft pastel tint of your brand color.

### 2. Changing the Application Font
In `ui_common.py`, locate line 15:
```css
QWidget { font-family: 'Segoe UI', 'Noto Sans', Arial; font-size: 10pt; color: #1f2933; }
```
Replace `'Segoe UI'` with your desired typeface (e.g., `'Inter'`, `'Roboto'`, or `'Fira Sans'`).

### 3. Adjusting Default Window Dimensions
- Login Window: Open [`login_window.py`](login_window.py) line 19 $\rightarrow$ `self.resize(520, 640)`.
- Main Portals: Open [`portal_base.py`](portal_base.py) line 16 $\rightarrow$ `self.resize(1280, 860)`.
- Bottom SQL Dock Height: Open [`portal_base.py`](portal_base.py) line 42 $\rightarrow$ `self.resizeDocks([self.sql_dock], [220], Qt.Vertical)`.
