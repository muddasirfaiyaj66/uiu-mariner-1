const int ledPin = 9;  // LED pin
const int soilMoisturePin = A0;  // Soil moisture sensor pin

void setup() {
  Serial.begin(9600);  // Start serial communication
  pinMode(ledPin, OUTPUT);  // Set the LED pin as an output
}

void loop() {
  // Read the soil moisture sensor value
  int soilMoistureValue = analogRead(soilMoisturePin);
  Serial.println(soilMoistureValue);  // Send the value to PyQt6

  if (Serial.available() > 0) {
    int pwmValue = Serial.parseInt(); 
    if (pwmValue >= 0 && pwmValue <= 255) { 
      analogWrite(ledPin, pwmValue); 
    }
  }

  delay(30);  // Reduce the delay to make the loop more responsive
}
