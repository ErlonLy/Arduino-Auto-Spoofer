import serial
import serial.tools.list_ports
import subprocess
import time
import os
import json


class ArduinoUtils:
    @staticmethod
    def detect_arduino_ports():
        ports = []
        available_ports = serial.tools.list_ports.comports()

        for port in available_ports:
            if port.description and any(
                keyword.lower() in port.description.lower()
                for keyword in ['arduino', 'usb', 'com']
            ):
                ports.append({
                    'device': port.device,
                    'description': port.description,
                    'vid': port.vid,
                    'pid': port.pid
                })

        return ports

    @staticmethod
    def upload_sketch(port, arduino_path="", mode="universal"):
        try:
            if mode == "universal":
                sketch_path = os.path.join("firmware", "universal_spoofer")
            elif mode == "reset":
                sketch_path = os.path.join("firmware", "reset_arduino")
            elif mode == "blink":
                sketch_path = os.path.join("firmware", "blink_test")
            elif mode == "echo":
                sketch_path = os.path.join("firmware", "echo_test")
            else:
                return False, "", f"Modo desconhecido: {mode}"

            if not os.path.exists(sketch_path):
                return False, "", f"Sketch não encontrado: {sketch_path}"

            cli_path = os.path.join("utils", "arduino-cli.exe")
            cli_path = os.path.abspath(cli_path)

            if not os.path.exists(cli_path):
                return False, "", f"arduino-cli.exe não encontrado em {cli_path}"

            fqbn = "arduino:avr:leonardo"

            compile_cmd = [cli_path, "compile", "--fqbn", fqbn, sketch_path]
            compile_proc = subprocess.run(compile_cmd, capture_output=True, text=True)
            if compile_proc.returncode != 0:
                return False, compile_proc.stdout, compile_proc.stderr

            upload_cmd = [cli_path, "upload", "-p", port, "--fqbn", fqbn, sketch_path]
            upload_proc = subprocess.run(upload_cmd, capture_output=True, text=True)

            return upload_proc.returncode == 0, upload_proc.stdout, upload_proc.stderr

        except Exception as e:
            return False, "", str(e)

    @staticmethod
    def send_command(port, command, baudrate=115200, timeout=2):
        try:
            with serial.Serial(port, baudrate, timeout=timeout) as ser:
                time.sleep(2) 
                ser.reset_input_buffer()  
                
                ser.write(f"{command}\n".encode())
                time.sleep(0.5)

                response = ""
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if ser.in_waiting > 0:
                        line = ser.readline().decode(errors="ignore").strip()
                        if line:
                            response += line + "\n"
                            if any(keyword in line for keyword in ["SUCCESS", "ERROR", "STATUS", "READY"]):
                                break
                    time.sleep(0.1)

                return True, response.strip()

        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_arduino_info(port):
        return ArduinoUtils.send_command(port, "STATUS")

    @staticmethod
    def reset_arduino(port):
        return ArduinoUtils.send_command(port, "RESET")

    @staticmethod
    def save_config(port):
        return ArduinoUtils.send_command(port, "SAVE")

    @staticmethod
    def spoof_arduino(port, vid, pid, product_name):
        command = f'SPOOF {vid} {pid} "{product_name}"'
        return ArduinoUtils.send_command(port, command, timeout=5)

    @staticmethod
    def find_arduino_by_vid_pid(vid, pid):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if port.vid == vid and port.pid == pid:
                return port.device
        return None

    @staticmethod
    def list_all_serial_ports():
        ports = serial.tools.list_ports.comports()
        return [{
            "device": port.device,
            "description": port.description,
            "vid": port.vid,
            "pid": port.pid,
            "serial_number": port.serial_number,
            "manufacturer": port.manufacturer
        } for port in ports]

    @staticmethod
    def wait_for_reconnection(old_port, timeout=30, check_interval=1):
        print(f"Aguardando reconexão do Arduino (porta {old_port})...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            ports = ArduinoUtils.list_all_serial_ports()
            old_port_exists = any(p['device'] == old_port for p in ports)
            
            if not old_port_exists:
                break
                
            time.sleep(check_interval)

        start_time = time.time()
        while time.time() - start_time < timeout:
            ports = ArduinoUtils.list_all_serial_ports()
            
            for port_info in ports:
                if port_info['device'] != old_port:
                    if any(keyword.lower() in port_info['description'].lower() 
                           for keyword in ['arduino', 'usb serial', 'com']):
                        print(f"Novo Arduino encontrado na porta: {port_info['device']}")
                        return port_info['device']
            
            time.sleep(check_interval)
        
        print("Timeout aguardando reconexão do Arduino")
        return None

    @staticmethod
    def run_serial_tool(command_args):
        try:
            serial_tool_path = os.path.join("utils", "serial_tool.exe")
            if not os.path.exists(serial_tool_path):
                return False, "serial_tool.exe não encontrado"
            
            result = subprocess.run(
                [serial_tool_path] + command_args,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip() or result.stdout.strip()
                
        except subprocess.TimeoutExpired:
            return False, "Timeout ao executar serial_tool"
        except Exception as e:
            return False, f"Erro ao executar serial_tool: {str(e)}"

    @staticmethod
    def get_serial_ports_with_info():
        ports_info = []
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            port_info = {
                'device': port.device,
                'description': port.description,
                'vid': f"0x{port.vid:04X}" if port.vid else "N/A",
                'pid': f"0x{port.pid:04X}" if port.pid else "N/A",
                'serial_number': port.serial_number or "N/A",
                'manufacturer': port.manufacturer or "N/A",
                'product': port.product or "N/A"
            }
            ports_info.append(port_info)
        
        return ports_info

    @staticmethod
    def check_port_ready(port, baudrate=115200, timeout=3):
        try:
            with serial.Serial(port, baudrate, timeout=timeout) as ser:
                ser.write(b"\n") 
                time.sleep(0.5)
                
                if ser.in_waiting > 0:
                    response = ser.readline().decode().strip()
                    return True, f"Porta respondendo: {response}"
                else:
                    ser.write(b"STATUS\n")
                    time.sleep(0.5)
                    
                    if ser.in_waiting > 0:
                        response = ser.readline().decode().strip()
                        return True, f"Resposta ao STATUS: {response}"
                    else:
                        return False, "Porta não responde"
                        
        except serial.SerialException as e:
            return False, f"Erro de comunicação: {str(e)}"
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"