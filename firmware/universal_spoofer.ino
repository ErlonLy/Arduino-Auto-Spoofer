#include <Arduino.h>
#include <Mouse.h>

#define BAUD_RATE 115200

void handleStatusCommand();
void handleSpoofCommand();
void handleResetCommand();

void setup() {
  Serial.begin(BAUD_RATE);
  Mouse.begin();

  while (!Serial) {
    delay(10);
  }

  Serial.println("{\"event\":\"ARDUINO_READY\",\"desc\":\"Universal Spoofer ativo\"}");
  Serial.println("{\"event\":\"COMMANDS\",\"list\":[\"AT\",\"AT+STATUS\",\"AT+SPOOF\",\"AT+RESET\",\"STATUS\",\"SPOOF\",\"RESET\"]}");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    command.toUpperCase();

    if (command == "AT") {
      Serial.println("{\"resp\":\"OK\"}");
    }
    else if (command == "AT+STATUS" || command == "STATUS") {
      handleStatusCommand();
    }
    else if (command == "AT+SPOOF" || command == "SPOOF") {
      handleSpoofCommand();
    }
    else if (command == "AT+RESET" || command == "RESET") {
      handleResetCommand();
    }
    else {
      Serial.print("{\"error\":\"Comando inválido: ");
      Serial.print(command);
      Serial.println("\"}");
    }
  }
}

void handleStatusCommand() {
  Serial.println("{\"status\":\"OK\",\"mode\":\"idle\"}");
}

void handleSpoofCommand() {
  for (int i = 0; i < 5; i++) {
    Mouse.move(10, 0, 0);
    delay(100);
    Mouse.move(-10, 0, 0);
    delay(100);
  }
  Serial.println("{\"status\":\"SPOOF_DONE\"}");
}

void handleResetCommand() {
  Serial.println("{\"status\":\"RESET\",\"action\":\"Reiniciando variáveis\"}");
}
