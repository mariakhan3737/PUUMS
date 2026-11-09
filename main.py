"""PUUMS desktop app entry point:   python app/main.py"""
import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

from admin_portal import AdminPortal
from citizen_portal import CitizenPortal
from db import Database
from employee_portal import EmployeePortal
from login_window import LoginWindow
from ui_common import STYLE


class App:
    def __init__(self):
        self.qt = QApplication(sys.argv)
        self.qt.setStyleSheet(STYLE)
        try:
            self.db = Database()
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(None, "Cannot connect to MySQL",
                                 f"{e}\n\nCheck config.py and run setup_db.py first.")
            sys.exit(1)
        self.login = LoginWindow(self.db)
        self.login.logged_in.connect(self.open_portal)
        self.portal = None
        self.login.show()

    def open_portal(self, user):
        role = user["role"]
        cls = {"Citizen": CitizenPortal, "Employee": EmployeePortal,
               "Admin": AdminPortal, "Super-Admin": AdminPortal}[role]
        self.portal = cls(self.db, user)
        self.portal.logout.connect(self.login.show)
        self.login.hide()
        self.portal.show()

    def run(self):
        return self.qt.exec_()


if __name__ == "__main__":
    sys.exit(App().run())
