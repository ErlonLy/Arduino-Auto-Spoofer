#include <Mouse.h>

void setup() {
  Serial.begin(115200);
  Mouse.begin();
  
  // Aguarda conexão serial
  while (!Serial) {
    delay(10);
  }
  
  Serial.println("ARDUINO_SPOOFER_READY");
  Serial.println("Comandos disponíveis:");
  Serial.println("SPOOF - Inicia spoofing");
  Serial.println("STATUS - Verifica status");
  Serial.println("RESET - Reseta para padrão");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readString();
    command.trim();
    command.toUpperCase();
    
    if (command == "SPOOF") {
      handleSpoofCommand();
    }
    else if (command == "STATUS") {
      Serial.println("STATUS_OK");
    }
    else if (command == "RESET") {
      handleResetCommand();
    }
    else {
      Serial.println("COMANDO_INVALIDO");
    }
  }
  
  delay(100);
}

void handleSpoofCommand() {
  Serial.println("SPOOFING_INICIADO");
  
  // Simula movimento de mouse (exemplo)
  for (int i = 0; i < 5; i++) {
    Mouse.move(10, 0);
    delay(50);
    Mouse.move(-10, 0);
    delay(50);
  }
  
  Serial.println("SPOOFING_CONCLUIDO");
}

void handleResetCommand() {
  Serial.println("RESET_INICIADO");
  // Aqui viria a lógica de reset
  Serial.println("RESET_CONCLUIDO");
}