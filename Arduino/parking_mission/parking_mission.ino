#include <Ultrasonic.h>
#include <Car_Library.h>

int motor_left1 = 4;
int motor_left2 = 5;
int motor_right1 = 6;
int motor_right2 = 7;
int motor_dir_con1 = 2;
int motor_dir_con2 = 3;
int potPin = A0;      // Pin for the potentiometer
int trig1 = 10; //Rf
int echo1 = 11;


int maxDistance = 900; //mm
int sigCnt = 0;

#define TOLERANCE 0
#define FORWARD 520

void motor_left(int motorSpeed){
  motor_backward(motor_dir_con1, motor_dir_con2, motorSpeed);
}

void motor_right(int motorSpeed){
  motor_forward(motor_dir_con1, motor_dir_con2, motorSpeed);
}

void rotate_counterclockwise(int motorSpeed){
    motor_forward(motor_left2, motor_left1, motorSpeed); 
    motor_forward(motor_right1, motor_right2, motorSpeed); 
    delay_toward_forward(1350); //fix me
    motor_hold(motor_left1, motor_left2);
    motor_hold(motor_right1, motor_right2);
    delay_toward_forward(1500);
    
    motor_forward(motor_left2, motor_left1, motorSpeed); 
    motor_forward(motor_right1, motor_right2, motorSpeed); 
    delay_toward_forward(1350); //fixed
    motor_hold(motor_left1, motor_left2);
    motor_hold(motor_right1, motor_right2);
    delay_toward_forward(1500); //fixed
    
    motor_forward(motor_left2, motor_left1, motorSpeed); 
    motor_forward(motor_right1, motor_right2, motorSpeed); 
    delay_toward_forward(1350); //fixed
    motor_hold(motor_left1, motor_left2);
    motor_hold(motor_right1, motor_right2);
    delay_toward_forward(1500); //fixed

    motor_forward(motor_left2, motor_left1, motorSpeed); 
    motor_forward(motor_right1, motor_right2, motorSpeed); 
    delay_toward_forward(1350); //fixed
    motor_hold(motor_left1, motor_left2);
    motor_hold(motor_right1, motor_right2);
    delay_toward_forward(1500); //fixed

    motor_forward(motor_left2, motor_left1, motorSpeed); 
    motor_forward(motor_right1, motor_right2, motorSpeed); 
    delay_toward_forward(1350); //fixed
    motor_hold(motor_left1, motor_left2);
    motor_hold(motor_right1, motor_right2);
    delay_toward_forward(1500); //fixed

    Serial.print("Twist");
}
void rotate_clockwise(int motorSpeed){
    motor_forward(motor_left2, motor_left1, motorSpeed); 
    motor_backward(motor_right2, motor_right1, motorSpeed);
    delay_toward_forward(1450); //fix me 
    motor_hold(motor_left1, motor_left2);
    motor_hold(motor_right1, motor_right2);
    delay_toward_forward(1500);
    
    motor_forward(motor_left2, motor_left1, motorSpeed); 
    motor_forward(motor_right1, motor_right2, motorSpeed); 
    delay_toward_forward(1450); //fixed
    motor_hold(motor_left1, motor_left2);
    motor_hold(motor_right1, motor_right2);
    delay_toward_forward(1500);

    motor_forward(motor_left2, motor_left1, motorSpeed); 
    motor_forward(motor_right1, motor_right2, motorSpeed); 
    delay_toward_forward(1450); //fixed
    motor_hold(motor_left1, motor_left2);
    motor_hold(motor_right1, motor_right2);
    delay_toward_forward(1500);

    motor_forward(motor_left2, motor_left1, motorSpeed); 
    motor_forward(motor_right1, motor_right2, motorSpeed); 
    delay_toward_forward(1450); //fixed
    motor_hold(motor_left1, motor_left2);
    motor_hold(motor_right1, motor_right2);
    delay_toward_forward(1500);

    motor_forward(motor_left2, motor_left1, motorSpeed); 
    motor_forward(motor_right1, motor_right2, motorSpeed); 
    delay_toward_forward(1750); //final twist!!
    motor_hold(motor_left1, motor_left2);
    motor_hold(motor_right1, motor_right2);
    delay_toward_forward(1500);
}

void delay_toward_forward(int delayMs){
  int elapsedTime = 0;
  while(elapsedTime < delayMs){
    int curValue = analogRead(A0);
    Serial.println(curValue);
    if (abs(curValue - FORWARD) <= TOLERANCE) break;

    if (curValue < FORWARD) motor_left(75);
    else motor_right(75);
    
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
  pinMode(motor_left1, OUTPUT);
  pinMode(motor_left2, OUTPUT);
  pinMode(motor_right1, OUTPUT);
  pinMode(motor_right2, OUTPUT);
  pinMode(motor_dir_con1, OUTPUT);
  pinMode(motor_dir_con2, OUTPUT);
  pinMode(A0, INPUT);  
  pinMode(trig1, OUTPUT); // Sets the trigPin as an Output
  pinMode(echo1, INPUT);

  delay_toward_forward(5000);
  
//  rotate_counterclockwise(150);
}
void loop(){
    delay(10);
    long distanceRf = ultrasonic_distance(trig1, echo1);
    // Move car forward
    motor_forward(motor_left1, motor_left2, 60);  
    motor_forward(motor_right1, motor_right2, 60); 
    delay(10);

    Serial.print("Distance: ");
    Serial.println(distanceRf);

     if (distanceRf < maxDistance) {
      sigCnt += 1;
     }
  //   if (sigCnt > 0 && (distanceRb > maxDistance && distanceRf > maxDistance)) {
  //    sigCnt += 1;
  //   }
     if (sigCnt >= 20){
      Serial.println("Spot Detected");   
      
      motor_forward(motor_left1, motor_left2, 60); //Forward one more
      motor_forward(motor_right1, motor_right2, 60); 
      delay_toward_forward(6000);//pretty accurate 
      
      Serial.println("little bit more front");
      
      motor_hold(motor_left1, motor_left2);
      motor_hold(motor_right1, motor_right2);
      delay_toward_forward(1000);
      
      rotate_counterclockwise(150);
     
      motor_backward(motor_left1, motor_left2, 80);
      motor_backward(motor_right1, motor_right2, 80);
  
      int elapsedTime = 0;
      sigCnt = 0;
      while(sigCnt <= 10) {
        if (ultrasonic_distance(trig1, echo1) <= 1000){
          sigCnt+=1;
    Serial.print("Distance: ");
    Serial.println(distanceRf);
        }
        elapsedTime += 100;
        delay_toward_forward(100);
      }
  
      elapsedTime += 2000;
      delay_toward_forward(1500); // little bit more back
      
      Serial.print("Parking Complete");
    
      motor_hold(motor_left1, motor_left2);
      motor_hold(motor_right1, motor_right2);
      delay_toward_forward(3500);
  
      motor_forward(motor_left1, motor_left2, 80); 
      motor_forward(motor_right1, motor_right2, 80); 
      delay_toward_forward(elapsedTime+2000);
  
      motor_hold(motor_left1, motor_left2);
      motor_hold(motor_right1, motor_right2);
      delay_toward_forward(1000);
  
  //???????????? ??????
      rotate_clockwise(150);

  //Towards the 'Out' line
      motor_forward(motor_left1, motor_left2, 110); 
      motor_forward(motor_right1, motor_right2, 110); 
      delay_toward_forward(15000);
  
      motor_hold(motor_left1, motor_left2);
      motor_hold(motor_right1, motor_right2);
      delay_toward_forward(15000);
     }
//    }
//   }
  }
