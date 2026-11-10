"""EmployeePortal: Screens 6 and 7. Screen 8 is a placeholder."""
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (QDateEdit, QDoubleSpinBox, QFormLayout, QGroupBox, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget)

from app.db import DBError
from app.portals.portal_base import PortalWindow
from app.ui.ui_common import PlaceholderTab, error, fill_table, fmt, info, kpi_card, make_table, title


class EmployeePortal(PortalWindow):
    def __init__(self, database, user):
        super().__init__(database, user, "Employee Portal")
        scope = database.one(
            "SELECT r.regionName, p.providerName, p.utilityType FROM Employee e "
            "LEFT JOIN Region r ON r.regionId = e.regionId "
            "LEFT JOIN Provider p ON p.providerId = e.providerId WHERE e.employeeId = %s",
            (user["employeeId"],))
        user["scope"] = f"{scope[1]} ({scope[2]}) · {scope[0]}"
        self.queue = TaskQueueTab(self)
        self.reading = MeterReadingTab(self)
        self.tabs.addTab(self.queue, "Task Queue")
        self.tabs.addTab(self.reading, "Meter Reading")
        self.tabs.addTab(PlaceholderTab(8, "Request & Dispatch Update",
                         ["sp_AssignTanker (checks capacity tier + availability, one transaction)",
                          "trg_tanker_status_sync (Tanker Busy / Available)",
                          "trg_complaint_status_log (Open → In Progress → Resolved audit)"]),
                         "Request && Dispatch Update")
        self.queue.refresh()


# ======================================================================
# Screen 6 - Employee Operations Queue (vw_EmployeeTaskQueue)
# ======================================================================
class TaskQueueTab(QWidget):
    def __init__(self, portal):
        super().__init__()
        self.p = portal
        lay = QVBoxLayout(self)
        lay.addLayout(title("Employee Operations Queue",
                            f"{portal.user['name']} · {portal.user['jobRole']} · {portal.user['scope']}"))
        cards = QHBoxLayout()
        f1, self.k_open = kpi_card("Open / in-progress complaints")
        f2, self.k_pending = kpi_card("Pending tanker requests")
        f3, self.k_disp = kpi_card("Tankers dispatched")
        for f in (f1, f2, f3):
            cards.addWidget(f)
        lay.addLayout(cards)
        lay.addWidget(QLabel("<b>Tasks for my region and provider</b>"))
        self.table = make_table()
        lay.addWidget(self.table)

    def refresh(self):
        u = self.p.user
        try:
            _, rows = self.p.db.query(
                "SELECT taskRef, customer, taskType, area, status, taskDate "
                "FROM vw_EmployeeTaskQueue WHERE regionId = %s AND providerId = %s "
                "ORDER BY taskDate", (u["regionId"], u["providerId"]))
        except DBError as e:
            error(self, e)
            return
        fill_table(self.table, ["ID", "Customer", "Request", "Area", "Status", "Date"], rows)
        self.k_open.setText(str(sum(1 for r in rows if r[2] == "Complaint")))
        self.k_pending.setText(str(sum(1 for r in rows if r[2] == "Water Tanker" and r[4] == "Pending")))
        self.k_disp.setText(str(sum(1 for r in rows if r[4] == "Dispatched")))


