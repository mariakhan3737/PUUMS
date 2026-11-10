"""Shared widgets: styled tables, the SQL log panel, placeholders, helpers."""
import datetime
from decimal import Decimal

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QAbstractItemView, QDockWidget, QFrame, QHBoxLayout,
                             QHeaderView, QLabel, QMessageBox, QPlainTextEdit,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget)

from app import db
from app.ui.xp_style import XP_STYLE

STYLE = XP_STYLE


def fmt(value):
    if value is None:
        return "-"
    if isinstance(value, Decimal):
        return f"{value:,.2f}".rstrip("0").rstrip(".") if value % 1 else f"{value:,.0f}"
    if isinstance(value, datetime.datetime):
        return value.strftime("%d %b %Y %H:%M")
    if isinstance(value, datetime.date):
        return value.strftime("%d %b %Y")
    return str(value)


def make_table(headers=None):
    t = QTableWidget()
    t.setEditTriggers(QAbstractItemView.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectRows)
    t.setSelectionMode(QAbstractItemView.SingleSelection)
    t.setAlternatingRowColors(True)
    t.verticalHeader().setVisible(False)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    if headers:
        t.setColumnCount(len(headers))
        t.setHorizontalHeaderLabels(headers)
    return t


def fill_table(table, headers, rows, hidden=()):
    """Fill a table; rows' raw tuples are kept in each first cell's UserRole."""
    table.clear()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, val in enumerate(row[:len(headers)]):
            item = QTableWidgetItem(fmt(val))
            if isinstance(val, (int, float, Decimal)) and not isinstance(val, bool):
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if c == 0:
                item.setData(Qt.UserRole, row)
            table.setItem(r, c, item)
    for c in hidden:
        table.setColumnHidden(c, True)


def selected_row(table):
    r = table.currentRow()
    if r < 0 or table.item(r, 0) is None:
        return None
    return table.item(r, 0).data(Qt.UserRole)


def title(text, sub=None):
    box = QVBoxLayout()
    lbl = QLabel(text)
    lbl.setObjectName("title")
    box.addWidget(lbl)
    if sub:
        s = QLabel(sub)
        s.setObjectName("muted")
        box.addWidget(s)
    return box


def kpi_card(caption):
    frame = QFrame()
    frame.setObjectName("card")
    lay = QVBoxLayout(frame)
    value = QLabel("-")
    value.setObjectName("kpi")
    cap = QLabel(caption)
    cap.setObjectName("muted")
    lay.addWidget(value)
    lay.addWidget(cap)
    return frame, value


def error(parent, msg):
    QMessageBox.critical(parent, "Database rejected the operation", str(msg))


def info(parent, msg):
    QMessageBox.information(parent, "PUUMS", str(msg))


def secondary(btn):
    btn.setProperty("secondary", True)
    return btn


class PlaceholderTab(QWidget):
    """Tab for a screen scheduled for the final milestone."""

    def __init__(self, screen, name, sql_objects):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addLayout(title(name, f"Screen {screen} - UI scheduled for the final milestone"))
        note = QLabel("Database objects already built and testable in MySQL:\n\n  • "
                      + "\n  • ".join(sql_objects))
        note.setObjectName("muted")
        note.setAlignment(Qt.AlignTop)
        lay.addWidget(note)
        lay.addStretch()


class SqlLogDock(QDockWidget):
    """Bottom panel that shows every SQL statement the app executes."""

    def __init__(self, parent):
        super().__init__("SQL executed by this screen", parent)
        body = QWidget()
        lay = QVBoxLayout(body)
        lay.setContentsMargins(4, 4, 4, 4)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        font = QFont("Lucida Console")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(8)
        self.text.setFont(font)
        bar = QHBoxLayout()
        clear = secondary(QPushButton("Clear"))
        clear.clicked.connect(self.text.clear)
        bar.addStretch()
        bar.addWidget(clear)
        lay.addWidget(self.text)
        lay.addLayout(bar)
        self.setWidget(body)
        db.on_sql(self.append)

    def append(self, text):
        try:
            self.text.appendPlainText(text)
        except RuntimeError:          # window already closed (after logout)
            return
        self.text.verticalScrollBar().setValue(self.text.verticalScrollBar().maximum())
