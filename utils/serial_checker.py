import serial
import serial.tools.list_ports
import time
from PyQt5.QtCore import QThread, pyqtSignal

class SerialChecker(QThread):
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # (success, port_name)

    def __init__(self, port_name, timeout=3):
        super().__init__()
        self.port_name = port_name
        self.timeout = timeout

    def run(self):
        try:
            self.message.emit(f"Testando comunicação com {self.port_name}...")
            self.progress.emit(30)
            
            # Tentar comunicação com Arduino
            success, response = self.test_serial_communication(self.port_name)
            
            if success:
                self.message.emit(f"✅ Arduino respondendo: {response}")
                self.progress.emit(100)
                self.finished.emit(True, self.port_name)
            else:
                self.message.emit(f"❌ Arduino não respondeu: {response}")
                self.progress.emit(100)
                self.finished.emit(False, self.port_name)
                
        except Exception as e:
            self.message.emit(f"❌ Erro na verificação: {str(e)}")
            self.finished.emit(False, self.port_name)

    def test_serial_communication(self, port_name):
        """Testa comunicação serial com comando AT"""
        try:
            with serial.Serial(
                port=port_name,
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            ) as ser:
                
                # Limpar buffer
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                
                # Enviar comando de teste
                ser.write(b'AT\r\n')
                time.sleep(0.5)
                
                # Ler resposta
                if ser.in_waiting > 0:
                    response = ser.readline().decode().strip()
                    if response == 'OK':
                        return True, response
                    else:
                        return False, f"Resposta inesperada: {response}"
                else:
                    return False, "Nenhuma resposta recebida"
                    
        except serial.SerialException as e:
            return False, f"Erro serial: {str(e)}"
        except Exception as e:
            return False, f"Erro: {str(e)}"

class PortDiscovery(QThread):
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    ports_found = pyqtSignal(list)  # Lista de portas disponíveis

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            self.message.emit("Procurando portas COM...")
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
        """Encontra todas as portas Arduino disponíveis"""
        arduino_ports = []
        try:
            ports = serial.tools.list_ports.comports()
            
            for port in ports:
                # Verificar por descrição ou VID/PID comum do Arduino
                is_arduino = (
                    'Arduino' in port.description or
                    'CH340' in port.description or
                    'CH341' in port.description or
                    'USB Serial' in port.description or
                    (port.vid == 0x2341 and port.pid == 0x8036) or  # Arduino Leonardo
                    (port.vid == 0x2341 and port.pid == 0x8037) or  # Arduino Micro
                    (port.vid == 0x2A03 and port.pid == 0x8036)     # Arduino Leonardo (clone)
                )
                
                if is_arduino:
                    arduino_ports.append({
                        'device': port.device,
                        'description': port.description,
                        'vid': f"0x{port.vid:04X}" if port.vid else "N/A",
                        'pid': f"0x{port.pid:04X}" if port.pid else "N/A"
                    })
            
            return arduino_ports
            
        except Exception as e:
            print(f"Erro ao buscar portas: {e}")
            return []