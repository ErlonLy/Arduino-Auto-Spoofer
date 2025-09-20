#include <Arduino.h>
#include <avr/wdt.h>  // para reset via watchdog

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    ; // espera USB conectar
  }
  Serial.println("{\"status\":\"READY\",\"fw\":\"reset_only\"}");
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    cmd.toUpperCase();

    if (cmd == "STATUS") {
      Serial.println("{\"status\":\"OK\",\"fw\":\"reset_only\"}");
    }
    else if (cmd == "RESET") {
      Serial.println("{\"reset\":\"executing\"}");
      delay(100);
      wdt_enable(WDTO_15MS);  // ativa watchdog para reset
      while (1) {}            // trava até reset
    }
    else {
      Serial.println("{\"error\":\"unknown_command\"}");
    }
  }
}
