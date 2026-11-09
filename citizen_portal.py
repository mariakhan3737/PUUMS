"""CustomerPortal: Screens 3, 14, 13, 4 (transaction), 16. Screens 5 and 15
are placeholders for the final milestone."""
import json
from decimal import Decimal

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QDateEdit, QDialog, QDoubleSpinBox,
                             QFormLayout, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QVBoxLayout, QWidget)

from db import DBError
from portal_base import PortalWindow
from ui_common import (PlaceholderTab, error, fill_table, fmt, info, make_table,
                       secondary, selected_row, title)


class CitizenPortal(PortalWindow):
    def __init__(self, database, user):
        super().__init__(database, user, "Customer Portal")
        self.dashboard = DashboardTab(self)
        self.connections = ConnectionsTab(self)
        self.payment = PaymentTab(self)
        self.ledger = LedgerTab(self)
        self.tabs.addTab(self.dashboard, "Dashboard && Bills")
        self.tabs.addTab(self.connections, "My Utility Connections")
        self.tabs.addTab(self.payment, "Consolidated Payment")
        self.tabs.addTab(self.ledger, "Transaction Ledger")
        self.tabs.addTab(PlaceholderTab(5, "Tanker Booking",
                         ["TankerRequest / TankerRate tables",
                          "sp_AssignTanker, trg_tanker_status_sync",
                          "cost = TankerRate.baseFlatRate (+ urgencySurcharge)"]), "Tanker Booking")
        self.tabs.addTab(PlaceholderTab(15, "Helpdesk & Complaints",
                         ["Complaint table + ComplaintStatusLog",
                          "trg_complaint_status_log (audit of every status change)"]),
                         "Helpdesk Complaints")
        self.dashboard.refresh()

    def open_payment_for(self, bill_id):
        self.tabs.setCurrentWidget(self.payment)
        self.payment.preselect(bill_id)


# ======================================================================
# Screen 3 - Citizen Dashboard & Bills
# ======================================================================
class DashboardTab(QWidget):
    def __init__(self, portal):
        super().__init__()
        self.p = portal
        lay = QVBoxLayout(self)
        lay.addLayout(title("Citizen Dashboard & Bills"))
        self.profile = QLabel()
        self.profile.setObjectName("muted")
        lay.addWidget(self.profile)

        lay.addWidget(QLabel("<b>Registered Premises</b>"))
        self.premises = make_table()
        self.premises.setMaximumHeight(140)
        lay.addWidget(self.premises)

        lay.addWidget(QLabel("<b>Bills (active connections only)</b>"))
        self.bills = make_table()
        self.bills.doubleClicked.connect(self.view_bill)
        lay.addWidget(self.bills)

        row = QHBoxLayout()
        view = secondary(QPushButton("View Bill"))
        view.clicked.connect(self.view_bill)
        pay = QPushButton("Pay Bill")
        pay.clicked.connect(self.pay_bill)
        row.addWidget(view)
        row.addWidget(pay)
        lay.addLayout(row)

    def refresh(self):
        db, cnic = self.p.db, self.p.user["cnic"]
        try:
            c = db.one("SELECT firstName, lastName, cnic, phone, email FROM Citizen WHERE cnic=%s", (cnic,))
            self.profile.setText(f"{c[0]} {c[1]}   ·   CNIC {c[2]}   ·   {c[3] or ''}   ·   {c[4] or ''}")
            _, rows = db.query(
                "SELECT p.address, p.premiseType, r.regionName, "
                "       COUNT(sc.connectionId) AS activeConnections "
                "FROM Premise p JOIN Region r ON r.regionId = p.regionId "
                "LEFT JOIN ServiceConnection sc ON sc.premiseId = p.premiseId AND sc.status = 'Active' "
                "WHERE p.cnic = %s GROUP BY p.premiseId, p.address, p.premiseType, r.regionName", (cnic,))
            fill_table(self.premises, ["Address", "Premise Type", "Region", "Active Connections"], rows)
            _, rows = db.query(
                "SELECT billId, utility, provider, DATE_FORMAT(billingMonth, '%%b %%Y'), totalAmount, "
                "       balanceDue, dueDate, status "
                "FROM vw_CitizenActiveBills WHERE cnic = %s "
                "ORDER BY billingMonth DESC, utility", (cnic,))
            fill_table(self.bills, ["Bill #", "Utility", "Provider", "Billing Month", "Amount (Rs.)",
                                    "Balance (Rs.)", "Due Date", "Status"], rows)
        except DBError as e:
            error(self, e)

    def view_bill(self):
        row = selected_row(self.bills)
        if not row:
            info(self, "Select a bill first.")
            return
        BillBreakdownDialog(self.p, row[0]).exec_()
        self.refresh()

    def pay_bill(self):
        row = selected_row(self.bills)
        if not row:
            info(self, "Select a bill first.")
            return
        if row[5] <= 0:
            info(self, "This bill is already paid.")
            return
        self.p.open_payment_for(row[0])


