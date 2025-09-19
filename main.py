import sys
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGroupBox, QLabel, QComboBox, 
                             QPushButton, QTextEdit, QProgressBar, QFileDialog,
                             QMessageBox, QTabWidget, QLineEdit, QStatusBar,
                             QMenuBar, QMenu, QAction, QGridLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import serial.tools.list_ports
import subprocess
from utils.file_manager import FileManager
from utils.arduino_utils import ArduinoUtils
from utils.spoof_engine import SpoofEngine
from utils.serial_checker import SerialChecker, PortDiscovery

class SpoofWorker(QThread):
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, config, file_manager, arduino_utils):
        super().__init__()
        self.config = config
        self.file_manager = file_manager
        self.arduino_utils = arduino_utils

    def run(self):
        try:
            self.message.emit("Iniciando processo de spoofing...")
            self.progress.emit(10)
            
            backup_file = self.file_manager.backup_boards_file(self.config['arduino_path'])
            if not backup_file:
                self.message.emit("Erro: Não foi possível criar backup!")
                self.finished.emit(False)
                return
            
            self.progress.emit(30)
            
            success = self.file_manager.modify_boards_file(
                self.config['arduino_path'], 
                self.config['mouse_profile']
            )
            
            if not success:
                self.message.emit("Erro na modificação do boards.txt!")
                self.finished.emit(False)
                return
            
            self.progress.emit(60)
            
            if self.config.get('upload_sketch', False):
                self.message.emit("Fazendo upload do sketch...")
                success, stdout, stderr = self.arduino_utils.upload_sketch(
                    self.config['selected_port'],
                    "firmware/mouse_spoofer.ino",
                    self.config['arduino_path']
                )
                if not success:
                    self.message.emit(f"Erro no upload: {stderr}")
            
            self.progress.emit(100)
            self.message.emit("Processo concluído com sucesso!")
            self.finished.emit(True)
            
        except Exception as e:
            self.message.emit(f"Erro durante spoofing: {str(e)}")
            self.finished.emit(False)

class RestoreWorker(QThread):
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, arduino_path, backup_file, file_manager):
        super().__init__()
        self.arduino_path = arduino_path
        self.backup_file = backup_file
        self.file_manager = file_manager

    def run(self):
        try:
            self.message.emit("Iniciando restauração...")
            self.progress.emit(30)
            
            success = self.file_manager.restore_backup(
                self.backup_file, 
                self.arduino_path
            )
            
            if not success:
                self.message.emit("Erro na restauração do backup!")
                self.finished.emit(False)
                return
            
            self.message.emit("Backup restaurado com sucesso!")
            self.progress.emit(100)
            self.finished.emit(True)
            
        except Exception as e:
            self.message.emit(f"Erro durante restauração: {str(e)}")
            self.finished.emit(False)

class ArduinoSpooferApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.serial_checker = None
        self.port_discovery = None
        self.file_manager = FileManager()
        self.arduino_utils = ArduinoUtils()
        self.spoof_engine = SpoofEngine()
        
        self.config = {
            'arduino_path': '',
            'selected_port': '',
            'selected_brand': '',
            'selected_model': '',
            'upload_sketch': True,
            'mouse_profiles': self.spoof_engine.load_profiles()
        }
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        self.setWindowTitle("Arduino Mouse Spoofer")
        self.setGeometry(100, 100, 900, 700)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.create_menu_bar()
        
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
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

    def apply_theme(self):
        from styles.red_black_theme import RED_BLACK_STYLE
        self.setStyleSheet(RED_BLACK_STYLE)

    def create_menu_bar(self):
        menubar = self.menuBar()
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
        self.brand_combo.addItems(self.config['mouse_profiles'].keys())
        self.brand_combo.currentTextChanged.connect(self.update_models)
        mouse_layout.addWidget(self.brand_combo, 0, 1)
        
        mouse_layout.addWidget(QLabel("Modelo:"), 1, 0)
        self.model_combo = QComboBox()
        mouse_layout.addWidget(self.model_combo, 1, 1)
        
        layout.addWidget(mouse_group)

        path_group = QGroupBox("Caminho do Arduino")
        path_layout = QHBoxLayout(path_group)
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Caminho para boards.txt do Arduino...")
        path_layout.addWidget(self.path_edit)
        
        self.browse_btn = QPushButton("Procurar")
        self.browse_btn.clicked.connect(self.browse_arduino_path)
        path_layout.addWidget(self.browse_btn)
        
        layout.addWidget(path_group)

        action_layout = QHBoxLayout()
        self.spoof_btn = QPushButton("Executar Spoofer")
        self.spoof_btn.clicked.connect(self.execute_spoof)
        self.spoof_btn.setStyleSheet("background-color: #d32f2f; color: white; font-size: 14px;")
        action_layout.addWidget(self.spoof_btn)
        
        self.restore_btn = QPushButton("Restaurar Backup")
        self.restore_btn.clicked.connect(self.restore_backup)
        action_layout.addWidget(self.restore_btn)
        
        layout.addLayout(action_layout)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        self.refresh_ports()
        self.update_models()

    def setup_config_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Configurações avançadas serão implementadas aqui"))

    def refresh_ports(self):
        self.port_combo.clear()
        self.port_status_label.setText("Status: Não verificado")
        self.port_status_label.setStyleSheet("color: #ff5252; font-weight: bold;")
        
        self.port_discovery = PortDiscovery()
        self.port_discovery.message.connect(self.log_message)
        self.port_discovery.progress.connect(self.progress_bar.setValue)
        self.port_discovery.ports_found.connect(self.on_ports_discovered)
        self.port_discovery.start()

    def on_ports_discovered(self, ports):
        for port in ports:
            display_text = f"{port['device']} - {port['description']}"
            self.port_combo.addItem(display_text, port['device'])
        
        if ports:
            self.log_message(f"{len(ports)} porta(s) Arduino encontrada(s)")
        else:
            self.log_message("Nenhuma porta Arduino encontrada")

    def verify_selected_port(self):
        port = self.port_combo.currentText()
        if not port:
            self.log_message("Selecione uma porta primeiro!")
            return
        
        self.port_status_label.setText("Status: Verificando...")
        self.port_status_label.setStyleSheet("color: #ffeb3b; font-weight: bold;")
        self.verify_btn.setEnabled(False)
        
        self.serial_checker = SerialChecker(port)
        self.serial_checker.message.connect(self.log_message)
        self.serial_checker.progress.connect(self.progress_bar.setValue)
        self.serial_checker.finished.connect(self.on_verification_finished)
        self.serial_checker.start()

    def on_verification_finished(self, success, port_name):
        self.verify_btn.setEnabled(True)
        if success:
            self.port_status_label.setText("Status: ✅ Verificado")
            self.port_status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
            self.log_message(f"Porta {port_name} verificada com sucesso!")
            self.config['verified_port'] = port_name
        else:
            self.port_status_label.setText("Status: ❌ Falha")
            self.port_status_label.setStyleSheet("color: #f44336; font-weight: bold;")
            self.log_message(f"Falha na verificação da porta {port_name}")

    def update_models(self):
        self.model_combo.clear()
        brand = self.brand_combo.currentText()
        if brand in self.config['mouse_profiles']:
            self.model_combo.addItems(self.config['mouse_profiles'][brand].keys())

    def browse_arduino_path(self):
        path = QFileDialog.getExistingDirectory(self, "Selecionar Pasta do Arduino")
        if path:
            self.path_edit.setText(path)

    def execute_spoof(self):
        if not self.validate_inputs():
            return
        
        brand = self.brand_combo.currentText()
        model = self.model_combo.currentText()
        mouse_profile = self.spoof_engine.get_profile(brand, model)
        
        if not mouse_profile:
            self.log_message("Perfil de mouse não encontrado!")
            return
        
        self.config.update({
            'selected_port': self.port_combo.currentText(),
            'selected_brand': brand,
            'selected_model': model,
            'arduino_path': self.path_edit.text(),
            'mouse_profile': mouse_profile
        })
        
        self.worker = SpoofWorker(self.config, self.file_manager, self.arduino_utils)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.message.connect(self.log_message)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.start()
        
        self.set_buttons_enabled(False)

    def restore_backup(self):
        backup_file = self.file_manager.get_latest_backup()
        if not backup_file:
            self.log_message("Nenhum backup encontrado!")
            return
        
        self.worker = RestoreWorker(
            self.config['arduino_path'], 
            backup_file, 
            self.file_manager
        )
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.message.connect(self.log_message)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.start()
        
        self.set_buttons_enabled(False)

    def validate_inputs(self):
        if not self.port_combo.currentText():
            self.log_message("Selecione uma porta COM!")
            return False
        if not self.model_combo.currentText():
            self.log_message("Selecione um modelo de mouse!")
            return False
        if not self.path_edit.text():
            self.log_message("Selecione o caminho do Arduino!")
            return False
        if not hasattr(self, 'verified_port') or self.config.get('verified_port') != self.port_combo.currentText():
            self.log_message("Verifique a porta antes de continuar!")
            return False
        return True

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        self.status_bar.showMessage(message)

    def on_operation_finished(self, success):
        self.set_buttons_enabled(True)
        if success:
            self.log_message("Operação concluída com sucesso!")
        else:
            self.log_message("Operação falhou!")

    def set_buttons_enabled(self, enabled):
        self.spoof_btn.setEnabled(enabled)
        self.restore_btn.setEnabled(enabled)
        self.refresh_ports_btn.setEnabled(enabled)
        self.browse_btn.setEnabled(enabled)
        self.verify_btn.setEnabled(enabled)

    def load_settings(self):
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                    self.path_edit.setText(self.config.get('arduino_path', ''))
        except:
            pass

    def save_config(self):
        try:
            with open('config.json', 'w') as f:
                json.dump(self.config, f)
            self.log_message("Configurações salvas!")
        except Exception as e:
            self.log_message(f"Erro ao salvar: {str(e)}")

    def load_config(self):
        path, _ = QFileDialog.getOpenFileName(self, "Carregar Configuração", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, 'r') as f:
                    self.config.update(json.load(f))
                    self.path_edit.setText(self.config.get('arduino_path', ''))
                self.log_message("Configuração carregada!")
            except Exception as e:
                self.log_message(f"Erro ao carregar: {str(e)}")

    def show_about(self):
        QMessageBox.about(self, "Sobre", "Arduino Mouse Spoofer\n\nFerramenta para spoofing de Arduino como mouse HID")

def main():
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    window = ArduinoSpooferApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()