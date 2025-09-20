import os
import shutil
import subprocess
from datetime import datetime


class FileManager:
    def __init__(self):
        self.backup_dir = "backups"
        os.makedirs(self.backup_dir, exist_ok=True)

    def _find_boards_file(self, arduino_path):
        """
        Procura o boards.txt dentro do caminho fornecido (recursivamente).
        Exemplo válido:
        .../Arduino15/packages/arduino/hardware/avr/1.8.6/boards.txt
        """
        # Primeiro procura no caminho específico do Arduino AVR
        possible_paths = [
            os.path.join(arduino_path, "packages", "arduino", "hardware", "avr"),
            os.path.join(arduino_path, "hardware", "arduino", "avr"),
            arduino_path  # Busca recursivamente como fallback
        ]
        
        for base_path in possible_paths:
            if os.path.exists(base_path):
                for root, dirs, files in os.walk(base_path):
                    if "boards.txt" in files:
                        return os.path.join(root, "boards.txt")
        return None

    def backup_boards_file(self, arduino_path):
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

    def get_latest_backup(self):
        try:
            backups = sorted(
                [
                    os.path.join(self.backup_dir, f)
                    for f in os.listdir(self.backup_dir)
                    if f.endswith(".txt") and "boards_" in f
                ],
                key=os.path.getmtime,
                reverse=True,
            )
            return backups[0] if backups else None
        except Exception as e:
            print(f"❌ Erro ao buscar backups: {e}")
            return None

    def modify_boards_file(self, arduino_path, profile):
        """
        Atualiza boards.txt do Leonardo para emular outro dispositivo (spoof).
        - Substitui build.vid / build.pid / build.usb_product / build.usb_manufacturer
        - Substitui todas as entradas leonardo.vid.N e leonardo.pid.N
        - Atualiza também upload_port.*
        - Modifica o nome da placa
        """
        try:
            boards_path = self._find_boards_file(arduino_path)
            if not boards_path:
                print("⚠️ boards.txt não encontrado para modificação")
                return False

            print(f"📝 Modificando boards.txt em: {boards_path}")
            
            with open(boards_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            prefix = "leonardo"
            new_lines = []
            in_leonardo_block = False
            touched = {
                "name": False, 
                "vid": False, 
                "pid": False, 
                "product": False,
                "manufacturer": False
            }

            for line in lines:
                stripped_line = line.strip()
                
                # Detecta início do bloco leonardo
                if line.startswith("leonardo.name="):
                    in_leonardo_block = True
                    # Atualiza o nome da placa
                    new_lines.append(f"leonardo.name={profile.get('name', 'Logitech G502 HERO')}\n")
                    touched["name"] = True
                    continue
                
                # Detecta fim do bloco leonardo
                if in_leonardo_block and stripped_line == "":
                    in_leonardo_block = False
                
                # Processa linhas dentro do bloco leonardo
                if in_leonardo_block:
                    # Modifica VID e PID em todas as variantes
                    if line.startswith("leonardo.vid."):
                        new_lines.append(f"{line.split('=')[0]}={profile['vid']}\n")
                        touched["vid"] = True
                        continue
                    elif line.startswith("leonardo.pid."):
                        new_lines.append(f"{line.split('=')[0]}={profile['pid']}\n")
                        touched["pid"] = True
                        continue
                    elif line.startswith("leonardo.upload_port."):
                        if ".vid=" in line:
                            new_lines.append(f"{line.split('=')[0]}={profile['vid']}\n")
                        elif ".pid=" in line:
                            new_lines.append(f"{line.split('=')[0]}={profile['pid']}\n")
                        else:
                            new_lines.append(line)
                        continue
                    elif line.startswith(f"{prefix}.build.vid"):
                        new_lines.append(f"{prefix}.build.vid={profile['vid']}\n")
                        touched["vid"] = True
                        continue
                    elif line.startswith(f"{prefix}.build.pid"):
                        new_lines.append(f"{prefix}.build.pid={profile['pid']}\n")
                        touched["pid"] = True
                        continue
                    elif line.startswith(f"{prefix}.build.usb_product"):
                        new_lines.append(f'{prefix}.build.usb_product="{profile["product"]}"\n')
                        touched["product"] = True
                        continue
                    elif line.startswith(f"{prefix}.build.usb_manufacturer"):
                        new_lines.append(f'{prefix}.build.usb_manufacturer="{profile.get("manufacturer", "Logitech")}"\n')
                        touched["manufacturer"] = True
                        continue
                    elif line.startswith(f"{prefix}.build.extra_flags"):
                        if "extra_flags" in profile and profile["extra_flags"]:
                            new_lines.append(
                                f"{prefix}.build.extra_flags={{build.usb_flags}} {profile['extra_flags']}\n"
                            )
                        else:
                            new_lines.append(f"{prefix}.build.extra_flags={{build.usb_flags}}\n")
                        continue
                
                new_lines.append(line)

            # Adiciona linhas que não existiam no arquivo original
            if not touched["name"]:
                new_lines.append(f"leonardo.name={profile.get('name', 'Logitech G502 HERO')}\n")
            
            if not touched["vid"]:
                new_lines.append(f"{prefix}.build.vid={profile['vid']}\n")
            
            if not touched["pid"]:
                new_lines.append(f"{prefix}.build.pid={profile['pid']}\n")
            
            if not touched["product"]:
                new_lines.append(f'{prefix}.build.usb_product="{profile["product"]}"\n')
            
            if not touched["manufacturer"]:
                new_lines.append(f'{prefix}.build.usb_manufacturer="{profile.get("manufacturer", "Logitech")}"\n')

            # Escreve o arquivo modificado
            with open(boards_path, "w", encoding="utf-8", errors="ignore") as f:
                f.writelines(new_lines)

            # Limpa o cache do arduino-cli
            self._clean_arduino_cache()
            
            print("✅ boards.txt modificado com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao modificar boards.txt: {e}")
            return False

    def _clean_arduino_cache(self):
        """Limpa o cache do Arduino CLI para garantir que as mudanças tenham efeito"""
        try:
            cli_path = os.path.join("utils", "arduino-cli.exe")
            cli_path = os.path.abspath(cli_path)
            if os.path.exists(cli_path):
                result = subprocess.run([cli_path, "cache", "clean"], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    print("✅ Cache do arduino-cli limpo")
                else:
                    print(f"⚠️ Cache clean retornou código {result.returncode}")
            else:
                print("⚠️ arduino-cli.exe não encontrado para limpar cache")
        except subprocess.TimeoutExpired:
            print("⚠️ Timeout ao limpar cache do arduino-cli")
        except Exception as e:
            print(f"⚠️ Erro ao limpar cache: {e}")

    def verify_modification(self, arduino_path, expected_vid, expected_pid):
        """
        Verifica se as modificações no boards.txt foram aplicadas corretamente
        """
        try:
            boards_path = self._find_boards_file(arduino_path)
            if not boards_path:
                return False, "Arquivo boards.txt não encontrado"
            
            with open(boards_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Verifica se os valores esperados estão presentes
            vid_correct = f"build.vid={expected_vid}" in content
            pid_correct = f"build.pid={expected_pid}" in content
            vid_entries = content.count(f"vid={expected_vid}")
            pid_entries = content.count(f"pid={expected_pid}")
            
            return (vid_correct and pid_correct, 
                   f"VID: {vid_correct} ({vid_entries} entradas), PID: {pid_correct} ({pid_entries} entradas)")
                   
        except Exception as e:
            return False, f"Erro na verificação: {str(e)}"