from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QMainWindow, QPushButton, QTabWidget,
                             QVBoxLayout, QWidget)

from ui_common import SqlLogDock, secondary


class PortalWindow(QMainWindow):
    logout = pyqtSignal()

    def __init__(self, database, user, portal_name):
        super().__init__()
        self.db = database
        self.user = user
        self.setWindowTitle(f"PUUMS - {portal_name}")
        self.resize(1280, 860)

        central = QWidget()
        lay = QVBoxLayout(central)
        top = QHBoxLayout()
        brand = QLabel(f"<b>PUUMS</b> &nbsp;·&nbsp; {portal_name}")
        who = QLabel(f"{user.get('name', user['username'])}  ({user['role']})")
        who.setObjectName("muted")
        self.sql_btn = secondary(QPushButton("Hide SQL"))
        self.sql_btn.clicked.connect(self._toggle_sql)
        out = secondary(QPushButton("Log out"))
        out.clicked.connect(self._logout)
        top.addWidget(brand)
        top.addStretch()
        top.addWidget(who)
        top.addWidget(self.sql_btn)
        top.addWidget(out)
        lay.addLayout(top)

        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self._tab_changed)
        lay.addWidget(self.tabs)
        self.setCentralWidget(central)

        self.sql_dock = SqlLogDock(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.sql_dock)
        self.resizeDocks([self.sql_dock], [220], Qt.Vertical)

    def _toggle_sql(self):
        vis = not self.sql_dock.isVisible()
        self.sql_dock.setVisible(vis)
        self.sql_btn.setText("Hide SQL" if vis else "Show SQL")

    def _tab_changed(self, idx):
        w = self.tabs.widget(idx)
        if hasattr(w, "refresh"):
            w.refresh()

    def _logout(self):
        self.logout.emit()
        self.close()
