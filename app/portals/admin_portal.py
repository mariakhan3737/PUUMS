"""AdminPortal: Screens 9, 10, 11, 18. Screens 12 and 17 are placeholders."""
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QComboBox, QDateEdit, QDoubleSpinBox, QFormLayout, QGridLayout,
                             QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit,
                             QProgressBar, QPushButton, QSplitter, QTableWidgetItem,
                             QVBoxLayout, QWidget)

from app.db import DBError
from app.portals.portal_base import PortalWindow
from app.ui.ui_common import (PlaceholderTab, error, fill_table, fmt, info, kpi_card, make_table,
                       secondary, selected_row, title)


class AdminPortal(PortalWindow):
    def __init__(self, database, user):
        super().__init__(database, user, "Admin Portal")
        self.analytics = AnalyticsTab(self)
        self.tabs.addTab(self.analytics, "Analytics")
        self.tabs.addTab(TariffTab(self), "Tariff Management")
        self.tabs.addTab(ProviderRegionTab(self), "Provider && Region Setup")
        self.tabs.addTab(PlaceholderTab(12, "Fleet & Staff Configuration",
                         ["sp_ProvisionEmployee (UserAccount + Employee in one transaction)",
                          "Tanker table (capacityTier → TankerRate, driverId → Employee)"]),
                         "Fleet && Staff Configuration")
        self.tabs.addTab(PlaceholderTab(17, "Tanker Rate Configuration",
                         ["TankerRate (capacityTier, baseFlatRate, urgencySurcharge, effectiveDate)"]),
                         "Tanker Rate Configuration")
        self.tabs.addTab(BillingTab(self), "Monthly Billing Cycle")
        self.analytics.refresh()


def month_picker(default):
    d = QDateEdit(default)
    d.setDisplayFormat("MMM yyyy")
    d.setCalendarPopup(True)
    return d


def first_of(qdate):
    return f"{qdate.year()}-{qdate.month():02d}-01"


# ======================================================================
# Screen 9 - Operational Analytics Dashboard (views)
# ======================================================================
class AnalyticsTab(QWidget):
    def __init__(self, portal):
        super().__init__()
        self.p = portal
        lay = QVBoxLayout(self)
        lay.addLayout(title("Operational Analytics Dashboard",
                            "All figures come from SQL views: vw_CollectionEfficiency, "
                            "vw_OutstandingDebt, vw_RegionalConsumption"))
        f = QHBoxLayout()
        self.month = month_picker(QDate(2026, 9, 1))
        self.month.dateChanged.connect(self.refresh)
        f.addWidget(QLabel("Billing month"))
        f.addWidget(self.month)
        f.addStretch()
        lay.addLayout(f)
        grid = QGridLayout()
        cards = {}
        for i, (key, cap) in enumerate([("billed", "Amount billed (Rs.)"),
                                        ("collected", "Revenue collected (Rs.)"),
                                        ("eff", "Collection efficiency"),
                                        ("outstanding", "Outstanding receivables, all months (Rs.)")]):
            frame, cards[key] = kpi_card(cap)
            grid.addWidget(frame, 0, i)
        self.cards = cards
        lay.addLayout(grid)
        split = QSplitter(Qt.Vertical)
        w1 = QWidget()
        l1 = QVBoxLayout(w1)
        l1.addWidget(QLabel("<b>Regional consumption heatmap</b> (units)"))
        self.heat = make_table()
        l1.addWidget(self.heat)
        w2 = QWidget()
        l2 = QVBoxLayout(w2)
        l2.addWidget(QLabel("<b>Outstanding debt by provider and region</b>"))
        self.debt = make_table()
        l2.addWidget(self.debt)
        split.addWidget(w1)
        split.addWidget(w2)
        lay.addWidget(split)

    def refresh(self):
        m = first_of(self.month.date())
        db = self.p.db
        try:
            b, c = db.one("SELECT COALESCE(SUM(amountBilled),0), COALESCE(SUM(amountCollected),0) "
                          "FROM vw_CollectionEfficiency WHERE billingMonth = %s", (m,))
            out = db.one("SELECT COALESCE(SUM(amountOutstanding),0) FROM vw_OutstandingDebt")[0]
            _, heat = db.query("SELECT regionName, electricityUnits, gasUnits, waterUnits "
                               "FROM vw_RegionalConsumption WHERE readingMonth = %s "
                               "ORDER BY regionName", (m,))
            _, debt = db.query("SELECT providerName, regionName, unpaidBills, amountOutstanding, "
                               "oldestDueDate FROM vw_OutstandingDebt ORDER BY amountOutstanding DESC")
        except DBError as e:
            error(self, e)
            return
        self.cards["billed"].setText(fmt(b))
        self.cards["collected"].setText(fmt(c))
        self.cards["eff"].setText(f"{(100 * c / b):.1f}%" if b else "-")
        self.cards["outstanding"].setText(fmt(out))
        fill_table(self.heat, ["Region", "Electricity", "Gas", "Piped Water"], heat)
        for col in (1, 2, 3):                        # colour cells by intensity
            vals = [float(r[col]) for r in heat]
            hi = max(vals) if vals and max(vals) > 0 else 1
            for r, v in enumerate(vals):
                a = int(40 + 160 * v / hi) if v else 0
                self.heat.item(r, col).setBackground(QColor(74, 42, 107, a))
        fill_table(self.debt, ["Provider", "Region", "Unpaid Bills", "Amount Outstanding (Rs.)",
                               "Oldest Due Date"], debt)