# ======================================================================
# Screen 7 - Manual Meter Reading Entry
# ======================================================================
class MeterReadingTab(QWidget):
    def __init__(self, portal):
        super().__init__()
        self.p = portal
        self.conn = None
        lay = QVBoxLayout(self)
        lay.addLayout(title("Meter Reading Entry",
                            f"Only connections for {portal.user['scope']} can be found "
                            "(water tankers are not metered)"))
        s = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Consumer No. / Meter No.   e.g. SG-7788-2210")
        self.search.returnPressed.connect(self.lookup)
        btn = QPushButton("Search")
        btn.clicked.connect(self.lookup)
        s.addWidget(self.search)
        s.addWidget(btn)
        lay.addLayout(s)

        box = QGroupBox("Connection")
        self.details = QFormLayout(box)
        self.lbl = {}
        for k in ["Customer", "Provider", "Consumer / Meter", "Premise", "Last reading"]:
            self.lbl[k] = QLabel("-")
            self.details.addRow(k, self.lbl[k])
        lay.addWidget(box)

        entry = QGroupBox("New reading")
        ef = QFormLayout(entry)
        self.month = QDateEdit(QDate.currentDate().addMonths(-1))
        self.month.setDisplayFormat("MMM yyyy")
        self.month.setCalendarPopup(True)
        self.value = QDoubleSpinBox()
        self.value.setRange(0, 99_999_999)
        self.value.setDecimals(2)
        ef.addRow("Reading month", self.month)
        ef.addRow("Current reading", self.value)
        self.save_btn = QPushButton("Save Reading")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save)
        ef.addRow(self.save_btn)
        lay.addWidget(entry)

        lay.addWidget(QLabel("<b>Reading history for this connection</b> "
                             "(previous reading is filled in by trg_validate_meter_reading)"))
        self.history = make_table()
        lay.addWidget(self.history)

    def lookup(self):
        key = self.search.text().strip()
        u = self.p.user
        try:
            row = self.p.db.one(
                "SELECT sc.connectionId, CONCAT(c.firstName, ' ', c.lastName), pr.providerName, "
                "       sc.consumerNo, sc.meterNo, p.address, "
                "       (SELECT currentReading FROM MeterReading m WHERE m.connectionId = sc.connectionId "
                "         ORDER BY readingMonth DESC LIMIT 1), "
                "       (SELECT readingMonth FROM MeterReading m WHERE m.connectionId = sc.connectionId "
                "         ORDER BY readingMonth DESC LIMIT 1) "
                "FROM ServiceConnection sc "
                "JOIN Provider pr ON pr.providerId = sc.providerId "
                "JOIN Premise p   ON p.premiseId   = sc.premiseId "
                "JOIN Citizen c   ON c.cnic        = p.cnic "
                "WHERE (sc.consumerNo = %s OR sc.meterNo = %s) "
                "  AND sc.providerId = %s AND p.regionId = %s AND sc.status = 'Active'",
                (key, key, u["providerId"], u["regionId"]))
        except DBError as e:
            error(self, e)
            return
        if not row:
            self.conn = None
            self.save_btn.setEnabled(False)
            info(self, "No active connection with that number in your provider/region.")
            return
        self.conn = row[0]
        self.lbl["Customer"].setText(row[1])
        self.lbl["Provider"].setText(row[2])
        self.lbl["Consumer / Meter"].setText(f"{row[3]}  /  {row[4]}")
        self.lbl["Premise"].setText(row[5])
        last = f"{fmt(row[6])} ({row[7].strftime('%b %Y')})" if row[6] is not None else "none"
        self.lbl["Last reading"].setText(last)
        if row[7]:
            self.month.setDate(QDate(row[7].year, row[7].month, 1).addMonths(1))
        self.value.setValue(float(row[6] or 0))
        self.save_btn.setEnabled(True)
        self.load_history()

    def load_history(self):
        _, rows = self.p.db.query(
            "SELECT DATE_FORMAT(mr.readingMonth, '%%b %%Y'), mr.readingDate, mr.previousReading, "
            "       mr.currentReading, mr.currentReading - mr.previousReading AS units, e.name "
            "FROM MeterReading mr JOIN Employee e ON e.employeeId = mr.employeeId "
            "WHERE mr.connectionId = %s ORDER BY mr.readingMonth DESC", (self.conn,))
        fill_table(self.history, ["Month", "Entered", "Previous", "Current", "Units", "Entered by"], rows)

    def save(self):
        d = self.month.date()
        try:
            self.p.db.execute(
                "INSERT INTO MeterReading (readingMonth, readingDate, currentReading, connectionId, employeeId) "
                "VALUES (%s, CURDATE(), %s, %s, %s)",
                (f"{d.year()}-{d.month():02d}-01", round(self.value.value(), 2),
                 self.conn, self.p.user["employeeId"]))
            info(self, "Reading saved.")
            self.lookup()
        except DBError as e:
            error(self, e)
