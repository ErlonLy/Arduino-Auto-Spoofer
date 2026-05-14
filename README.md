# Arduino Mouse Spoofer

Este projeto foi desenvolvido para auxiliar a comunidade. Caso considere este trabalho útil, agradecemos se puder deixar uma estrela no repositório, o que motiva o desenvolvimento de novas atualizações e projetos.

---

## Instruções de Instalação e Execução

### 1. Criação do Ambiente Virtual
No terminal, dentro do diretório do projeto, execute:

```bash
python -m venv .venv
```

### 2. Ativação do Ambiente Virtual
- **Windows (PowerShell):**
  ```bash
  .venv\Scripts\Activate.ps1
  ```
- **Windows (CMD):**
  ```bash
  .venv\Scripts\activate.bat
  ```
- **Linux/macOS:**
  ```bash
  source .venv/bin/activate
  ```

### 3. Instalação de Dependências
```bash
pip install -r requirements.txt
```

### 4. Inicialização da Aplicação
```bash
python main.py
```

---

## Estrutura do Projeto

```
Arduino-Auto-Spoofer/
├── main.py                # Interface principal (PyQt5)
├── requirements.txt       # Lista de dependências
├── utils/                 # Módulos auxiliares
│   ├── file_manager.py    # Gerenciamento de boards.txt (backup, restauração, modificação)
│   ├── arduino_utils.py   # Detecção de hardware e portas seriais
│   ├── spoof_engine.py    # Motor de aplicação de spoof e comunicação com firmware
├── firmware/              # Código fonte C++ para Arduino
│   ├── universal_spoofer.ino
│   ├── blink_test.ino
├── boards_templates/      # Modelos de configuração para boards.txt
│   └── boards.txt
├── backups/               # Armazenamento de backups automáticos
└── styles/                # Definições de temas visuais (Qt)
    └── red_black_theme.py
```

---

## Descrição dos Componentes

- **utils/**: Módulos Python responsáveis pela lógica de negócio e manipulação de arquivos.
- **firmware/**: Códigos fonte para microcontroladores Arduino (.ino).
- **boards_templates/**: Contém o arquivo base para as modificações de hardware.
- **backups/**: Diretório destinado à preservação dos arquivos originais antes de modificações.
- **styles/**: Arquivos de estilização para a interface gráfica.

---

## Funcionalidades Principais

- Detecção automática de portas de comunicação (COM).
- Modificação dinâmica do arquivo `boards.txt` com parâmetros HID (VID/PID, Fabricante e Produto).
- Implementação de firmware universal para spoof em dispositivos Arduino.
- Funcionalidade de restauração do estado original do sistema através de backups.
- Verificação de integridade e detecção de modificações prévias nos arquivos de configuração.
- Otimização do reconhecimento de hardware para periféricos de entrada.

---

## Requisitos Técnicos

- Compatível com **Arduino Leonardo R3** (ATmega32u4).
- Requer a instalação prévia do **Arduino IDE** ou **Arduino CLI** no sistema operacional.
- O projeto é de código aberto e contribuições são incentivadas.

---

## Termos de Uso e Licença

Este software é fornecido estritamente para fins educacionais e de pesquisa. O uso inadequado desta ferramenta é de inteira responsabilidade do usuário.
