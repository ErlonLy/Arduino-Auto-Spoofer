import os
import shutil
import subprocess
from datetime import datetime


class FileManager:
    def __init__(self):
        self.backup_dir = "backups"
        os.makedirs(self.backup_dir, exist_ok=True)
        # Template mínimo do boards.txt
        self.template_file = os.path.join("boards_templates", "boards.txt")

    def _find_boards_file(self, arduino_path):
        """
        Localiza boards.txt dentro do Arduino AVR
        """
        possible_paths = [
            os.path.join(arduino_path, "packages", "arduino", "hardware", "avr"),
            os.path.join(arduino_path, "hardware", "arduino", "avr"),
            arduino_path
        ]
        for base_path in possible_paths:
            if os.path.exists(base_path):
                for root, _, files in os.walk(base_path):
                    if "boards.txt" in files:
                        return os.path.join(root, "boards.txt")
        return None

    def backup_boards_file(self, arduino_path):
        """
        Copia o boards.txt original para a pasta de backups
        """
        try:
            boards_path = self._find_boards_file(arduino_path)
            if not boards_path:
                print("⚠️ boards.txt não encontrado para backup")
                return None
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"boards_{timestamp}.txt")
            shutil.copy2(boards_path, backup_file)
            print(f"✅ Backup criado: {backup_file}")
            return backup_file
        except Exception as e:
            print(f"❌ Erro no backup: {e}")
            return None

    def restore_backup(self, backup_file, arduino_path):
        """
        Restaura um backup anterior
        """
        try:
            boards_path = self._find_boards_file(arduino_path)
            if not boards_path:
                print("⚠️ boards.txt não encontrado para restauração")
                return False
            shutil.copy2(backup_file, boards_path)
            print(f"✅ Backup restaurado: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ Erro na restauração: {e}")
            return False

    def modify_boards_file(self, arduino_path, profile):
        """
        Substitui o boards.txt do usuário pelo template mínimo
        e injeta apenas as extra_flags.
        """
        try:
            boards_path = self._find_boards_file(arduino_path)
            if not boards_path:
                print("⚠️ boards.txt não encontrado para modificação")
                return False

            if not os.path.exists(self.template_file):
                print(f"⚠️ Template não encontrado: {self.template_file}")
                return False

            # Lê template base
            with open(self.template_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Monta extra_flags
            flags = []
            if profile.get("force_vid_pid", False):
                flags.append(f"-DUSB_VID={profile['vid']} -DUSB_PID={profile['pid']}")
            if profile.get("force_product_manufacturer", False):
                usb_product = profile.get("usb_product", profile.get("product", "Arduino Leonardo"))
                usb_manufacturer = profile.get("usb_manufacturer", profile.get("manufacturer", "Arduino"))
                # Mantém espaços, mas envolve em aspas para string literal válida
                flags.append(f'-DUSB_PRODUCT="{usb_product}"')
                flags.append(f'-DUSB_MANUFACTURER="{usb_manufacturer}"')

            extra_flags = " ".join(flags)

            # Substitui placeholder {EXTRA_FLAGS}
            content = content.replace("{EXTRA_FLAGS}", extra_flags)

            # Backup do boards.txt atual
            self.backup_boards_file(arduino_path)

            # Escreve no boards.txt real
            with open(boards_path, "w", encoding="utf-8") as f:
                f.write(content)

            self._clean_arduino_cache()
            print("✅ boards.txt atualizado com sucesso (via template mínimo)")
            return True
        except Exception as e:
            print(f"❌ Erro detalhado ao modificar boards.txt: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _clean_arduino_cache(self):
        """
        Limpa cache do Arduino CLI
        """
        try:
            cli_path = os.path.join("utils", "arduino-cli.exe")
            if os.path.exists(cli_path):
                subprocess.run([cli_path, "cache", "clean"], timeout=30)

            temp_dirs = [
                os.path.join(os.environ.get('TEMP', ''), 'arduino', 'sketches'),
                os.path.join(os.environ.get('TEMP', ''), 'arduino', 'cores'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp', 'arduino', 'sketches'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp', 'arduino', 'cores')
            ]

            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    print(f"🧹 Diretório temporário limpo: {temp_dir}")

        except Exception as e:
            print(f"⚠️ Erro ao limpar cache: {e}")

    def verify_modification(self, arduino_path, expected_vid, expected_pid):
        """
        Confere se boards.txt foi modificado corretamente
        """
        try:
            boards_path = self._find_boards_file(arduino_path)
            if not boards_path:
                return False, "Arquivo boards.txt não encontrado"

            with open(boards_path, "r", encoding="utf-8") as f:
                content = f.read()

            vid_ok = f"-DUSB_VID={expected_vid}" in content
            pid_ok = f"-DUSB_PID={expected_pid}" in content
            return (vid_ok and pid_ok, f"VID OK: {vid_ok}, PID OK: {pid_ok}")
        except Exception as e:
            return False, f"Erro na verificação: {str(e)}"

    # ---------------- NOVA FUNÇÃO ----------------
    def check_spoof_trace(self, arduino_path):
        """
        Verifica se o bloco do Leonardo no boards.txt está idêntico ao padrão de fábrica.
        Se houver qualquer diferença ou flags extras → rastro de spoofer detectado.
        """
        factory_block = {
            "leonardo.name": "Arduino Leonardo",
            "leonardo.vid.0": "0x2341",
            "leonardo.pid.0": "0x0036",
            "leonardo.vid.1": "0x2341",
            "leonardo.pid.1": "0x8036",
            "leonardo.vid.2": "0x2A03",
            "leonardo.pid.2": "0x0036",
            "leonardo.vid.3": "0x2A03",
            "leonardo.pid.3": "0x8036",
            "leonardo.upload_port.0.vid": "0x2341",
            "leonardo.upload_port.0.pid": "0x0036",
            "leonardo.upload_port.1.vid": "0x2341",
            "leonardo.upload_port.1.pid": "0x8036",
            "leonardo.upload_port.2.vid": "0x2A03",
            "leonardo.upload_port.2.pid": "0x0036",
            "leonardo.upload_port.3.vid": "0x2A03",
            "leonardo.upload_port.3.pid": "0x8036",
            "leonardo.upload_port.4.board": "leonardo",
            "leonardo.upload.tool": "avrdude",
            "leonardo.upload.tool.default": "avrdude",
            "leonardo.upload.tool.network": "arduino_ota",
            "leonardo.upload.protocol": "avr109",
            "leonardo.upload.maximum_size": "28672",
            "leonardo.upload.maximum_data_size": "2560",
            "leonardo.upload.speed": "57600",
            "leonardo.upload.disable_flushing": "true",
            "leonardo.upload.use_1200bps_touch": "true",
            "leonardo.upload.wait_for_upload_port": "true",
            "leonardo.bootloader.tool": "avrdude",
            "leonardo.bootloader.tool.default": "avrdude",
            "leonardo.bootloader.low_fuses": "0xff",
            "leonardo.bootloader.high_fuses": "0xd8",
            "leonardo.bootloader.extended_fuses": "0xcb",
            "leonardo.bootloader.file": "caterina/Caterina-Leonardo.hex",
            "leonardo.bootloader.unlock_bits": "0x3F",
            "leonardo.bootloader.lock_bits": "0x2F",
            "leonardo.build.mcu": "atmega32u4",
            "leonardo.build.f_cpu": "16000000L",
            "leonardo.build.vid": "0x2341",
            "leonardo.build.pid": "0x8036",
            "leonardo.build.usb_product": "\"Arduino Leonardo\"",
            "leonardo.build.board": "AVR_LEONARDO",
            "leonardo.build.core": "arduino",
            "leonardo.build.variant": "leonardo",
            "leonardo.build.extra_flags": "{build.usb_flags}"
        }

        boards_path = self._find_boards_file(arduino_path)
        if not boards_path or not os.path.exists(boards_path):
            return False, "boards.txt não encontrado"

        with open(boards_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip().startswith("leonardo.")]

        for line in lines:
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()
            if key not in factory_block:
                return True, f"⚠️ Rastro detectado: chave extra '{key}'"
            if key == "leonardo.build.extra_flags":
                if value != "{build.usb_flags}":
                    return True, f"⚠️ Rastro detectado: extra_flags adulterado → {value}"
            elif value != factory_block[key]:
                return True, f"⚠️ Rastro detectado: {key} esperado '{factory_block[key]}', encontrado '{value}'"

        return False, "✅ boards.txt está no padrão original"

