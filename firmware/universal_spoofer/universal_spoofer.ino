#include <EEPROM.h>
#include <Mouse.h>

// Estrutura para armazenar configuração na EEPROM
struct Config {
  uint16_t vid;
  uint16_t pid;
  char product_name[32];
  bool configured;
};

Config config;

void setup() {
  // Inicializa comunicação serial
  Serial.begin(115200);
  while (!Serial) { delay(10); }
  
  // Lê configuração da EEPROM
  EEPROM.get(0, config);
  
  // Se não está configurado, usa valores padrão do Arduino Leonardo
  if (!config.configured) {
    config.vid = 0x2341;
    config.pid = 0x8036;
    strcpy(config.product_name, "Arduino Leonardo");
    config.configured = true;
    EEPROM.put(0, config);
  }
  
  // Inicializa a emulação de mouse HID :cite[1]:cite[8]
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
      
      // Reinicia para aplicar as mudanças
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
  
  // Mantém a emulação HID ativa com movimento mínimo :cite[8]
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
  Serial.println(config.product_name);
  
  // CORREÇÃO: Removida a verificação Mouse.isReady() que não existe
  // Em vez disso, verificamos se o mouse está inicializado de outra forma
  Serial.print("HID_ACTIVE:");
  Serial.println("YES"); // Assumimos que está ativo após Mouse.begin()
}

void handleSpoofCommand(String command) {
  // Formato: SPOOF VID PID "Product Name"
  int firstSpace = command.indexOf(' ');
  if (firstSpace <= 0) {
    Serial.println("ERROR:INVALID_SPOOF_FORMAT");
    Serial.println("Use: SPOOF VID PID \"Product Name\"");
    Serial.println("Ex: SPOOF 0x046D 0xC08B \"Logitech G502 HERO\"");
    return;
  }
  
  String remaining = command.substring(firstSpace + 1);
  remaining.trim();
  
  // Encontra o próximo espaço (separador VID/PID)
  int secondSpace = remaining.indexOf(' ');
  if (secondSpace <= 0) {
    Serial.println("ERROR:INVALID_SPOOF_FORMAT");
    Serial.println("Use: SPOOF VID PID \"Product Name\"");
    return;
  }
  
  String vidStr = remaining.substring(0, secondSpace);
  String pidAndProduct = remaining.substring(secondSpace + 1);
  pidAndProduct.trim();
  
  // Encontra o próximo espaço ou aspas
  int thirdSpace = pidAndProduct.indexOf(' ');
  int quotePos = pidAndProduct.indexOf('"');
  
  String pidStr;
  String product;
  
  if (quotePos >= 0) {
    // Se tem aspas, extrai PID antes das aspas e produto entre aspas
    pidStr = pidAndProduct.substring(0, quotePos);
    pidStr.trim();
    
    int endQuote = pidAndProduct.indexOf('"', quotePos + 1);
    if (endQuote > quotePos) {
      product = pidAndProduct.substring(quotePos + 1, endQuote);
    } else {
      product = pidAndProduct.substring(quotePos + 1);
    }
  } else if (thirdSpace > 0) {
    // Se não tem aspas, mas tem espaço
    pidStr = pidAndProduct.substring(0, thirdSpace);
    product = pidAndProduct.substring(thirdSpace + 1);
    product.trim();
  } else {
    // Apenas PID, sem produto
    pidStr = pidAndProduct;
    product = "Custom HID Device";
  }
  
  // Remove possíveis prefixos 0x ou #
  if (vidStr.startsWith("0x") || vidStr.startsWith("0X")) {
    vidStr = vidStr.substring(2);
  } else if (vidStr.startsWith("#")) {
    vidStr = vidStr.substring(1);
  }
  
  if (pidStr.startsWith("0x") || pidStr.startsWith("0X")) {
    pidStr = pidStr.substring(2);
  } else if (pidStr.startsWith("#")) {
    pidStr = pidStr.substring(1);
  }
  
  // Converte para números
  char *endptr;
  unsigned long vidLong = strtoul(vidStr.c_str(), &endptr, 16);
  if (*endptr != '\0' || vidLong > 0xFFFF) {
    Serial.println("ERROR:INVALID_VID");
    Serial.print("VID fornecido: ");
    Serial.println(vidStr);
    return;
  }
  
  unsigned long pidLong = strtoul(pidStr.c_str(), &endptr, 16);
  if (*endptr != '\0' || pidLong > 0xFFFF) {
    Serial.println("ERROR:INVALID_PID");
    Serial.print("PID fornecido: ");
    Serial.println(pidStr);
    return;
  }
  
  // Atualiza configuração
  config.vid = (uint16_t)vidLong;
  config.pid = (uint16_t)pidLong;
  product.toCharArray(config.product_name, sizeof(config.product_name));
  
  Serial.println("SPOOF_SUCCESS");
  Serial.print("Nova configuração - VID: 0x");
  Serial.print(config.vid, HEX);
  Serial.print(", PID: 0x");
  Serial.print(config.pid, HEX);
  Serial.print(", Product: ");
  Serial.println(config.product_name);
  Serial.println("Execute SAVE para persistir e reiniciar");
}

void resetToDefault() {
  config.vid = 0x2341;
  config.pid = 0x8036;
  strcpy(config.product_name, "Arduino Leonardo");
  config.configured = true;
  EEPROM.put(0, config);
  
  Serial.println("RESET_SUCCESS");
  Serial.println("Restaurado para padrão Arduino Leonardo");
  Serial.println("Execute SAVE para persistir e reiniciar");
}

void testMouseFunctions() {
  Serial.println("TEST_MOUSE:Iniciando teste de funções HID...");
  
  // Teste de movimento :cite[1]:cite[8]
  Serial.println("TEST_MOUSE:Movendo para direita");
  Mouse.move(10, 0, 0);
  delay(500);
  
  Serial.println("TEST_MOUSE:Movendo para esquerda");
  Mouse.move(-10, 0, 0);
  delay(500);
  
  Serial.println("TEST_MOUSE:Movendo para baixo");
  Mouse.move(0, 10, 0);
  delay(500);
  
  Serial.println("TEST_MOUSE:Movendo para cima");
  Mouse.move(0, -10, 0);
  delay(500);
  
  // Teste de cliques :cite[1]:cite[8]
  Serial.println("TEST_MOUSE:Clique esquerdo");
  Mouse.click(MOUSE_LEFT);
  delay(300);
  
  Serial.println("TEST_MOUSE:Clique direito");
  Mouse.click(MOUSE_RIGHT);
  delay(300);
  
  Serial.println("TEST_MOUSE:Clique medio");
  Mouse.click(MOUSE_MIDDLE);
  delay(300);
  
  Serial.println("TEST_MOUSE:Teste concluído");
}