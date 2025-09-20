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
            if any(keyword in port.description for keyword in ['Arduino', 'USB', 'COM']):
                ports.append({
                    'device': port.device,
                    'description': port.description,
                    'vid': port.vid,
                    'pid': port.pid
                })

        return ports

    @staticmethod
    def upload_sketch(port, arduino_path="", mode="universal"):
        """
        Compila e envia o firmware para o Arduino.
        mode = "universal" -> universal_spoofer.ino
        mode = "reset"     -> reset_arduino.ino
        """
        try:
            sketch_file = "universal_spoofer.ino" if mode == "universal" else "reset_arduino.ino"
            sketch_path = os.path.join("firmware", sketch_file)

            if not os.path.exists(sketch_path):
                return False, "", f"Sketch não encontrado: {sketch_path}"

            fqbn = "arduino:avr:micro"  # ajuste conforme sua placa

            compile_cmd = ["arduino-cli", "compile", "--fqbn", fqbn, sketch_path]
            compile_proc = subprocess.run(
                compile_cmd, capture_output=True, text=True, cwd=arduino_path
            )
            if compile_proc.returncode != 0:
                return False, compile_proc.stdout, compile_proc.stderr

            upload_cmd = ["arduino-cli", "upload", "-p", port, "--fqbn", fqbn, sketch_path]
            upload_proc = subprocess.run(
                upload_cmd, capture_output=True, text=True, cwd=arduino_path
            )

            return upload_proc.returncode == 0, upload_proc.stdout, upload_proc.stderr

        except Exception as e:
            return False, "", str(e)

    @staticmethod
    def send_command(port, command, baudrate=115200, timeout=1):
        """
        Envia comando simples (STATUS, SPOOF, RESET).
        """
        try:
            with serial.Serial(port, baudrate, timeout=timeout) as ser:
                time.sleep(1)
                ser.write(f"{command}\n".encode())
                time.sleep(0.5)

                response = ""
                while ser.in_waiting > 0:
                    response += ser.readline().decode(errors="ignore").strip() + "\n"

                try:
                    return True, json.loads(response.strip())
                except Exception:
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
    def spoof_arduino(port):
        return ArduinoUtils.send_command(port, "SPOOF")

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
