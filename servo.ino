#include <Servo.h>

Servo servoMotor;
const int servoPin = 9;

void setup() {
  servoMotor.attach(servoPin);

  int centerServoAngle = map(-20, -60, 60, 0, 180);
  servoMotor.write(centerServoAngle);
}

void loop() {
}
