# 🎯 Arduino Mouse Spoofer

Projeto feito para ajudar a comunidade, por favor deem estrelas ⭐ para esse projeto, assim me motiva a atualizar e criar novos.

---

## 🚀 Como rodar o projeto

### 1. Criar ambiente virtual
No terminal (dentro da pasta do projeto):

```bash
python -m venv .venv
```

### 2. Ativar ambiente virtual
- **Windows (PowerShell):**
  ```bash
  .venv\Scripts\Activate.ps1 ( ou entra na pasta .venv\Scripts\ arrasta e solta no terminal do vscode )
  ```
- **Windows (CMD):**
  ```bash
  .venv\Scripts\activate.bat
  ```
- **Linux/macOS:**
  ```bash
  source .venv/bin/activate
  ```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Rodar o programa
```bash
python main.py
```

---

## 📂 Estrutura do Projeto

```
Arduino-Auto-Spoofer/
│── main.py                # Interface principal (PyQt5)
│── requirements.txt       # Lista de dependências
│
├── utils/                 # Código auxiliar
│   ├── file_manager.py    # Manipula boards.txt (backup, restore, modificação)
│   ├── arduino_utils.py   # Funções de detecção de portas/Arduino
│   ├── spoof_engine.py    # Motor que aplica o spoof (gera e envia firmware)
│
├── firmware/              # Firmwares em C++ para Arduino
│   ├── universal_spoofer.ino
│   ├── blink_test.ino
│
├── boards_templates/      # Templates originais de boards.txt
│   └── boards.txt
│
├── backups/               # Backups automáticos do boards.txt
│
├── styles/                # Estilos visuais (themes Qt)
│   └── red_black_theme.py
```

---

## 📖 Descrição das pastas

- [**utils/**](utils) → Contém módulos em Python para manipulação de arquivos e lógica de spoof.  
- [**firmware/**](firmware) → Códigos Arduino (.ino) enviados ao microcontrolador.  
- [**boards_templates/**](boards_templates) → Template mínimo do `boards.txt` usado como base.  
- [**backups/**](backups) → Onde são salvos os backups do `boards.txt` antes de qualquer modificação.  
- [**styles/**](styles) → Estilos visuais (CSS/Qt) usados no frontend da aplicação.  

---

## ⚙️ Funcionalidades

- Detecta portas COM automaticamente.  
- Modifica o `boards.txt` com flags HID (VID/PID, fabricante e produto).  
- Envia firmware universal de spoof para o Arduino.  
- Permite restaurar `boards.txt` original a partir de backup.  
- Detecta rastros de spoof no arquivo do Arduino.  
- Força o reconhecimento de fabricante dos mouses

---

## 📌 Observações

- O projeto foi testado com **Arduino Leonardo R3** (ATmega32u4).  
- Para funcionamento correto, é necessário que o **Arduino IDE** ou **Arduino CLI** esteja instalado no sistema.  
- Projeto aberto para o público , então se quiser contribuir , é bem vinda a ajuda.
---

## 📝 Licença

Este projeto é apenas para fins educacionais.
