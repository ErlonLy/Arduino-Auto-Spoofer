import serial
import time
import json
import os


class SpoofEngine:
    def __init__(self, port=None, baud_rate=115200, timeout=2):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.ser = None

    # ---------------- Conexão ----------------
    def connect(self):
        try:
            if not self.port:
                return False
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            time.sleep(1)
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao conectar: {e}")
            return False

    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

    # ---------------- Comunicação ----------------
    def send(self, command):
        """
        Envia comando ao Arduino e retorna resposta.
        Retorna sempre (success: bool, response: str|dict).
        """
        try:
            if not self.ser or not self.ser.is_open:
                return False, "No connection"

            self.ser.reset_input_buffer()
            self.ser.write(f"{command}\n".encode())
            time.sleep(0.5)

            response = ""
            while self.ser.in_waiting > 0:
                line = self.ser.readline().decode(errors="ignore").strip()
                if line:
                    response += line

            if not response:
                return False, "No response"

            # tenta converter para JSON
            try:
                parsed = json.loads(response)
                return True, parsed
            except Exception:
                return True, response  # devolve string bruta

        except Exception as e:
            return False, str(e)

    # ---------------- Comandos ----------------
    def get_status(self):
        return self.send("STATUS")

    def reset(self):
        return self.send("RESET")

    def spoof(self):
        return self.send("SPOOF")

    # ---------------- Perfis ----------------
    def load_profiles(self, filename="mouse_profiles/profiles.json"):
        """
        Carrega perfis de mouse.
        """
        try:
            if not os.path.exists(filename):
                print(f"[AVISO] Arquivo de perfis não encontrado: {filename}")
                return {}

            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERRO] Falha ao carregar perfis: {e}")
            return {}

    def get_profile(self, brand, model):
        profiles = self.load_profiles()
        return profiles.get(brand, {}).get(model)
