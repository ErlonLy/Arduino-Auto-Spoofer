import serial
import serial.tools.list_ports
import time
import json
from PyQt5.QtCore import QThread, pyqtSignal


class SerialChecker(QThread):
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, port_name, timeout=3):
        super().__init__()
        self.port_name = self.extract_port_name(port_name)
        self.timeout = timeout

    def extract_port_name(self, port_string):
        if not port_string:
            return ""
        if port_string.startswith("COM") and len(port_string) <= 10:
            return port_string
        if " - " in port_string:
            parts = port_string.split(" - ")
            if parts and parts[0].startswith("COM"):
                return parts[0].strip()
        import re
        com_match = re.search(r"COM\d+", port_string)
        return com_match.group(0) if com_match else port_string

    def run(self):
        try:
            self.message.emit(f"🔍 Testando comunicação com {self.port_name}...")
            self.progress.emit(30)

            with serial.Serial(self.port_name, 115200, timeout=self.timeout) as ser:
                time.sleep(1)
                ser.reset_input_buffer()
                ser.write(b"STATUS\n")
                time.sleep(0.5)
                response = ser.readline().decode(errors="ignore").strip()

            if not response:
                self.message.emit("❌ Nenhuma resposta recebida")
                self.finished.emit(False, self.port_name)
                return

            try:
                parsed = json.loads(response)
                status = parsed.get("status", "")
                if status in ("OK", "READY"):
                    fw = parsed.get("fw", "desconhecido")
                    self.message.emit(f"✅ Firmware ativo: {fw}")
                    self.finished.emit(True, self.port_name)
                else:
                    self.message.emit(f"⚠️ JSON inesperado: {parsed}")
                    self.finished.emit(False, self.port_name)
            except json.JSONDecodeError:
                if "OK" in response.upper():
                    self.message.emit("⚠️ Resposta OK não-JSON")
                    self.finished.emit(True, self.port_name)
                else:
                    self.message.emit(f"❌ Resposta inválida: {response}")
                    self.finished.emit(False, self.port_name)

        except Exception as e:
            self.message.emit(f"❌ Erro: {str(e)}")
            self.finished.emit(False, self.port_name)


class PortDiscovery(QThread):
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    ports_found = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            self.message.emit("📡 Procurando portas COM...")
            self.progress.emit(30)

            ports = self.find_arduino_ports()

            if ports:
                self.message.emit(f"✅ {len(ports)} porta(s) encontrada(s)")
                self.ports_found.emit(ports)
            else:
                self.message.emit("❌ Nenhuma porta Arduino encontrada")
                self.ports_found.emit([])

            self.progress.emit(100)

        except Exception as e:
            self.message.emit(f"❌ Erro na descoberta de portas: {str(e)}")
            self.ports_found.emit([])

    def find_arduino_ports(self):
        arduino_ports = []
        try:
            ports = serial.tools.list_ports.comports()

            for port in ports:
                is_arduino = (
                    "Arduino" in port.description
                    or "CH340" in port.description
                    or "CH341" in port.description
                    or "USB Serial" in port.description
                    or (port.vid == 0x2341 and port.pid == 0x8036)
                    or (port.vid == 0x2341 and port.pid == 0x8037)
                    or (port.vid == 0x2A03 and port.pid == 0x8036)
                )

                if is_arduino:
                    arduino_ports.append({
                        "device": port.device,
                        "description": port.description,
                        "vid": f"0x{port.vid:04X}" if port.vid else "N/A",
                        "pid": f"0x{port.pid:04X}" if port.pid else "N/A",
                    })

            return arduino_ports

        except Exception as e:
            print(f"Erro ao buscar portas: {e}")
            return []