# ======================================================================
# Screen 14 - Detailed Bill Breakdown (vw_BillLineItems)
# ======================================================================
class BillBreakdownDialog(QDialog):
    def __init__(self, portal, bill_id):
        super().__init__(portal)
        self.p = portal
        self.bill_id = bill_id
        self.setWindowTitle("Invoice Line Items")
        self.resize(760, 620)
        lay = QVBoxLayout(self)
        lay.addLayout(title("Detailed Bill Breakdown"))
        try:
            _, rows = portal.db.query(
                "SELECT providerName, utilityType, consumerNo, meterNo, billingMonth, dueDate, status, "
                "       previousReading, currentReading, unitsConsumed, "
                "       itemNo, chargeDescription, units, unitRate, lineAmount "
                "FROM vw_BillLineItems WHERE billId = %s ORDER BY itemNo", (bill_id,))
            bal = portal.db.one("SELECT totalAmount, paidAmount, balanceDue FROM vw_BillBalance "
                                "WHERE billId = %s", (bill_id,))
        except DBError as e:
            error(self, e)
            return
        h = rows[0]
        grid = QGridLayout()
        info_pairs = [("Bill No", f"BILL-{bill_id:06d}"), ("Provider", f"{h[0]} ({h[1]})"),
                      ("Consumer No", h[2]), ("Meter No", h[3]),
                      ("Billing Month", h[4].strftime("%b %Y")), ("Due Date", fmt(h[5])),
                      ("Previous Reading", fmt(h[7])), ("Current Reading", fmt(h[8])),
                      ("Units Consumed", fmt(h[9])), ("Status", h[6])]
        for i, (k, v) in enumerate(info_pairs):
            lbl = QLabel(k)
            lbl.setObjectName("muted")
            grid.addWidget(lbl, i // 2, (i % 2) * 2)
            grid.addWidget(QLabel(f"<b>{v}</b>"), i // 2, (i % 2) * 2 + 1)
        box = QGroupBox("Bill header")
        box.setLayout(grid)
        lay.addWidget(box)

        items = make_table()
        fill_table(items, ["#", "Charge", "Units", "Rate (Rs.)", "Amount (Rs.)"],
                   [r[10:15] for r in rows])
        lay.addWidget(items)

        tot = QLabel(f"Total: <b>Rs. {fmt(bal[0])}</b> &nbsp;&nbsp; Paid: Rs. {fmt(bal[1])} "
                     f"&nbsp;&nbsp; Balance due: <b>Rs. {fmt(bal[2])}</b>")
        tot.setAlignment(Qt.AlignRight)
        lay.addWidget(tot)
        row = QHBoxLayout()
        pay = QPushButton("Pay This Bill")
        pay.setEnabled(bal[2] > 0)
        pay.clicked.connect(self._pay)
        close = secondary(QPushButton("Close"))
        close.clicked.connect(self.accept)
        row.addWidget(pay)
        row.addWidget(close)
        lay.addLayout(row)

    def _pay(self):
        self.accept()
        self.p.open_payment_for(self.bill_id)


# ======================================================================
# Screen 13 - My Utility Connections
# ======================================================================
class ConnectionsTab(QWidget):
    def __init__(self, portal):
        super().__init__()
        self.p = portal
        lay = QVBoxLayout(self)
        lay.addLayout(title("Manage Utility Accounts",
                            "One service connection per utility per premise "
                            "(UNIQUE premiseId, providerId)"))
        row = QHBoxLayout()
        add_p = secondary(QPushButton("Add Premise"))
        add_p.clicked.connect(self.add_premise)
        add_c = QPushButton("Add Connection")
        add_c.clicked.connect(self.add_connection)
        row.addWidget(add_p)
        row.addWidget(add_c)
        lay.addLayout(row)
        self.table = make_table()
        lay.addWidget(self.table)
        row2 = QHBoxLayout()
        deact = secondary(QPushButton("Deactivate"))
        deact.clicked.connect(lambda: self.set_status("Inactive"))
        react = secondary(QPushButton("Reactivate"))
        react.clicked.connect(lambda: self.set_status("Active"))
        row2.addWidget(deact)
        row2.addWidget(react)
        lay.addLayout(row2)

    def refresh(self):
        try:
            _, rows = self.p.db.query(
                "SELECT sc.connectionId, pr.providerName, pr.utilityType, sc.consumerNo, sc.meterNo, "
                "       p.area AS premise, sc.status, sc.connectionDate "
                "FROM ServiceConnection sc "
                "JOIN Premise p   ON p.premiseId   = sc.premiseId "
                "JOIN Provider pr ON pr.providerId = sc.providerId "
                "WHERE p.cnic = %s ORDER BY p.premiseId, pr.providerId", (self.p.user["cnic"],))
            fill_table(self.table, ["ID", "Provider", "Utility", "Consumer No.", "Meter No.",
                                    "Premise", "Status", "Connection Date"], rows)
        except DBError as e:
            error(self, e)

    def set_status(self, status):
        row = selected_row(self.table)
        if not row:
            info(self, "Select a connection first.")
            return
        try:
            self.p.db.execute("UPDATE ServiceConnection SET status = %s WHERE connectionId = %s",
                              (status, row[0]))
            self.refresh()
        except DBError as e:
            error(self, e)

    def add_premise(self):
        d = QDialog(self)
        d.setWindowTitle("Add Premise")
        f = QFormLayout(d)
        house, street, area = QLineEdit(), QLineEdit(), QLineEdit()
        region, ptype = QComboBox(), QComboBox()
        _, regions = self.p.db.query("SELECT regionId, regionName FROM Region ORDER BY regionName")
        for rid, name in regions:
            region.addItem(name, rid)
        ptype.addItems(["Residential", "Commercial"])
        for lbl, w in [("House No", house), ("Street", street), ("Area", area),
                       ("Region", region), ("Premise Type", ptype)]:
            f.addRow(lbl, w)
        ok = QPushButton("Save")
        ok.clicked.connect(d.accept)
        f.addRow(ok)
        if d.exec_() != QDialog.Accepted:
            return
        try:
            self.p.db.execute(
                "INSERT INTO Premise (address, houseNo, street, area, premiseType, cnic, regionId) "
                "VALUES (CONCAT('House ', %s, ', ', %s, ', ', %s), %s, %s, %s, %s, %s, %s)",
                (house.text(), street.text(), area.text(), house.text(), street.text(), area.text(),
                 ptype.currentText(), self.p.user["cnic"], region.currentData()))
            self.refresh()
        except DBError as e:
            error(self, e)

    def add_connection(self):
        d = QDialog(self)
        d.setWindowTitle("Add Service Connection")
        f = QFormLayout(d)
        premise, provider = QComboBox(), QComboBox()
        consumer, meter = QLineEdit(), QLineEdit()
        _, prem = self.p.db.query("SELECT premiseId, address FROM Premise WHERE cnic = %s",
                                  (self.p.user["cnic"],))
        for pid, addr in prem:
            premise.addItem(addr, pid)
        _, provs = self.p.db.query("SELECT providerId, CONCAT(providerName, ' - ', utilityType) "
                                   "FROM Provider ORDER BY providerId")
        for pid, name in provs:
            provider.addItem(name, pid)
        for lbl, w in [("Premise", premise), ("Provider", provider),
                       ("Consumer / Account No.", consumer), ("Meter No.", meter)]:
            f.addRow(lbl, w)
        ok = QPushButton("Save")
        ok.clicked.connect(d.accept)
        f.addRow(ok)
        if d.exec_() != QDialog.Accepted:
            return
        try:
            self.p.db.execute(
                "INSERT INTO ServiceConnection (consumerNo, meterNo, connectionDate, status, premiseId, providerId) "
                "VALUES (%s, %s, CURDATE(), 'Active', %s, %s)",
                (consumer.text().strip(), meter.text().strip(), premise.currentData(), provider.currentData()))
            self.refresh()
        except DBError as e:
            error(self, e)


# ======================================================================
# Screen 4 - Consolidated Bill Payment (TRANSACTION SCREEN)
# ======================================================================
class PaymentTab(QWidget):
    def __init__(self, portal):
        super().__init__()
        self.p = portal
        self._preselect = None
        lay = QVBoxLayout(self)
        lay.addLayout(title("BILL PAYMENT",
                            "Tick bills across utilities, pay once. Runs sp_ProcessPayment: "
                            "OCC check → Payment → PaymentAllocation → COMMIT / ROLLBACK"))
        self.table = make_table()
        self.table.itemChanged.connect(self._recalc)
        lay.addWidget(self.table)

        form = QHBoxLayout()
        self.selected_total = QLabel("Selected outstanding: Rs. 0")
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0, 10_000_000)
        self.amount.setDecimals(2)
        self.amount.setPrefix("Rs. ")
        self.method = QComboBox()
        self.method.addItems(["Card", "Bank Transfer", "JazzCash", "EasyPaisa", "Cash"])
        form.addWidget(self.selected_total)
        form.addStretch()
        form.addWidget(QLabel("Amount"))
        form.addWidget(self.amount)
        form.addWidget(QLabel("Method"))
        form.addWidget(self.method)
        lay.addLayout(form)

        demo = QGroupBox("Failure demos (to show ROLLBACK)")
        dl = QHBoxLayout(demo)
        self.sim_drop = QCheckBox("Simulate network drop before COMMIT")
        self.sim_occ = QCheckBox("Simulate another session editing a bill (stale OCC version)")
        dl.addWidget(self.sim_drop)
        dl.addWidget(self.sim_occ)
        lay.addWidget(demo)

        btn = QPushButton("Process Payment")
        btn.clicked.connect(self.process)
        lay.addWidget(btn)

        self.result = QLabel()
        self.result.setWordWrap(True)
        self.result.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lay.addWidget(self.result)
        self.receipt_btn = secondary(QPushButton("View Receipt"))
        self.receipt_btn.setEnabled(False)
        self.receipt_btn.clicked.connect(lambda: ReceiptDialog(self.p, self.last_payment).exec_())
        lay.addWidget(self.receipt_btn)
        self.last_payment = None

    def preselect(self, bill_id):
        self._preselect = bill_id
        self.refresh()

    def refresh(self):
        try:
            _, rows = self.p.db.query(
                "SELECT billId, utility, provider, DATE_FORMAT(billingMonth, '%%b %%Y'), dueDate, "
                "       balanceDue, occVersion "
                "FROM vw_CitizenActiveBills WHERE cnic = %s AND balanceDue > 0 "
                "ORDER BY dueDate", (self.p.user["cnic"],))
        except DBError as e:
            error(self, e)
            return
        self.table.blockSignals(True)
        fill_table(self.table, ["Bill #", "Utility", "Provider", "Month", "Due Date",
                                "Balance Due (Rs.)", "OCC ver."], rows)
        for r, row in enumerate(rows):
            item = self.table.item(r, 0)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if row[0] == self._preselect else Qt.Unchecked)
        self.table.blockSignals(False)
        self._preselect = None
        self._recalc()

    def _checked(self):
        out = []
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 0)
            if item.checkState() == Qt.Checked:
                out.append(item.data(Qt.UserRole))
        return out

    def _recalc(self, *_):
        total = sum((row[5] for row in self._checked()), Decimal(0))
        self.selected_total.setText(f"Selected outstanding: <b>Rs. {fmt(total)}</b>")
        self.amount.setMaximum(float(total) if total else 0)
        self.amount.setValue(float(total))

    def process(self):
        bills = self._checked()
        if not bills:
            info(self, "Tick at least one bill.")
            return
        payload = json.dumps([{"billId": b[0], "ver": b[6]} for b in bills])
        try:
            if self.sim_occ.isChecked():
                # another session changes the first bill after this screen loaded it
                self.p.db.execute("UPDATE Bill SET occVersion = occVersion + 1 WHERE billId = %s",
                                  (bills[0][0],))
            _, (pid, msg) = self.p.db.call(
                "CALL sp_ProcessPayment(%s, %s, %s, %s, %s, @pid, @msg)",
                (self.p.user["cnic"], payload, round(self.amount.value(), 2),
                 self.method.currentText(), self.sim_drop.isChecked()),
                out_vars=("@pid", "@msg"))
        except DBError as e:
            error(self, e)
            return
        ok = pid is not None
        names = "; ".join(f"{b[1]} {b[3]}" for b in bills)
        color = "#166534" if ok else "#b91c1c"
        self.result.setText(f"<span style='color:{color}; font-weight:600'>{msg}</span><br>"
                            f"Bills: {names}")
        self.last_payment = pid
        self.receipt_btn.setEnabled(ok)
        self.sim_drop.setChecked(False)
        self.sim_occ.setChecked(False)
        self.refresh()