# ======================================================================
# Screen 10 - Tariff Management (Setup Screen 1)
# ======================================================================
class TariffTab(QWidget):
    def __init__(self, portal):
        super().__init__()
        self.p = portal
        self.current_tariff = None
        lay = QVBoxLayout(self)
        lay.addLayout(title("Tariff Management",
                            "NEPRA-style slab tariffs per provider + category; new rates are added "
                            "with a new effective date so history is preserved"))
        split = QSplitter(Qt.Horizontal)

        left = QWidget()
        ll = QVBoxLayout(left)
        self.filter = QComboBox()
        self.filter.currentIndexChanged.connect(self.load_list)
        ll.addWidget(self.filter)
        self.table = make_table()
        self.table.itemSelectionChanged.connect(self.load_selected)
        ll.addWidget(self.table)
        split.addWidget(left)

        right = QWidget()
        rl = QVBoxLayout(right)
        box = QGroupBox("Tariff")
        f = QFormLayout(box)
        self.provider = QComboBox()
        self.category = QComboBox()
        self.category.addItems(["Residential", "Commercial"])
        self.effective = QDateEdit(QDate.currentDate())
        self.effective.setCalendarPopup(True)
        self.effective.setDisplayFormat("dd MMM yyyy")
        self.fixed, self.fpa, self.gst = QDoubleSpinBox(), QDoubleSpinBox(), QDoubleSpinBox()
        for s in (self.fixed, self.fpa, self.gst):
            s.setRange(0, 100000)
            s.setDecimals(2)
        self.gst.setMaximum(100)
        f.addRow("Provider", self.provider)
        f.addRow("Category", self.category)
        f.addRow("Effective date", self.effective)
        f.addRow("Fixed charges (Rs.)", self.fixed)
        f.addRow("FPA (Rs./unit)", self.fpa)
        f.addRow("GST %", self.gst)
        rl.addWidget(box)
        sbox = QGroupBox("Slabs  (leave Max empty for 'and above')")
        sl = QVBoxLayout(sbox)
        self.slabs = make_table(["Min units", "Max units", "Rate (Rs./unit)"])
        self.slabs.setEditTriggers(self.slabs.AllEditTriggers)
        sl.addWidget(self.slabs)
        sb = QHBoxLayout()
        add = secondary(QPushButton("+ slab"))
        add.clicked.connect(lambda: self.slabs.insertRow(self.slabs.rowCount()))
        rem = secondary(QPushButton("- slab"))
        rem.clicked.connect(lambda: self.slabs.removeRow(self.slabs.rowCount() - 1))
        sb.addWidget(add)
        sb.addWidget(rem)
        sb.addStretch()
        sl.addLayout(sb)
        rl.addWidget(sbox)
        btns = QHBoxLayout()
        for text, fn in [("ADD", self.add), ("UPDATE", self.update), ("DELETE", self.delete),
                         ("Clear", self.clear)]:
            b = QPushButton(text) if text != "Clear" else secondary(QPushButton(text))
            b.clicked.connect(fn)
            btns.addWidget(b)
        rl.addLayout(btns)
        split.addWidget(right)
        split.setSizes([700, 450])
        lay.addWidget(split)

    def refresh(self):
        _, provs = self.p.db.query("SELECT providerId, providerName FROM Provider ORDER BY providerId")
        self.filter.blockSignals(True)
        self.filter.clear()
        self.filter.addItem("All providers", None)
        self.provider.clear()
        for pid, name in provs:
            self.filter.addItem(name, pid)
            self.provider.addItem(name, pid)
        self.filter.blockSignals(False)
        self.load_list()

    def load_list(self):
        pid = self.filter.currentData()
        try:
            _, rows = self.p.db.query(
                "SELECT t.tariffId, pr.providerName, t.consumerCategory, s.slabNumber, s.minUnits, "
                "       s.maxUnits, s.ratePerUnit, t.fixedCharges, t.fpaRate, t.gstPercent, t.effectiveDate "
                "FROM Tariff t JOIN TariffSlab s ON s.tariffId = t.tariffId "
                "JOIN Provider pr ON pr.providerId = t.providerId "
                "WHERE (%s IS NULL OR t.providerId = %s) "
                "ORDER BY pr.providerName, t.consumerCategory, t.effectiveDate DESC, s.slabNumber",
                (pid, pid))
        except DBError as e:
            error(self, e)
            return
        fill_table(self.table, ["Tariff", "Provider", "Category", "Slab", "Min", "Max", "Rate",
                                "Fixed", "FPA", "GST %", "Effective"], rows)

    def load_selected(self):
        row = selected_row(self.table)
        if not row:
            return
        tid = row[0]
        h = self.p.db.one("SELECT providerId, consumerCategory, effectiveDate, fixedCharges, fpaRate, "
                          "gstPercent FROM Tariff WHERE tariffId = %s", (tid,))
        _, slabs = self.p.db.query("SELECT minUnits, maxUnits, ratePerUnit FROM TariffSlab "
                                   "WHERE tariffId = %s ORDER BY slabNumber", (tid,))
        self.current_tariff = tid
        self.provider.setCurrentIndex(self.provider.findData(h[0]))
        self.category.setCurrentText(h[1])
        self.effective.setDate(QDate(h[2].year, h[2].month, h[2].day))
        self.fixed.setValue(float(h[3]))
        self.fpa.setValue(float(h[4]))
        self.gst.setValue(float(h[5]))
        self.slabs.setRowCount(len(slabs))
        for r, s in enumerate(slabs):
            for c, v in enumerate(s):
                self.slabs.setItem(r, c, QTableWidgetItem("" if v is None else str(v)))

    def _slab_values(self):
        out = []
        for r in range(self.slabs.rowCount()):
            cells = [self.slabs.item(r, c).text().strip() if self.slabs.item(r, c) else ""
                     for c in range(3)]
            if not any(cells):
                continue
            try:
                out.append((int(cells[0]), int(cells[1]) if cells[1] else None, float(cells[2])))
            except ValueError:
                raise DBError(f"Slab row {r + 1}: min/max must be whole numbers and rate a number")
        if not out:
            raise DBError("Add at least one slab")
        return out

    def _header(self):
        d = self.effective.date()
        return (self.category.currentText(), self.fixed.value(), self.fpa.value(), self.gst.value(),
                f"{d.year()}-{d.month():02d}-{d.day():02d}", self.provider.currentData())

    def add(self):
        try:
            slabs = self._slab_values()
            stmts = [("INSERT INTO Tariff (consumerCategory, fixedCharges, fpaRate, gstPercent, "
                      "effectiveDate, providerId) VALUES (%s, %s, %s, %s, %s, %s)", self._header())]
            for i, (mn, mx, rate) in enumerate(slabs, 1):
                stmts.append(("INSERT INTO TariffSlab (tariffId, slabNumber, minUnits, maxUnits, ratePerUnit) "
                              "VALUES (LAST_INSERT_ID(), %s, %s, %s, %s)", (i, mn, mx, rate)))
            self.p.db.transaction(stmts)
            info(self, "Tariff added.")
            self.load_list()
        except DBError as e:
            error(self, e)

    def update(self):
        if not self.current_tariff:
            info(self, "Select a tariff row first.")
            return
        try:
            slabs = self._slab_values()
            tid = self.current_tariff
            stmts = [("UPDATE Tariff SET consumerCategory=%s, fixedCharges=%s, fpaRate=%s, gstPercent=%s, "
                      "effectiveDate=%s, providerId=%s WHERE tariffId=%s", self._header() + (tid,)),
                     ("DELETE FROM TariffSlab WHERE tariffId = %s", (tid,))]
            for i, (mn, mx, rate) in enumerate(slabs, 1):
                stmts.append(("INSERT INTO TariffSlab (tariffId, slabNumber, minUnits, maxUnits, ratePerUnit) "
                              "VALUES (%s, %s, %s, %s, %s)", (tid, i, mn, mx, rate)))
            self.p.db.transaction(stmts)
            info(self, "Tariff updated.")
            self.load_list()
        except DBError as e:
            error(self, e)

    def delete(self):
        if not self.current_tariff:
            info(self, "Select a tariff row first.")
            return
        try:
            self.p.db.execute("DELETE FROM Tariff WHERE tariffId = %s", (self.current_tariff,))
            self.clear()
            self.load_list()
        except DBError as e:
            error(self, e)

    def clear(self):
        self.current_tariff = None
        self.table.clearSelection()
        self.slabs.setRowCount(1)
        for c in range(3):
            self.slabs.setItem(0, c, QTableWidgetItem(""))
        for s in (self.fixed, self.fpa, self.gst):
            s.setValue(0)


