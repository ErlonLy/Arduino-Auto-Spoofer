import sys
import os
import json
import time
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QGroupBox, QLabel, QComboBox,
                             QPushButton, QTextEdit, QProgressBar, QFileDialog,
                             QMessageBox, QTabWidget, QLineEdit, QStatusBar,
                             QAction, QGridLayout, QCheckBox, QMenuBar,
                             QDesktopWidget)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QPoint
from utils.file_manager import FileManager
from utils.arduino_utils import ArduinoUtils
from utils.spoof_engine import SpoofEngine


class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setFixedHeight(35)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)

        self.title = QLabel("Arduino Mouse Spoofer")
        self.title.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
        layout.addWidget(self.title)

        layout.addStretch()

        self.minButton = QPushButton("–")
        self.minButton.setFixedSize(40, 25)
        self.minButton.setObjectName("titleButton")
        self.minButton.clicked.connect(self.parent.showMinimized)
        layout.addWidget(self.minButton)

        self.closeButton = QPushButton("✕")
        self.closeButton.setFixedSize(40, 25)
        self.closeButton.setObjectName("closeButton")
        self.closeButton.clicked.connect(self.parent.close)
        layout.addWidget(self.closeButton)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent.dragPosition = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.parent.move(event.globalPos() - self.parent.dragPosition)
            event.accept()


class ArduinoSpooferApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dragPosition = QPoint()
        self.worker = None
        self.file_manager = FileManager()
        self.arduino_utils = ArduinoUtils()
        self.spoof_engine = SpoofEngine()

        self.config = {
            'arduino_path': '',
            'selected_port': '',
            'selected_brand': '',
            'selected_model': '',
            'upload_sketch': True,
            'firmware_mode': 'universal',
            'mouse_profiles': self.spoof_engine.load_profiles(),
            'force_vid_pid': False,
            'force_product_manufacturer': False
        }

        self.mouse_profiles = self.config['mouse_profiles']
        if not self.mouse_profiles:
            self.mouse_profiles = {"Exemplo": {"Modelo1": {"vid": "0x1234", "pid": "0x5678"}}}

        self.init_ui()
        self.load_settings()
        self.center_window()

    def init_ui(self):
        self.setWindowTitle("Arduino Mouse Spoofer")
        self.setGeometry(100, 100, 950, 750)
        self.setWindowFlags(Qt.FramelessWindowHint)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)

        self.menu_bar = QMenuBar(self)
        self.create_menu_bar(self.menu_bar)
        main_layout.addWidget(self.menu_bar)

        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        spoof_tab = QWidget()
        tabs.addTab(spoof_tab, "Spoofer")
        self.setup_spoof_tab(spoof_tab)

        config_tab = QWidget()
        tabs.addTab(config_tab, "Configurações")
        self.setup_config_tab(config_tab)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Pronto")

        self.apply_theme()

    def center_window(self):
        screen = QDesktopWidget().availableGeometry().center()
        frame = self.frameGeometry()
        frame.moveCenter(screen)
        self.move(frame.topLeft())

    def apply_theme(self):
        from styles.red_black_theme import RED_BLACK_STYLE
        self.setStyleSheet(RED_BLACK_STYLE)

    def create_menu_bar(self, menubar):
        file_menu = menubar.addMenu("Arquivo")

        load_action = QAction("Carregar Configuração", self)
        load_action.triggered.connect(self.load_config)
        file_menu.addAction(load_action)

        save_action = QAction("Salvar Configuração", self)
        save_action.triggered.connect(self.save_config)
        file_menu.addAction(save_action)

        file_menu.addSeparator()
        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("Ajuda")
        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_spoof_tab(self, tab):
        layout = QVBoxLayout(tab)

        port_group = QGroupBox("Configuração da Porta")
        port_layout = QGridLayout(port_group)

        port_layout.addWidget(QLabel("Porta COM:"), 0, 0)
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(150)
        port_layout.addWidget(self.port_combo, 0, 1)

        self.refresh_ports_btn = QPushButton("Atualizar Portas")
        self.refresh_ports_btn.clicked.connect(self.refresh_ports)
        port_layout.addWidget(self.refresh_ports_btn, 0, 2)

        verify_layout = QHBoxLayout()
        self.verify_btn = QPushButton("Verificar Porta")
        self.verify_btn.clicked.connect(self.verify_selected_port)
        verify_layout.addWidget(self.verify_btn)

        self.port_status_label = QLabel("Status: Não verificado")
        self.port_status_label.setStyleSheet("color: #ff5252; font-weight: bold;")
        verify_layout.addWidget(self.port_status_label)

        port_layout.addLayout(verify_layout, 1, 0, 1, 3)
        layout.addWidget(port_group)

        mouse_group = QGroupBox("Seleção de Mouse")
        mouse_layout = QGridLayout(mouse_group)

        mouse_layout.addWidget(QLabel("Marca:"), 0, 0)
        self.brand_combo = QComboBox()
        self.brand_combo.addItems(self.mouse_profiles.keys())
        self.brand_combo.currentTextChanged.connect(self.update_models)
        mouse_layout.addWidget(self.brand_combo, 0, 1)

        mouse_layout.addWidget(QLabel("Modelo:"), 1, 0)
        self.model_combo = QComboBox()
        mouse_layout.addWidget(self.model_combo, 1, 1)

        layout.addWidget(mouse_group)

        path_group = QGroupBox("Caminho do Arduino")
        path_layout = QHBoxLayout(path_group)

        self.path_edit_spoofer = QLineEdit()
        self.path_edit_spoofer.setPlaceholderText("Caminho para instalação do Arduino CLI...")
        path_layout.addWidget(self.path_edit_spoofer)

        self.browse_btn = QPushButton("Procurar")
        self.browse_btn.clicked.connect(self.browse_arduino_path)
        path_layout.addWidget(self.browse_btn)

        layout.addWidget(path_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        default_path = self.find_default_arduino_path()
        if default_path:
            self.path_edit_spoofer.setText(default_path)
            self.log_message(f"✅ Caminho Arduino encontrado: {default_path}")
        else:
            self.log_message("⚠️ Pasta do Arduino não encontrada, favor buscar manualmente.")

        action_layout = QHBoxLayout()
        self.spoof_btn = QPushButton("Executar Spoofer")
        self.spoof_btn.clicked.connect(self.execute_spoof)
        self.spoof_btn.setStyleSheet("background-color: #d32f2f; color: white; font-size: 14px;")
        action_layout.addWidget(self.spoof_btn)

        layout.addLayout(action_layout)

        test_layout = QHBoxLayout()
        self.test_status_btn = QPushButton("Testar STATUS")
        self.test_status_btn.clicked.connect(self.test_status)
        test_layout.addWidget(self.test_status_btn)

        self.test_spoof_btn = QPushButton("Testar SPOOF")
        self.test_spoof_btn.clicked.connect(self.test_spoof)
        test_layout.addWidget(self.test_spoof_btn)

        layout.addLayout(test_layout)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.refresh_ports()
        self.update_models()

    def setup_config_tab(self, tab):
        layout = QGridLayout(tab)

        fw_group = QGroupBox("Firmware")
        fw_layout = QVBoxLayout(fw_group)
        self.fw_combo = QComboBox()
        self.fw_combo.addItems(["universal"])
        fw_layout.addWidget(QLabel("Selecionar firmware:"))
        fw_layout.addWidget(self.fw_combo)

        flags_group = QGroupBox("Opções de Flags USB")
        flags_layout = QVBoxLayout(flags_group)
        self.chk_force_vid_pid = QCheckBox("Forçar VID/PID")
        self.chk_force_product_manufacturer = QCheckBox("Forçar Nome Produto/Fabricante")
        flags_layout.addWidget(self.chk_force_vid_pid)
        flags_layout.addWidget(self.chk_force_product_manufacturer)

        arduino_group = QGroupBox("Localização do Arduino")
        arduino_layout = QVBoxLayout(arduino_group)
        self.path_edit_config = QLineEdit()
        self.path_edit_config.setPlaceholderText("Caminho para instalação do Arduino CLI...")
        browse_btn = QPushButton("Procurar Manualmente")
        browse_btn.clicked.connect(self.browse_arduino_path)
        arduino_layout.addWidget(self.path_edit_config)
        arduino_layout.addWidget(browse_btn)

        verify_group = QGroupBox("Verificação do Spoof")
        verify_layout = QVBoxLayout(verify_group)
        self.verify_spoof_btn = QPushButton("Procurar rastro do Arduino")
        self.verify_spoof_btn.clicked.connect(self.verify_spoof_status)
        verify_layout.addWidget(self.verify_spoof_btn)

        layout.addWidget(fw_group, 0, 0)
        layout.addWidget(flags_group, 0, 1)
        layout.addWidget(arduino_group, 1, 0)
        layout.addWidget(verify_group, 1, 1)

    def find_default_arduino_path(self):
        base_path = os.path.join(
            os.path.expanduser("~"),
            "AppData", "Local", "Arduino15", "packages", "arduino", "hardware", "avr"
        )
        if os.path.exists(base_path):
            versions = os.listdir(base_path)
            versions = [v for v in versions if os.path.isdir(os.path.join(base_path, v))]
            if versions:
                versions.sort(reverse=True)
                default_path = os.path.join(base_path, versions[0])
                boards_file = os.path.join(default_path, "boards.txt")
                if os.path.exists(boards_file):
                    return default_path
        return None

    def refresh_ports(self):
        self.port_combo.clear()
        self.port_status_label.setText("Status: Não verificado")
        self.port_status_label.setStyleSheet("color: #ff5252; font-weight: bold;")

        ports = self.arduino_utils.list_all_serial_ports()
        if ports:
            for p in ports:
                label = f"{p['device']} ({p['description']})"
                self.port_combo.addItem(label, p['device'])
            self.log_message(f"{len(ports)} porta(s) encontrada(s)")
        else:
            self.log_message("Nenhuma porta encontrada")

    def verify_selected_port(self):
        port = self.port_combo.currentData()
        if not port:
            self.log_message("Selecione uma porta primeiro!")
            return

        self.port_status_label.setText("Status: Verificando...")
        self.port_status_label.setStyleSheet("color: #ffeb3b; font-weight: bold;")

        ok, out, err = self.arduino_utils.upload_sketch(
            port, self.path_edit_spoofer.text(), mode="blink"
        )
        if ok:
            self.port_status_label.setText("Status: ✅ Sucesso")
            self.port_status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
            self.log_message(f"{port}  ✅ Verificado com Sucesso !!!")
        else:
            self.port_status_label.setText("Status: ❌ Falha")
            self.port_status_label.setStyleSheet("color: #f44336; font-weight: bold;")
            self.log_message(f"Falha ao enviar blink_test.ino: {err or out}")

    def update_models(self):
        self.model_combo.clear()
        brand = self.brand_combo.currentText()
        if brand in self.mouse_profiles:
            self.model_combo.addItems(self.mouse_profiles[brand].keys())

    def browse_arduino_path(self):
        path = QFileDialog.getExistingDirectory(self, "Selecionar Pasta do Arduino")
        if path:
            self.path_edit_spoofer.setText(path)
            self.path_edit_config.setText(path)

    def verify_spoof_status(self):
        arduino_path = self.path_edit_config.text().strip()
        if not arduino_path:
            self.log_message("⚠️ Caminho do Arduino não definido.")
            return

        profile = self.config.get("mouse_profile")
        if not profile:
            brand = self.brand_combo.currentText()
            model = self.model_combo.currentText()
            profile = self.spoof_engine.get_profile(brand, model)

        if not profile:
            self.log_message("⚠️ Nenhum perfil carregado ou selecionado.")
            return

        vid = profile.get("vid")
        pid = profile.get("pid")

        ok, msg = self.file_manager.check_spoof_trace(arduino_path)
        if ok:
            self.log_message(f"✅ Spoof detectado: {msg}")
        else:
            self.log_message(f"❌ Spoof não encontrado: {msg}")

    def execute_spoof(self):
        if not self.validate_inputs():
            return

        brand = self.brand_combo.currentText()
        model = self.model_combo.currentText()
        mouse_profile = self.spoof_engine.get_profile(brand, model)
        if not mouse_profile:
            self.log_message("Perfil de mouse não encontrado!")
            return

        port = self.port_combo.currentData()
        vid = mouse_profile["vid"]
        pid = mouse_profile["pid"]
        product = mouse_profile.get("product", f"{brand} {model}")

        force_vid_pid = self.chk_force_vid_pid.isChecked()
        force_product_manufacturer = self.chk_force_product_manufacturer.isChecked()

        self.config.update({
            'selected_port': port,
            'selected_brand': brand,
            'selected_model': model,
            'arduino_path': self.path_edit_spoofer.text(),
            'mouse_profile': mouse_profile,
            'firmware_mode': self.fw_combo.currentText(),
            'force_vid_pid': force_vid_pid,
            'force_product_manufacturer': force_product_manufacturer
        })

        arduino_path = self.path_edit_spoofer.text().strip()
        backup = self.file_manager.backup_boards_file(arduino_path)
        if backup:
            self.log_message(f"Backup criado: {backup}")
        else:
            self.log_message("⚠️ Não foi possível criar backup do boards.txt")

        ok = self.file_manager.modify_boards_file(
            arduino_path,
            {
                "vid": vid,
                "pid": pid,
                "product": product,
                "usb_product": mouse_profile.get("usb_product", product),
                "usb_manufacturer": mouse_profile.get("usb_manufacturer", brand),
                "force_vid_pid": force_vid_pid,
                "force_product_manufacturer": force_product_manufacturer
            }
        )
        if not ok:
            self.log_message("❌ Falha ao modificar boards.txt")
            return
        self.log_message(f"boards.txt modificado para {brand} {model} ({vid}:{pid})")

        self.log_message("⚡ Enviando firmware universal...")
        time.sleep(3) 
        ok, out, err = self.arduino_utils.upload_sketch(
            port, arduino_path, mode="universal"
        )

        if not ok:
            self.log_message(f"❌ Falha ao enviar universal_spoofer.ino: {err or out}")
            return

        self.log_message("✅ Firmware universal enviado, aguardando reconexão...")
        self.progress_bar.setValue(100)

    def validate_inputs(self):
        if not self.port_combo.currentData():
            self.log_message("Selecione uma porta COM!")
            return False
        if not self.model_combo.currentText():
            self.log_message("Selecione um modelo de mouse!")
            return False
        if not self.path_edit_spoofer.text():
            self.log_message("Selecione o caminho do Arduino!")
            return False
        return True

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        self.statusBar().showMessage(message)

    def test_status(self):
        port = self.port_combo.currentData()
        if not port:
            self.log_message("Nenhuma porta selecionada para teste")
            return
        resp = self.spoof_engine.get_status(port)
        self.log_message(f"STATUS: {resp}")

    def test_spoof(self):
        port = self.port_combo.currentData()
        if not port:
            self.log_message("Nenhuma porta selecionada para teste")
            return
        brand = self.brand_combo.currentText()
        model = self.model_combo.currentText()
        profile = self.spoof_engine.get_profile(brand, model)
        if not profile:
            self.log_message("Perfil de mouse não encontrado")
            return
        vid = profile["vid"]
        pid = profile["pid"]
        resp = self.spoof_engine.spoof(port, vid, pid)
        self.log_message(f"SPOOF: {resp}")

    def load_settings(self):
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                    self.path_edit_spoofer.setText(self.config.get('arduino_path', ''))
                    self.path_edit_config.setText(self.config.get('arduino_path', ''))
                    self.chk_force_vid_pid.setChecked(self.config.get('force_vid_pid', False))
                    self.chk_force_product_manufacturer.setChecked(self.config.get('force_product_manufacturer', False))
        except Exception as e:
            self.log_message(f"Erro ao carregar config inicial: {e}")

    def save_config(self):
        try:
            self.config['force_vid_pid'] = self.chk_force_vid_pid.isChecked()
            self.config['force_product_manufacturer'] = self.chk_force_product_manufacturer.isChecked()
            self.config['arduino_path'] = self.path_edit_spoofer.text()
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            self.log_message("Configurações salvas em config.json!")
        except Exception as e:
            self.log_message(f"Erro ao salvar configuração: {e}")

    def load_config(self):
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self.config.update(saved)
                    self.path_edit_spoofer.setText(self.config.get('arduino_path', ''))
                    self.path_edit_config.setText(self.config.get('arduino_path', ''))
                    brand = self.config.get('selected_brand', '')
                    model = self.config.get('selected_model', '')
                    if brand in self.mouse_profiles:
                        self.brand_combo.setCurrentText(brand)
                        if model in self.mouse_profiles[brand]:
                            self.model_combo.setCurrentText(model)
                    self.chk_force_vid_pid.setChecked(self.config.get('force_vid_pid', False))
                    self.chk_force_product_manufacturer.setChecked(self.config.get('force_product_manufacturer', False))
                self.log_message("Configuração carregada de config.json!")
        except Exception as e:
            self.log_message(f"Erro ao carregar configuração: {e}")

    def show_about(self):
        QMessageBox.about(self, "Sobre","Arduino Mouse Spoofer automatico\n\n \tFeito por Lyrien")


def main():
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    window = ArduinoSpooferApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
