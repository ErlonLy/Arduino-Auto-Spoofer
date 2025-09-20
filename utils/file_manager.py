import os
import shutil
from datetime import datetime


class FileManager:
    def __init__(self, backup_dir="backups"):
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)

    def backup_boards_file(self, arduino_path):
        """
        Faz backup do boards.txt em backups/ com timestamp.
        """
        try:
            boards_file = os.path.join(arduino_path, "hardware", "arduino", "avr", "boards.txt")
            if not os.path.exists(boards_file):
                return None

            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            backup_name = f"boards_{timestamp}.txt"
            backup_file = os.path.join(self.backup_dir, backup_name)

            shutil.copy2(boards_file, backup_file)
            return backup_file
        except Exception as e:
            print(f"[ERRO] Falha no backup: {e}")
            return None

    def restore_backup(self, backup_file, arduino_path):
        """
        Restaura um backup específico para boards.txt.
        """
        try:
            boards_file = os.path.join(arduino_path, "hardware", "arduino", "avr", "boards.txt")
            if not os.path.exists(backup_file):
                return False

            shutil.copy2(backup_file, boards_file)
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao restaurar backup: {e}")
            return False

    def get_latest_backup(self):
        """
        Retorna o backup mais recente em backups/.
        """
        try:
            backups = [
                os.path.join(self.backup_dir, f)
                for f in os.listdir(self.backup_dir)
                if f.startswith("boards_") and f.endswith(".txt")
            ]
            if not backups:
                return None
            backups.sort(key=os.path.getmtime, reverse=True)
            return backups[0]
        except Exception as e:
            print(f"[ERRO] Não foi possível localizar backups: {e}")
            return None

    def modify_boards_file(self, arduino_path, mouse_profile):
        """
        Exemplo de modificação simples no boards.txt (pode ser expandido).
        Substitui/add algumas linhas de configuração conforme mouse_profile.
        """
        try:
            boards_file = os.path.join(arduino_path, "hardware", "arduino", "avr", "boards.txt")
            if not os.path.exists(boards_file):
                return False

            with open(boards_file, "a", encoding="utf-8") as f:
                f.write("\n# Spoofer Profile\n")
                f.write(f"{mouse_profile['vendor']} {mouse_profile['product']}\n")

            return True
        except Exception as e:
            print(f"[ERRO] Falha ao modificar boards.txt: {e}")
            return False