# ======================================================================
# Screen 11 - Provider & Region Setup (Setup Screen 2)
# ======================================================================
class ProviderRegionTab(QWidget):
    def __init__(self, portal):
        super().__init__()
        self.p = portal
        lay = QVBoxLayout(self)
        lay.addLayout(title("Provider & Region Setup"))

        pbox = QGroupBox("Utility providers")
        pl = QVBoxLayout(pbox)
        pf = QHBoxLayout()
        self.p_name, self.p_phone, self.p_dept = QLineEdit(), QLineEdit(), QLineEdit()
        self.p_type = QComboBox()
        self.p_type.addItems(["Electricity", "Gas", "Piped Water"])
        for w, ph in [(self.p_name, "Provider name"), (self.p_phone, "Contact phone"),
                      (self.p_dept, "Department")]:
            w.setPlaceholderText(ph)
        for w in (self.p_name, self.p_type, self.p_phone, self.p_dept):
            pf.addWidget(w)
        pl.addLayout(pf)
        pl.addLayout(self._buttons(self.add_provider, self.update_provider, self.delete_provider))
        self.ptable = make_table()
        self.ptable.itemSelectionChanged.connect(self.pick_provider)
        pl.addWidget(self.ptable)
        lay.addWidget(pbox)

        rbox = QGroupBox("Operating regions")
        rl = QVBoxLayout(rbox)
        rf = QHBoxLayout()
        self.r_name, self.r_city, self.r_prov = QLineEdit(), QLineEdit("Karachi"), QLineEdit("Sindh")
        self.r_name.setPlaceholderText("Region name")
        for w in (self.r_name, self.r_city, self.r_prov):
            rf.addWidget(w)
        rl.addLayout(rf)
        rl.addLayout(self._buttons(self.add_region, self.update_region, self.delete_region))
        self.rtable = make_table()
        self.rtable.itemSelectionChanged.connect(self.pick_region)
        rl.addWidget(self.rtable)
        lay.addWidget(rbox)

    @staticmethod
    def _buttons(add, upd, dele):
        row = QHBoxLayout()
        for text, fn in [("ADD", add), ("UPDATE", upd), ("DELETE", dele)]:
            b = QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        return row

    def refresh(self):
        try:
            _, provs = self.p.db.query(
                "SELECT pr.providerId, pr.providerName, pr.utilityType, pr.contactPhone, pr.department, "
                "       COUNT(sc.connectionId) AS connections "
                "FROM Provider pr LEFT JOIN ServiceConnection sc ON sc.providerId = pr.providerId "
                "GROUP BY pr.providerId, pr.providerName, pr.utilityType, pr.contactPhone, pr.department "
                "ORDER BY pr.providerId")
            _, regs = self.p.db.query(
                "SELECT r.regionId, r.regionName, r.city, r.province, COUNT(p.premiseId) AS premises "
                "FROM Region r LEFT JOIN Premise p ON p.regionId = r.regionId "
                "GROUP BY r.regionId, r.regionName, r.city, r.province ORDER BY r.regionId")
        except DBError as e:
            error(self, e)
            return
        fill_table(self.ptable, ["ID", "Provider", "Utility", "Contact", "Department", "Connections"], provs)
        fill_table(self.rtable, ["ID", "Region", "City", "Province", "Premises"], regs)

    def pick_provider(self):
        row = selected_row(self.ptable)
        if row:
            self.p_name.setText(row[1])
            self.p_type.setCurrentText(row[2])
            self.p_phone.setText(row[3] or "")
            self.p_dept.setText(row[4] or "")

    def pick_region(self):
        row = selected_row(self.rtable)
        if row:
            self.r_name.setText(row[1])
            self.r_city.setText(row[2])
            self.r_prov.setText(row[3])

    def _run(self, sql, params):
        try:
            self.p.db.execute(sql, params)
            self.refresh()
        except DBError as e:
            error(self, e)

    def _pvals(self):
        return (self.p_name.text().strip(), self.p_type.currentText(),
                self.p_phone.text().strip(), self.p_dept.text().strip())

    def add_provider(self):
        self._run("INSERT INTO Provider (providerName, utilityType, contactPhone, department) "
                  "VALUES (%s, %s, %s, %s)", self._pvals())

    def update_provider(self):
        row = selected_row(self.ptable)
        if row:
            self._run("UPDATE Provider SET providerName=%s, utilityType=%s, contactPhone=%s, "
                      "department=%s WHERE providerId=%s", self._pvals() + (row[0],))

    def delete_provider(self):
        row = selected_row(self.ptable)
        if row:   # FK from ServiceConnection/Tariff/Employee blocks deleting a provider in use
            self._run("DELETE FROM Provider WHERE providerId = %s", (row[0],))

    def _rvals(self):
        return (self.r_name.text().strip(), self.r_city.text().strip(), self.r_prov.text().strip())

    def add_region(self):
        self._run("INSERT INTO Region (regionName, city, province) VALUES (%s, %s, %s)", self._rvals())

    def update_region(self):
        row = selected_row(self.rtable)
        if row:
            self._run("UPDATE Region SET regionName=%s, city=%s, province=%s WHERE regionId=%s",
                      self._rvals() + (row[0],))

    def delete_region(self):
        row = selected_row(self.rtable)
        if row:
            self._run("DELETE FROM Region WHERE regionId = %s", (row[0],))


