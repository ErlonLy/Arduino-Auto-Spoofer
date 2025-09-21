#include <EEPROM.h>
#include <Mouse.h>


struct Config {
  uint16_t vid;
  uint16_t pid;
  char product_name[32];
  char manufacturer[32];
  bool configured;
};

Config config;


#ifndef USB_VID
#define USB_VID 0x2341
#endif

#ifndef USB_PID
#define USB_PID 0x8036
#endif

#ifndef USB_PRODUCT
#define USB_PRODUCT "Arduino Leonardo"
#endif

#ifndef USB_MANUFACTURER
#define USB_MANUFACTURER "Arduino"
#endif


void setup() {
  Serial.begin(115200);
  while (!Serial) { delay(10); }

  // Lê configuração da EEPROM
  EEPROM.get(0, config);

  if (!config.configured) {
    config.vid = USB_VID;
    config.pid = USB_PID;
    strncpy(config.product_name, USB_PRODUCT, sizeof(config.product_name));
    strncpy(config.manufacturer, USB_MANUFACTURER, sizeof(config.manufacturer));
    config.configured = true;
    EEPROM.put(0, config);
  }

  Mouse.begin();

  Serial.println("UNIVERSAL_SPOOFER_READY");
  printStatus();
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "STATUS") {
      printStatus();
    }
    else if (command.startsWith("SPOOF")) {
      handleSpoofCommand(command);
    }
    else if (command == "RESET") {
      resetToDefault();
    }
    else if (command == "SAVE") {
      EEPROM.put(0, config);
      Serial.println("CONFIG_SAVED");
      printStatus();
      Serial.println("Reiniciando para aplicar configuração...");
      delay(1000);
      setup();
    }
    else if (command == "TEST_MOUSE") {
      testMouseFunctions();
    }
    else {
      Serial.println("ERROR:UNKNOWN_COMMAND");
      Serial.println("Comandos disponíveis: STATUS, SPOOF, RESET, SAVE, TEST_MOUSE");
    }
  }

  // Mantém HID ativo
  static unsigned long lastMove = 0;
  if (millis() - lastMove > 5000) {
    Mouse.move(1, 0, 0);
    delay(10);
    Mouse.move(-1, 0, 0);
    lastMove = millis();
  }

  delay(50);
}

void printStatus() {
  Serial.print("STATUS:VID=0x");
  Serial.print(config.vid, HEX);
  Serial.print(",PID=0x");
  Serial.print(config.pid, HEX);
  Serial.print(",PRODUCT=");
  Serial.print(config.product_name);
  Serial.print(",MANUFACTURER=");
  Serial.println(config.manufacturer);
  Serial.println("HID_ACTIVE:YES");
}

void handleSpoofCommand(String command) {

  int firstSpace = command.indexOf(' ');
  if (firstSpace <= 0) {
    Serial.println("ERROR:INVALID_SPOOF_FORMAT");
    return;
  }

  String args = command.substring(firstSpace + 1);
  args.trim();
  int secondSpace = args.indexOf(' ');
  if (secondSpace <= 0) {
    Serial.println("ERROR:INVALID_SPOOF_FORMAT");
    return;
  }

  String vidStr = args.substring(0, secondSpace);
  String rest = args.substring(secondSpace + 1);
  rest.trim();

  int thirdSpace = rest.indexOf(' ');
  if (thirdSpace <= 0) {
    Serial.println("ERROR:INVALID_SPOOF_FORMAT");
    return;
  }

  String pidStr = rest.substring(0, thirdSpace);
  String remaining = rest.substring(thirdSpace + 1);
  remaining.trim();

  String product, manufacturer;
  int firstQuote = remaining.indexOf('"');
  if (firstQuote >= 0) {
    int secondQuote = remaining.indexOf('"', firstQuote + 1);
    if (secondQuote > firstQuote) {
      product = remaining.substring(firstQuote + 1, secondQuote);
      int nextQuote = remaining.indexOf('"', secondQuote + 1);
      if (nextQuote >= 0) {
        int lastQuote = remaining.indexOf('"', nextQuote + 1);
        if (lastQuote > nextQuote) {
          manufacturer = remaining.substring(nextQuote + 1, lastQuote);
        }
      }
    }
  }


  if (vidStr.startsWith("0x") || vidStr.startsWith("0X")) vidStr = vidStr.substring(2);
  if (pidStr.startsWith("0x") || pidStr.startsWith("0X")) pidStr = pidStr.substring(2);

  char *endptr;
  unsigned long vidLong = strtoul(vidStr.c_str(), &endptr, 16);
  if (*endptr != '\0') { Serial.println("ERROR:INVALID_VID"); return; }
  unsigned long pidLong = strtoul(pidStr.c_str(), &endptr, 16);
  if (*endptr != '\0') { Serial.println("ERROR:INVALID_PID"); return; }

  config.vid = (uint16_t)vidLong;
  config.pid = (uint16_t)pidLong;
  product.toCharArray(config.product_name, sizeof(config.product_name));
  manufacturer.toCharArray(config.manufacturer, sizeof(config.manufacturer));

  Serial.println("SPOOF_SUCCESS");
  printStatus();
  Serial.println("Execute SAVE para persistir e reiniciar");
}

void resetToDefault() {
  config.vid = USB_VID;
  config.pid = USB_PID;
  strncpy(config.product_name, USB_PRODUCT, sizeof(config.product_name));
  strncpy(config.manufacturer, USB_MANUFACTURER, sizeof(config.manufacturer));
  config.configured = true;
  EEPROM.put(0, config);

  Serial.println("RESET_SUCCESS");
  printStatus();
}

void testMouseFunctions() {
  Serial.println("TEST_MOUSE:Movimento e cliques...");
  Mouse.move(10, 0, 0); delay(500);
  Mouse.move(-10, 0, 0); delay(500);
  Mouse.click(MOUSE_LEFT); delay(300);
  Mouse.click(MOUSE_RIGHT); delay(300);
  Mouse.click(MOUSE_MIDDLE); delay(300);
  Serial.println("TEST_MOUSE:Concluído");
}
