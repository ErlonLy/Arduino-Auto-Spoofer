void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  while (!Serial) { delay(10); }
  Serial.println("BLINK_TEST_READY");
}

void loop() {
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.println("LED ON");
    delay(1000);
    digitalWrite(LED_BUILTIN, LOW);
    Serial.println("LED OFF");
    delay(1000);
  }
  Serial.println("TEST_COMPLETE");
  while (true) { delay(1000); } // trava depois do teste
}