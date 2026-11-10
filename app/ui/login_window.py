"""Screen 1 (Login) and Screen 2 (Citizen self-registration) in one window
with a QStackedWidget, matching LoginWindow.ui in the proposal."""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
                             QLineEdit, QMainWindow, QPushButton, QStackedWidget,
                             QVBoxLayout, QWidget)

from app.db import DBError
from app.ui.ui_common import error, info, secondary


class LoginWindow(QMainWindow):
    logged_in = pyqtSignal(dict)        # {accountId, username, role, ...}

    def __init__(self, database):
        super().__init__()
        self.db = database
        self.setWindowTitle("PUUMS - Login")
        self.resize(520, 640)
        self.stack = QStackedWidget()
        self.stack.addWidget(self._login_page())
        self.stack.addWidget(self._register_page())
        self.setCentralWidget(self.stack)

    # ------------------------------------------------------------- Screen 1
    def _login_page(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(50, 40, 50, 40)
        head = QLabel("PUUMS")
        head.setObjectName("title")
        head.setAlignment(Qt.AlignCenter)
        sub = QLabel("Pakistan Unified Utility Management System\nPilot region: Karachi")
        sub.setObjectName("muted")
        sub.setAlignment(Qt.AlignCenter)
        lay.addStretch()
        lay.addWidget(head)
        lay.addWidget(sub)
        lay.addSpacing(30)

        form = QFormLayout()
        self.username = QLineEdit()
        self.username.setPlaceholderText("42101-1234567-1  or  name@puums.pk")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.returnPressed.connect(self.do_login)
        form.addRow("CNIC / Email", self.username)
        form.addRow("Password", self.password)
        lay.addLayout(form)
        lay.addSpacing(10)

        login = QPushButton("LOGIN")
        login.clicked.connect(self.do_login)
        reg = secondary(QPushButton("Don't have an account? Register"))
        reg.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        lay.addWidget(login)
        lay.addWidget(reg)
        hint = QLabel("No role dropdown: the portal is chosen from UserAccount.role")
        hint.setObjectName("muted")
        hint.setAlignment(Qt.AlignCenter)
        lay.addWidget(hint)
        lay.addStretch()
        return page

    def do_login(self):
        try:
            row = self.db.one(
                "SELECT accountId, username, role FROM UserAccount "
                "WHERE username = %s AND passwordHash = SHA2(%s, 256)",
                (self.username.text().strip(), self.password.text()))
            if not row:
                error(self, "Invalid CNIC/email or password.")
                return
            account_id, username, role = row
            self.db.execute("UPDATE UserAccount SET lastLogin = NOW() WHERE accountId = %s",
                            (account_id,))
            user = {"accountId": account_id, "username": username, "role": role}
            if role == "Citizen":
                cnic, first, last = self.db.one(
                    "SELECT cnic, firstName, lastName FROM Citizen WHERE accountId = %s",
                    (account_id,))
                user.update(cnic=cnic, name=f"{first} {last}")
            else:
                emp = self.db.one(
                    "SELECT employeeId, name, role, providerId, regionId FROM Employee "
                    "WHERE accountId = %s", (account_id,))
                user.update(employeeId=emp[0], name=emp[1], jobRole=emp[2],
                            providerId=emp[3], regionId=emp[4])
            self.password.clear()
            self.logged_in.emit(user)
        except DBError as e:
            error(self, e)

    # ------------------------------------------------------------- Screen 2
    def _register_page(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(40, 20, 40, 20)
        head = QLabel("REGISTER")
        head.setObjectName("title")
        head.setAlignment(Qt.AlignCenter)
        lay.addWidget(head)

        self.reg = {}
        details = QGroupBox("Enter Details")
        f1 = QFormLayout(details)
        for key, label, ph in [("first", "First Name", ""), ("last", "Last Name", ""),
                               ("cnic", "CNIC", "42101-1234567-1"),
                               ("phone", "Phone Number", "0300-1234567"),
                               ("email", "Email", ""), ("pw", "Password", "")]:
            w = QLineEdit()
            w.setPlaceholderText(ph)
            if key == "pw":
                w.setEchoMode(QLineEdit.Password)
            self.reg[key] = w
            f1.addRow(label, w)
        self.reg["cnic"].setInputMask("99999-9999999-9;_")

        address = QGroupBox("Enter Address (primary premise)")
        f2 = QFormLayout(address)
        for key, label in [("house", "House No"), ("street", "Street"), ("area", "Area")]:
            self.reg[key] = QLineEdit()
            f2.addRow(label, self.reg[key])
        self.region = QComboBox()
        self.ptype = QComboBox()
        self.ptype.addItems(["Residential", "Commercial"])
        f2.addRow("Region", self.region)
        f2.addRow("Premise Type", self.ptype)

        lay.addWidget(details)
        lay.addWidget(address)
        row = QHBoxLayout()
        back = secondary(QPushButton("Back To Login"))
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        create = QPushButton("Create Account")
        create.clicked.connect(self.do_register)
        row.addWidget(back)
        row.addStretch()
        row.addWidget(create)
        lay.addLayout(row)
        self.stack.currentChanged.connect(self._load_regions)
        return page

    def _load_regions(self, idx):
        if idx != 1:
            return
        self.region.clear()
        _, rows = self.db.query("SELECT regionId, regionName FROM Region ORDER BY regionName")
        for rid, name in rows:
            self.region.addItem(name, rid)

    def do_register(self):
        v = {k: w.text().strip() for k, w in self.reg.items()}
        if not all([v["first"], v["last"], v["cnic"], v["pw"], v["house"], v["street"], v["area"]]):
            error(self, "Please fill in name, CNIC, password and address.")
            return
        try:
            self.db.call("CALL sp_RegisterCitizen(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                         (v["cnic"], v["first"], v["last"], v["phone"], v["email"] or None,
                          v["pw"], v["house"], v["street"], v["area"],
                          self.region.currentData(), self.ptype.currentText()))
            info(self, "Account created. You can now log in with your CNIC.")
            self.username.setText(v["cnic"])
            for w in self.reg.values():
                w.clear()
            self.stack.setCurrentIndex(0)
        except DBError as e:
            error(self, e)