class ReceiptDialog(QDialog):
    def __init__(self, portal, payment_id):
        super().__init__(portal)
        self.setWindowTitle("Payment Receipt")
        self.resize(620, 360)
        lay = QVBoxLayout(self)
        try:
            h = portal.db.one(
                "SELECT transactionRef, paymentDate, amountPaid, paymentMethod, transactionStatus "
                "FROM vw_PaymentLedger WHERE paymentId = %s", (payment_id,))
            _, rows = portal.db.query(
                "SELECT pa.billId, pr.utilityType, DATE_FORMAT(b.billingMonth, '%%b %%Y'), "
                "       pa.allocatedAmount, b.status "
                "FROM PaymentAllocation pa JOIN Bill b ON b.billId = pa.billId "
                "JOIN ServiceConnection sc ON sc.connectionId = b.connectionId "
                "JOIN Provider pr ON pr.providerId = sc.providerId "
                "WHERE pa.paymentId = %s ORDER BY b.dueDate", (payment_id,))
        except DBError as e:
            error(self, e)
            return
        lay.addLayout(title(f"Receipt {h[0]}", f"{fmt(h[1])} · {h[3]} · {h[4]}"))
        t = make_table()
        fill_table(t, ["Bill #", "Utility", "Month", "Allocated (Rs.)", "Bill Status"], rows)
        lay.addWidget(t)
        lay.addWidget(QLabel(f"<b>Total paid: Rs. {fmt(h[2])}</b>"))
        close = secondary(QPushButton("Close"))
        close.clicked.connect(self.accept)
        lay.addWidget(close)