# ======================================================================
# Screen 18 - Monthly Billing Cycle (stored procedure execution)
# ======================================================================
class BillingTab(QWidget):
    def __init__(self, portal):
        super().__init__()
        self.p = portal
        lay = QVBoxLayout(self)
        lay.addLayout(title("Execute Monthly Billing Cycle",
                            "CALL sp_GenerateMonthlyBills → sp_CalculateCascadingTariff per connection"))
        f = QHBoxLayout()
        self.month = month_picker(QDate(2026, 10, 1))
        self.provider = QComboBox()
        run = QPushButton("Execute Billing Procedure")
        run.clicked.connect(self.run)
        f.addWidget(QLabel("Month"))
        f.addWidget(self.month)
        f.addWidget(QLabel("Provider"))
        f.addWidget(self.provider)
        f.addWidget(run)
        f.addStretch()
        lay.addLayout(f)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        lay.addWidget(self.progress)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(220)
        lay.addWidget(self.log)
        lay.addWidget(QLabel("<b>Billing history</b>"))
        self.history = make_table()
        lay.addWidget(self.history)

    def refresh(self):
        _, provs = self.p.db.query("SELECT providerId, providerName FROM Provider ORDER BY providerId")
        self.provider.clear()
        self.provider.addItem("All", None)
        for pid, name in provs:
            self.provider.addItem(name, pid)
        self.load_history()

    def load_history(self):
        _, rows = self.p.db.query(
            "SELECT DATE_FORMAT(br.billingMonth, '%b %Y'), COALESCE(pr.providerName, 'All'), "
            "       br.billsGenerated, br.billsSkipped, br.billsFailed, br.runBy, br.runAt "
            "FROM BillingRun br LEFT JOIN Provider pr ON pr.providerId = br.providerId "
            "ORDER BY br.runAt DESC")
        fill_table(self.history, ["Month", "Provider", "Generated", "Skipped", "Failed",
                                  "Run By", "Run At"], rows)

    def run(self):
        self.progress.setValue(10)
        try:
            rows, (g, s, f) = self.p.db.call(
                "CALL sp_GenerateMonthlyBills(%s, %s, %s, @g, @s, @f)",
                (first_of(self.month.date()), self.provider.currentData(), self.p.user["username"]),
                out_vars=("@g", "@s", "@f"))
        except DBError as e:
            self.progress.setValue(0)
            error(self, e)
            return
        self.progress.setValue(100)
        self.log.setPlainText("\n".join(r[0] for r in rows))
        self.load_history()
