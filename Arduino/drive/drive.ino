#include <Car_Library.h>

int motor_dir_con1 = 2;
int motor_dir_con2 = 3;
int potPin = A0;      // Pin for the potentiometer
int motor_left1 = 4;
int motor_left2 = 5;
int motor_right1 = 6;
int motor_right2 = 7;

#define DELAY 10
#define TOLERANCE 2

#define FORWARD_ANGLE 517
#define ANGLE2 30
#define ANGLE6 28
#define ANGLE7 62
#define ANGLE1 59
#define ANGLE35 18
#define MOTOR_SPEED 170

void motor_left(int motorSpeed){
  motor_backward(motor_dir_con1, motor_dir_con2, motorSpeed);
}

void motor_right(int motorSpeed){
  motor_forward(motor_dir_con1, motor_dir_con2, motorSpeed);
}

void setup() {
  Serial.begin(9600);
  // setup motor pins
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(A0, INPUT);  
  pinMode(motor_left1, OUTPUT);
  pinMode(motor_left2, OUTPUT);
  pinMode(motor_right1, OUTPUT);
  pinMode(motor_right2, OUTPUT);
  
}

void loop() {
  int potValue = analogRead(A0);
//  Serial.println(potValue);
  delay(10);
  if (Serial.available() > 0) {
    int command = Serial.read();
    if (command == 10) {
      Serial.println("Command Recieved!");
      return;
    }
    if (command == '9') {
      motor_hold(motor_left1, motor_left2);
      motor_hold(motor_right1, motor_right2);
      return;
    }
    else {
      motor_forward(motor_left1, motor_left2, MOTOR_SPEED); 
      motor_forward(motor_right1, motor_right2, MOTOR_SPEED);   
    }
    
//    int desiredValue = FORWARD_ANGLE - (command - '3') * ANGLE24; // convert char to int
    int desiredValue = 0;
    if (command == '1') desiredValue = FORWARD_ANGLE  + ANGLE1 + 2;
    else if (command == '2') desiredValue = FORWARD_ANGLE + ANGLE2 + 2;
    else if (command == '3') desiredValue = FORWARD_ANGLE + ANGLE35 + 2;
    else if (command == '4') desiredValue = FORWARD_ANGLE;
    else if (command == '5') desiredValue = FORWARD_ANGLE - ANGLE35 + 3;
    else if (command == '6') desiredValue = FORWARD_ANGLE - ANGLE6;
    else if (command == '7') desiredValue = FORWARD_ANGLE - ANGLE7 + 1;
    
    desiredValue = min(max(desiredValue, 447), 600);
    // if(command == '1') desiredValue = 600;
    // else if (command == '5') desiredValue = 447;
    //maybe little bit bigger (Right Max = 447  ,Left max = 600)
    
    while(true){
      
      int curValue = analogRead(A0);
      int motorSpeed = min(abs(curValue - desiredValue) * 30, 200);

      if (abs(curValue - desiredValue) <= TOLERANCE) break;

      if (curValue < desiredValue) motor_left(motorSpeed);
      else motor_right(motorSpeed);
      delay(DELAY);
//      if (Serial.available() > 0) break; // check if difference signal comes in
    }
    
    motor_hold(motor_dir_con1, motor_dir_con2);
  }
}
