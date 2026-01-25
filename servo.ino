#include <Servo.h>

Servo servo1;

Servo servoMotor;
const int servoPin = 9;
int pos = 0;

void setup() {
  servo1.attach(9);  // Attach servo1 to digital pin 9
  Serial.begin(9600); // Initialize serial comm at 9600 baud
}

void loop() {
  if (Serial.available() > 0) {
    pos = Serial.read(); // Read the incoming byte (angle)
    servo1.write(pos);   // Set the servo position
    }
  }
