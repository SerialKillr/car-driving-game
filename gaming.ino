const int joyX = 34;
const int joyY = 35;
const int buzzerPin = 27;

void setup() {
  Serial.begin(115200);
  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW);
}

void loop() {
  // Check if Python sent BUZZ command
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "BUZZ") {
      digitalWrite(buzzerPin, HIGH);
      delay(1000);
      digitalWrite(buzzerPin, LOW);
    }
  }

  int xValue = analogRead(joyX);
  int yValue = analogRead(joyY);

  Serial.print(xValue);
  Serial.print(",");
  Serial.println(yValue);

  delay(25);
}
