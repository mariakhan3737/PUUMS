"""Windows XP Luna Blue theme — pure QSS, no layout changes.

Every widget keeps its position; only colours, borders, gradients and fonts
are changed to replicate the Windows XP "Luna" look (the default blue theme
shipped with Windows XP, 2001-2007).

References used while authoring:
  • Default XP Luna colours extracted from uxtheme msstyles
  • Tahoma 8 pt was the system font on Windows XP
"""

XP_STYLE = """

/* ================================================================
   GLOBAL  – Tahoma 8pt, warm beige XP background
   ================================================================ */
QWidget {
    font-family: 'Tahoma', 'MS Sans Serif', Arial;
    font-size: 8pt;
    color: #000000;
}
QMainWindow, QDialog {
    background: #ece9d8;
}

/* ================================================================
   BUTTONS  – the iconic 3-D "plastic" look
   ================================================================ */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0   #ffffff,
                    stop:0.05 #e3f1fc,
                    stop:0.45 #c5dcf0,
                    stop:0.50 #b5d2ec,
                    stop:1   #97c4e8);
    border: 1px solid #003c74;
    border-radius: 3px;
    padding: 4px 16px;
    color: #000000;
    min-height: 18px;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0   #fffce6,
                    stop:0.05 #fff0c9,
                    stop:0.45 #fce49c,
                    stop:0.50 #fad56c,
                    stop:1   #f7c740);
    border: 1px solid #b5730f;
}
QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0   #90b8da,
                    stop:0.45 #7ba4cc,
                    stop:0.50 #6e96bf,
                    stop:1   #5d87b0);
    border: 1px solid #003c74;
    padding-top: 5px;
    padding-left: 17px;
}
QPushButton:disabled {
    background: #ece9d8;
    border: 1px solid #aca899;
    color: #848484;
}
QPushButton:focus {
    border: 1px solid #003c74;
    outline: 1px dotted #000000;
    outline-offset: -3px;
}

/* Secondary / flat buttons keep the classic XP "standard button" look */
QPushButton[secondary="true"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0   #ffffff,
                    stop:0.45 #f0efe3,
                    stop:0.50 #e2dfd2,
                    stop:1   #d4d0c8);
    border: 1px solid #808080;
    color: #000000;
}
QPushButton[secondary="true"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0   #fffce6,
                    stop:0.05 #fff0c9,
                    stop:0.45 #fce49c,
                    stop:0.50 #fad56c,
                    stop:1   #f7c740);
    border: 1px solid #b5730f;
}
QPushButton[secondary="true"]:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0   #d4d0c8,
                    stop:0.50 #cac5ba,
                    stop:1   #bfbaa8);
    border: 1px solid #808080;
}

/* ================================================================
   INPUT FIELDS  – sunken inset, blue-grey border
   ================================================================ */
QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox, QPlainTextEdit {
    background: #ffffff;
    border: 2px inset #7f9db9;
    border-top-color: #7f9db9;
    border-left-color: #7f9db9;
    border-bottom-color: #f0f0f0;
    border-right-color: #f0f0f0;
    padding: 2px 4px;
    border-radius: 0px;
    selection-background-color: #316ac5;
    selection-color: #ffffff;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus,
QDoubleSpinBox:focus, QSpinBox:focus, QPlainTextEdit:focus {
    border: 2px inset #0054e3;
}

/* Combo dropdown */
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 18px;
    border-left: 1px solid #7f9db9;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f7f4, stop:1 #d4d0c8);
}
QComboBox::down-arrow {
    width: 7px;
    height: 4px;
}
QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #7f9db9;
    selection-background-color: #316ac5;
    selection-color: #ffffff;
}

/* Spin box buttons */
QDoubleSpinBox::up-button, QSpinBox::up-button,
QDoubleSpinBox::down-button, QSpinBox::down-button {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f7f4, stop:1 #d4d0c8);
    border: 1px solid #aca899;
    width: 16px;
}
QDoubleSpinBox::up-button:hover, QSpinBox::up-button:hover,
QDoubleSpinBox::down-button:hover, QSpinBox::down-button:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fffce6, stop:1 #f7c740);
    border: 1px solid #b5730f;
}

/* ================================================================
   TAB WIDGET  – classic XP raised tabs
   ================================================================ */
QTabWidget::pane {
    background: #ffffff;
    border: 1px solid #7f9db9;
    border-top: none;
    position: absolute;
    top: -1px;
}
QTabBar::tab {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f7f4, stop:0.4 #ece9d8, stop:1 #dbd7c9);
    border: 1px solid #7f9db9;
    border-bottom: none;
    padding: 4px 14px;
    margin-right: 2px;
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
    min-width: 60px;
}
QTabBar::tab:selected {
    background: #ffffff;
    border-bottom: 1px solid #ffffff;
    color: #000000;
    font-weight: bold;
    margin-bottom: -1px;
    padding-bottom: 5px;
}
QTabBar::tab:!selected {
    margin-top: 2px;
    color: #000000;
}
QTabBar::tab:hover:!selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fffce6, stop:1 #fce49c);
    border-color: #b5730f;
}

/* ================================================================
   TABLES  – XP classic list-view look
   ================================================================ */
QTableWidget {
    background: #ffffff;
    alternate-background-color: #f5f3ee;
    gridline-color: #d4d0c8;
    selection-background-color: #316ac5;
    selection-color: #ffffff;
    border: 2px inset #7f9db9;
    border-radius: 0px;
}
QHeaderView::section {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:0.45 #f0efe3, stop:0.5 #e8e6d9, stop:1 #d4d0c8);
    border: 1px outset #ffffff;
    border-right: 1px solid #aca899;
    border-bottom: 1px solid #aca899;
    padding: 3px 5px;
    font-weight: bold;
    font-size: 8pt;
    color: #000000;
}
QHeaderView::section:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fffce6, stop:1 #fce49c);
}

/* ================================================================
   GROUP BOX  – etched groove border
   ================================================================ */
QGroupBox {
    font-weight: bold;
    border: 2px groove #d4d0c8;
    border-radius: 0px;
    margin-top: 12px;
    padding-top: 14px;
    background: #ece9d8;
    color: #003399;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
    color: #003399;
    background: #ece9d8;
}

/* ================================================================
   TITLE & KPI LABELS
   ================================================================ */
QLabel#title {
    font-family: 'Tahoma', 'MS Sans Serif';
    font-size: 12pt;
    font-weight: bold;
    color: #003399;
}
QLabel#kpi {
    font-family: 'Tahoma', 'MS Sans Serif';
    font-size: 14pt;
    font-weight: bold;
    color: #003399;
}
QLabel#muted {
    color: #808080;
}

/* ================================================================
   CARD FRAMES  – raised 3-D panel
   ================================================================ */
QFrame#card {
    background: #ece9d8;
    border: 2px outset #d4d0c8;
    border-radius: 0px;
}

/* ================================================================
   PROGRESS BAR  – classic XP green chunks
   ================================================================ */
QProgressBar {
    background: #ffffff;
    border: 2px inset #7f9db9;
    border-radius: 0px;
    text-align: center;
    color: #000000;
    height: 18px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #65d465, stop:0.4 #37b837, stop:0.6 #27a527, stop:1 #0c920c);
    border: 1px solid #0c6e0c;
    width: 10px;
    margin: 1px;
}

/* ================================================================
   SCROLL BARS  – XP raised thumb on grooved track
   ================================================================ */
QScrollBar:vertical {
    background: #f0efe3;
    width: 17px;
    border: 1px solid #aca899;
    margin: 17px 0 17px 0;
}
QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ece9d8, stop:0.5 #d4d0c8, stop:1 #ece9d8);
    border: 1px outset #d4d0c8;
    min-height: 20px;
    border-radius: 0px;
}
QScrollBar::handle:vertical:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #fffce6, stop:0.5 #f7c740, stop:1 #fffce6);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f7f4, stop:1 #d4d0c8);
    border: 1px outset #d4d0c8;
    height: 17px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: #f0efe3;
}

QScrollBar:horizontal {
    background: #f0efe3;
    height: 17px;
    border: 1px solid #aca899;
    margin: 0 17px 0 17px;
}
QScrollBar::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ece9d8, stop:0.5 #d4d0c8, stop:1 #ece9d8);
    border: 1px outset #d4d0c8;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fffce6, stop:0.5 #f7c740, stop:1 #fffce6);
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f7f4, stop:1 #d4d0c8);
    border: 1px outset #d4d0c8;
    width: 17px;
}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: #f0efe3;
}

/* ================================================================
   DOCK WIDGET  – blue XP title bar for the SQL panel
   ================================================================ */
QDockWidget {
    font-weight: bold;
    color: #ffffff;
    titlebar-close-icon: none;
}
QDockWidget::title {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a7cc3, stop:0.3 #2968ac, stop:0.7 #1d5fa5, stop:1 #1553a0);
    padding: 4px 6px;
    text-align: left;
    border: 1px solid #003c74;
}

/* ================================================================
   SPLITTER  – visible XP grip
   ================================================================ */
QSplitter::handle {
    background: #ece9d8;
    border: 1px outset #d4d0c8;
}
QSplitter::handle:horizontal {
    width: 6px;
}
QSplitter::handle:vertical {
    height: 6px;
}
QSplitter::handle:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fffce6, stop:1 #fce49c);
}

/* ================================================================
   TOOLTIPS
   ================================================================ */
QToolTip {
    background: #ffffe1;
    border: 1px solid #000000;
    color: #000000;
    padding: 2px;
    font-size: 8pt;
}

/* ================================================================
   CHECK BOXES
   ================================================================ */
QCheckBox {
    spacing: 4px;
}
QCheckBox::indicator {
    width: 13px;
    height: 13px;
    border: 2px inset #7f9db9;
    border-radius: 0px;
    background: #ffffff;
}
QCheckBox::indicator:checked {
    background: #ffffff;
    image: none;
    border: 2px inset #7f9db9;
}
QCheckBox::indicator:hover {
    border: 2px inset #0054e3;
}

/* ================================================================
   CALENDAR POPUP (used by QDateEdit)
   ================================================================ */
QCalendarWidget QAbstractItemView {
    selection-background-color: #316ac5;
    selection-color: #ffffff;
    background: #ffffff;
    alternate-background-color: #f5f3ee;
}
QCalendarWidget QWidget#qt_calendar_navigationbar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a7cc3, stop:1 #1553a0);
    color: #ffffff;
}

/* ================================================================
   MENU BAR (if ever used)
   ================================================================ */
QMenuBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a7cc3, stop:0.5 #2968ac, stop:1 #1d5fa5);
    color: #ffffff;
    border-bottom: 1px solid #003c74;
}
QMenuBar::item:selected {
    background: #316ac5;
}
QMenu {
    background: #ffffff;
    border: 2px outset #d4d0c8;
}
QMenu::item:selected {
    background: #316ac5;
    color: #ffffff;
}

/* ================================================================
   MESSAGE BOXES  – inherit XP look
   ================================================================ */
QMessageBox {
    background: #ece9d8;
}
QMessageBox QLabel {
    color: #000000;
}
"""