# ======================================================================
# Screen 16 - Transaction Ledger & Receipts (vw_PaymentLedger)
# ======================================================================
class LedgerTab(QWidget):
    def __init__(self, portal):
        super().__init__()
        self.p = portal
        lay = QVBoxLayout(self)
        lay.addLayout(title("Transaction Ledger"))
        f = QHBoxLayout()
        self.date_from = QDateEdit(QDate(2026, 1, 1))
        self.date_to = QDateEdit(QDate.currentDate())
        for d in (self.date_from, self.date_to):
            d.setCalendarPopup(True)
            d.setDisplayFormat("dd/MM/yyyy")
            d.dateChanged.connect(self.refresh)
        self.status = QComboBox()
        self.status.addItems(["All", "Successful", "Failed"])
        self.status.currentIndexChanged.connect(self.refresh)
        f.addWidget(QLabel("From"))
        f.addWidget(self.date_from)
        f.addWidget(QLabel("To"))
        f.addWidget(self.date_to)
        f.addWidget(QLabel("Status"))
        f.addWidget(self.status)
        f.addStretch()
        lay.addLayout(f)
        self.summary = QLabel()
        lay.addWidget(self.summary)
        self.table = make_table()
        self.table.doubleClicked.connect(self.receipt)
        lay.addWidget(self.table)
        btn = secondary(QPushButton("View Receipt"))
        btn.clicked.connect(self.receipt)
        lay.addWidget(btn)

    def refresh(self):
        status = self.status.currentText()
        try:
            _, rows = self.p.db.query(
                "SELECT paymentId, transactionRef, paymentDate, amountPaid, paymentMethod, "
                "       allocatedBills, transactionStatus "
                "FROM vw_PaymentLedger "
                "WHERE cnic = %s AND DATE(paymentDate) BETWEEN %s AND %s "
                "  AND (%s = 'All' OR transactionStatus = %s) "
                "ORDER BY paymentDate DESC",
                (self.p.user["cnic"], self.date_from.date().toPyDate(), self.date_to.date().toPyDate(),
                 status, status))
            outstanding = self.p.db.one(
                "SELECT COALESCE(SUM(balanceDue), 0) FROM vw_CitizenActiveBills WHERE cnic = %s",
                (self.p.user["cnic"],))[0]
        except DBError as e:
            error(self, e)
            return
        fill_table(self.table, ["ID", "Transaction", "Date", "Amount Paid (Rs.)", "Method",
                                "Allocated Bills", "Status"], rows, hidden=(0,))
        paid = sum((r[3] for r in rows if r[6] == "Successful"), Decimal(0))
        self.summary.setText(f"Paid in period: <b>Rs. {fmt(paid)}</b> &nbsp;&nbsp;·&nbsp;&nbsp; "
                             f"Current outstanding balance: <b>Rs. {fmt(outstanding)}</b>")

    def receipt(self):
        row = selected_row(self.table)
        if not row:
            info(self, "Select a transaction first.")
            return
        if row[6] != "Successful":
            info(self, "Failed transactions were rolled back, so they have no allocations.")
            return
        ReceiptDialog(self.p, row[0]).exec_()
