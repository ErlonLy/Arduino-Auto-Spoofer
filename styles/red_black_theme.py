RED_BLACK_STYLE = """
QMainWindow, QDialog {
    background-color: #121212;
    color: #ffffff;
}

QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
    border: none;
}

QPushButton {
    background-color: #d32f2f;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #f44336;
}

QPushButton:pressed {
    background-color: #b71c1c;
}

QPushButton:disabled {
    background-color: #5d4037;
    color: #9e9e9e;
}

QComboBox, QLineEdit, QTextEdit {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #d32f2f;
    padding: 6px;
    border-radius: 3px;
}

QComboBox:focus, QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #ff5252;
}

QLabel {
    color: #e0e0e0;
    font-size: 11px;
}

QGroupBox {
    font-weight: bold;
    border: 2px solid #d32f2f;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 15px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 5px;
    color: #ff5252;
}

QProgressBar {
    border: 1px solid #d32f2f;
    border-radius: 3px;
    text-align: center;
    color: white;
}

QProgressBar::chunk {
    background-color: #d32f2f;
    width: 10px;
}

QTabWidget::pane {
    border: 1px solid #d32f2f;
    background-color: #1e1e1e;
}

QTabBar::tab {
    background-color: #2d2d2d;
    color: #e0e0e0;
    padding: 8px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #d32f2f;
    color: white;
}

QTabBar::tab:hover:!selected {
    background-color: #f44336;
}

QStatusBar {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

QMenuBar {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

QMenuBar::item:selected {
    background-color: #d32f2f;
}

QMenu {
    background-color: #1e1e1e;
    color: #e0e0e0;
    border: 1px solid #d32f2f;
}

QMenu::item:selected {
    background-color: #d32f2f;
    color: white;
}

QScrollBar:vertical {
    border: none;
    background-color: #2d2d2d;
    width: 12px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #d32f2f;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""