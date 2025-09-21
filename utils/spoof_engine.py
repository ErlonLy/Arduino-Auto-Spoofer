import os
import subprocess
import json


class SpoofEngine:
    def __init__(self, serial_tool_path="utils/serial_tool.exe"):
        self.serial_tool_path = serial_tool_path
        self.port = None
        self.profiles = self.load_profiles()

    def load_profiles(self, file_path=None):
        try:
            if file_path is None:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(base_dir, "..", "mouse_profiles", "profiles.json")

            file_path = os.path.abspath(file_path)

            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                print(f"[SpoofEngine] Arquivo não encontrado: {file_path}")
                return {}
        except Exception as e:
            print(f"[SpoofEngine] Erro ao carregar perfis: {e}")
            return {}

    def get_profile(self, brand, model):
        return self.profiles.get(brand, {}).get(model, None)

    def run_tool(self, args):
        try:
            cmd = [self.serial_tool_path] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout.strip()
            error = result.stderr.strip()

            if error:
                return False, error
            if result.returncode != 0:
                return False, output

            return True, output
        except subprocess.TimeoutExpired:
            return False, "Timeout ao comunicar com serial_tool"
        except Exception as e:
            return False, str(e)

    def verify(self, port):
        ok, resp = self.run_tool(["verify", port])
        if not ok:
            return "ERRO", resp

        if "OK" in resp:
            return "AT", resp
        elif "passivo" in resp.lower():
            return "PASSIVO", resp
        else:
            return "ERRO", resp

    def get_status(self, port):
        ok, resp = self.run_tool(["status", port])
        return resp if ok else f"ERRO: {resp}"

    def spoof(self, port, vid, pid):
        ok, resp = self.run_tool(["spoof", port, vid, pid])
        return resp if ok else f"ERRO: {resp}"

    def reset(self, port):
        ok, resp = self.run_tool(["reset", port])
        return resp if ok else f"ERRO: {resp}"
