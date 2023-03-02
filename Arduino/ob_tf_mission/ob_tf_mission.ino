//For obstacle and traffic light detection 

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
#define FORWARD_ANGLE 520
#define ANGLE2 38
#define ANGLE6 35
#define ANGLE7 69
#define ANGLE1 68
#define ANGLE35 25
#define MOTOR_SPEED 60

void motor_left(int motorSpeed){
  motor_backward(motor_dir_con1, motor_dir_con2, motorSpeed);
}

void motor_right(int motorSpeed){
  motor_forward(motor_dir_con1, motor_dir_con2, motorSpeed);
}

void delay_toward(int command, int delayMs){
  int elapsedTime = 0;
  int desiredValue = 0;
  if (command == '1') desiredValue = FORWARD_ANGLE  + ANGLE1 + 2;
  else if (command == '2') desiredValue = FORWARD_ANGLE + ANGLE2 + 2;
  else if (command == '3') desiredValue = FORWARD_ANGLE + ANGLE35 + 2;
  else if (command == '4') desiredValue = FORWARD_ANGLE;
  else if (command == '5') desiredValue = FORWARD_ANGLE - ANGLE35 + 3;
  else if (command == '6') desiredValue = FORWARD_ANGLE - ANGLE6;
  else if (command == '7') desiredValue = FORWARD_ANGLE - ANGLE7 + 1;
  
  desiredValue = min(max(desiredValue, 447), 600);

  while(elapsedTime < delayMs){
    int curValue = analogRead(A0);
    int motorSpeed = min(abs(curValue - desiredValue) * 30, 200);
    
    if (abs(curValue - desiredValue) <= TOLERANCE) break;

    if (curValue < desiredValue) motor_left(motorSpeed);
    else motor_right(motorSpeed);
    
    delay(10);
    elapsedTime += 10;
  }
  motor_hold(motor_dir_con1, motor_dir_con2);
  while(elapsedTime < delayMs) {
    delay(10);
    elapsedTime += 10;
  }
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
      //Serial.println("Command Recieved!");
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
     if (command == 'c') { //장애물 피하기 Rule based 진행
      motor_forward(motor_left1, motor_left2, 80); 
      motor_forward(motor_right1, motor_right2, 80); 
      delay_toward('1', 6000); // m:5700 f:5200
      delay_toward('7', 4600); // m:4600 f:4600
      delay_toward('4', 2000); // m:2000 f:2000
      delay_toward('7', 5000); // m:5600 f:4900
      delay_toward('1', 4600); // m:4600 f:4600
      delay_toward('4', 500);  // m:500  f:500
      Serial.println("of");
      return;
    }
    else {
      motor_forward(motor_left1, motor_left2, MOTOR_SPEED); 
      motor_forward(motor_right1, motor_right2, MOTOR_SPEED);   
    if (command == 'm') { //장애물 피하기 Rule based 진행
      motor_forward(motor_left1, motor_left2, 80); 
      motor_forward(motor_right1, motor_right2, 80); 
      delay_toward('1', 5200); // m:5700 f:5200
      delay_toward('7', 4600); // m:4600 f:4600
      delay_toward('4', 2000); // m:2000 f:2000
      delay_toward('7', 5600); // m:5600 f:4900
      delay_toward('1', 4600); // m:4600 f:4600
      delay_toward('4', 500);  // m:500  f:500
      Serial.println("of");
      return;
    }
    else {
      motor_forward(motor_left1, motor_left2, MOTOR_SPEED); 
      motor_forward(motor_right1, motor_right2, MOTOR_SPEED);  
    if (command == 'f') { //장애물 피하기 Rule based 진행
      motor_forward(motor_left1, motor_left2, 80); 
      motor_forward(motor_right1, motor_right2, 80); 
      delay_toward('1', 4550); // m:5700 f:5200
      delay_toward('7', 4600); // m:4600 f:4600
      delay_toward('4', 2000); // m:2000 f:2000
      delay_toward('7', 4900); // m:5600 f:4900
      delay_toward('1', 4600); // m:4600 f:4600
      delay_toward('4', 500);  // m:500  f:500
      Serial.println("of");
      return;
    }
    else {
      motor_forward(motor_left1, motor_left2, MOTOR_SPEED); 
      motor_forward(motor_right1, motor_right2, MOTOR_SPEED);  
    }
    if (command == 'r') {
      motor_forward(motor_left1, motor_left2, 80); 
      motor_forward(motor_right1, motor_right2, 80); 
      delay(4100); //영상 기준으로 세팅
      motor_hold(motor_left1, motor_left2);
      motor_hold(motor_right1, motor_right2);
      return; //For green, just send 4 to proceed
    }
    else {
      motor_forward(motor_left1, motor_left2, MOTOR_SPEED); 
      motor_forward(motor_right1, motor_right2, MOTOR_SPEED);   
    }
//    int desiredValue = FORWARD_ANGLE - (command - '3') * ANGLE24; // convert char to int
    int desiredValue = 0;
    if (command == '1') {
      desiredValue = FORWARD_ANGLE  + ANGLE1 + 2;
      motor_forward(motor_left1, motor_left2, MOTOR_SPEED); 
      motor_forward(motor_right1, motor_right2, MOTOR_SPEED);     //-10 
    }
    else if (command == '2') {
      desiredValue = FORWARD_ANGLE + ANGLE2 + 2;
    }
    else if (command == '3') {
      desiredValue = FORWARD_ANGLE + ANGLE35 + 2;
    }
    else if (command == '4') {
      desiredValue = FORWARD_ANGLE;
    } 
    else if (command == '5') {
      desiredValue = FORWARD_ANGLE - ANGLE35 + 3;
    }  
    else if (command == '6') {
      desiredValue = FORWARD_ANGLE - ANGLE6;
    }
    else if (command == '7') {
      desiredValue = FORWARD_ANGLE - ANGLE7 + 1;
    }
    
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
    }    }}
