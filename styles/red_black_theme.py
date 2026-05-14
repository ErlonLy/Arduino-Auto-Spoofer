RED_BLACK_STYLE = """
QMainWindow, QDialog {
    background-color:
    color:
}

QWidget {
    background-color:
    color:
    border: none;
}

QPushButton {
    background-color:
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color:
}

QPushButton:pressed {
    background-color:
}

QPushButton:disabled {
    background-color:
    color:
}

QComboBox, QLineEdit, QTextEdit {
    background-color:
    color:
    border: 1px solid
    padding: 6px;
    border-radius: 3px;
}

QComboBox:focus, QLineEdit:focus, QTextEdit:focus {
    border: 2px solid
}

QLabel {
    color:
    font-size: 11px;
}

QGroupBox {
    font-weight: bold;
    border: 2px solid
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 15px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 5px;
    color:
}

QProgressBar {
    border: 1px solid
    border-radius: 3px;
    text-align: center;
    color: white;
}

QProgressBar::chunk {
    background-color:
    width: 10px;
}

QTabWidget::pane {
    border: 1px solid
    background-color:
}

QTabBar::tab {
    background-color:
    color:
    padding: 8px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color:
    color: white;
}

QTabBar::tab:hover:!selected {
    background-color:
}

QStatusBar {
    background-color:
    color:
}

QMenuBar {
    background-color:
    color:
}

QMenuBar::item:selected {
    background-color:
}

QMenu {
    background-color:
    color:
    border: 1px solid
}

QMenu::item:selected {
    background-color:
    color: white;
}

QScrollBar:vertical {
    border: none;
    background-color:
    width: 12px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color:
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""