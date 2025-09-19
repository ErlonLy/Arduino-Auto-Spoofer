#include <Mouse.h>

void setup() {
  Serial.begin(115200);
  Mouse.begin();
  
  // Aguarda conexão serial (apenas para Leonardo/Micro)
  #if defined(__AVR_ATmega32U4__)
    while (!Serial) {
      delay(10);
    }
  #endif
  
  Serial.println("ARDUINO_SPOOFER_READY");
  Serial.println("Comandos AT disponíveis:");
  Serial.println("AT          - Teste de comunicação");
  Serial.println("AT+STATUS   - Status do dispositivo");
  Serial.println("AT+SPOOF    - Iniciar spoofing");
  Serial.println("AT+RESET    - Resetar configurações");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readString();
    command.trim();
    command.toUpperCase();
    
    // Comandos AT
    if (command == "AT") {
      Serial.println("OK");
    }
    else if (command == "AT+STATUS") {
      handleStatusCommand();
    }
    else if (command == "AT+SPOOF") {
      handleSpoofCommand();
    }
    else if (command == "AT+RESET") {
      handleResetCommand();
    }
    else if (command.startsWith("AT+PID")) {
      handlePIDCommand(command);
    }
    else if (command.startsWith("AT+HID")) {
      handleHIDCommand(command);
    }
    else {
      Serial.println("ERROR:COMANDO_INVALIDO");
    }
  }
  
  delay(50);
}

void handleStatusCommand() {
  Serial.println("STATUS:OK");
  Serial.println("VID:0x2341");
  Serial.println("PID:0x8036");
  Serial.println("MODEL:ARDUINO_MICRO");
  Serial.println("READY:TRUE");
}

void handleSpoofCommand() {
  Serial.println("SPOOF:INICIADO");
  
  // Simulação de spoofing
  for (int i = 0; i < 3; i++) {
    Mouse.move(5, 0);
    delay(100);
    Mouse.move(-5, 0);
    delay(100);
    Serial.print(".");
  }
  
  Serial.println("\nSPOOF:CONCLUIDO");
}

void handleResetCommand() {
  Serial.println("RESET:INICIADO");
  // Aqui viria a lógica de reset
  delay(500);
  Serial.println("RESET:CONCLUIDO");
}

void handlePIDCommand(String command) {
  if (command.length() > 6) {
    String newPID = command.substring(6);
    newPID.trim();
    Serial.print("PID_SET:");
    Serial.println(newPID);
  } else {
    Serial.println("ERROR:PID_INVALIDO");
  }
}

void handleHIDCommand(String command) {
  if (command.length() > 6) {
    String newHID = command.substring(6);
    newHID.trim();
    Serial.print("HID_SET:");
    Serial.println(newHID);
  } else {
    Serial.println("ERROR:HID_INVALIDO");
  }
}