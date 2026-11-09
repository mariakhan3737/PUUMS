"""Shared widgets: styled tables, the SQL log panel, placeholders, helpers."""
import datetime
from decimal import Decimal

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QAbstractItemView, QDockWidget, QFrame, QHBoxLayout,
                             QHeaderView, QLabel, QMessageBox, QPlainTextEdit,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget)

import db

STYLE = """
QWidget { font-family: 'Segoe UI', 'Noto Sans', Arial; font-size: 10pt; color: #1f2933; }
QMainWindow, QDialog { background: #f5f6f8; }
QTabWidget::pane { border: 1px solid #d9dde3; background: white; border-radius: 4px; }
QTabBar::tab { padding: 8px 14px; background: #e9ecf0; border: 1px solid #d9dde3;
               border-bottom: none; margin-right: 2px; }
QTabBar::tab:selected { background: white; color: #4a2a6b; font-weight: 600; }
QLabel#title { font-size: 15pt; font-weight: 700; color: #4a2a6b; }
QLabel#kpi   { font-size: 16pt; font-weight: 700; color: #4a2a6b; }
QLabel#muted { color: #6b7280; }
QPushButton { background: #4a2a6b; color: white; border: none; padding: 7px 14px;
              border-radius: 4px; }
QPushButton:hover { background: #5d3a85; }
QPushButton:disabled { background: #b8adc6; }
QPushButton[secondary="true"] { background: #e9ecf0; color: #1f2933; }
QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox, QPlainTextEdit {
    padding: 5px; border: 1px solid #c9ced6; border-radius: 4px; background: white; }
QTableWidget { gridline-color: #e5e7eb; background: white;
               selection-background-color: #e7dcf3; selection-color: #1f2933; }
QHeaderView::section { background: #eef0f3; padding: 5px; border: none;
                       border-bottom: 1px solid #d9dde3; font-weight: 600; }
QGroupBox { font-weight: 600; border: 1px solid #d9dde3; border-radius: 4px;
            margin-top: 10px; padding-top: 12px; background: white; }
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
QFrame#card { background: white; border: 1px solid #d9dde3; border-radius: 6px; }
"""


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
        font = QFont("Consolas")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(9)
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
