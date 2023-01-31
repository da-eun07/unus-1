#include <Car_Library.h>

int analogpin = A0 ;
int dir=0;

int motor_left1 = 3;
int motor_left2 = 2;
int motor_right1 = 4;
int motor_right2 = 5;
int motor_dir_con1 = 6;
int motor_dir_con2 = 7;

int real = 0; 
int lv = 175;
int lt = 400; //lane detection 결과 너무 왔다갔다 심하게 하면 lt 줄여보기
//줄여서 안 되면 원래 lv 하나 높인 후 lt 하나 줄여보기

void setup() {
Serial.begin(9600);
}

void loop() {
Stop();
delay(1000);

Go(250);

//1차 장애물 확인 후 왼쪽 차선으로 차선 변경
for(;;){
if(Serial.available()){
  dir=Serial.parseInt();}
if(dir=1){
  motor_backward(motor_dir_con1, motor_dir_con2, lv);
  delay(lt);}
if(dir=-1){
  motor_forward(motor_dir_con1, motor_dir_con2, lv);
  delay(lt);}
if(dir=2){
  motor_backward(motor_dir_con1, motor_dir_con2, 200);
  delay(1500);
  break;}
}

/*여기까지 잘 되는지 확인*/

//멈춰서 직진 방향으로 방향 조종
Stop();
pid_control(130);

//재출발
Go(250);

//2차 장애물 확인 후 1.5초간 오른쪽 차선으로 차선 변경
for(;;){
if(Serial.available()){
  dir=Serial.parseInt();}
if(dir=1){
  motor_backward(motor_dir_con1, motor_dir_con2, lv);
  delay(lt);}
if(dir=-1){
  motor_forward(motor_dir_con1, motor_dir_con2, lv);
  delay(lt);}
if(dir=-2){
  motor_forward(motor_dir_con1, motor_dir_con2, 200); 
  delay(1500); //차선 변경 시 lane 밖으로 너무 과도하게 나가면 delay time 줄여보기
  break;}
}


//멈춰서 직진 방향으로 방향 조종
Stop();
pid_control(130);

//재출발
Go(250);
delay(2000);

Stop();
delay(100000);
}

void Go(int v){
  motor_forward(motor_left1, motor_left2, v);
  motor_forward(motor_right1, motor_right2, v);
}

void Stop(void){
  motor_hold(motor_left1, motor_left2);
  motor_hold(motor_right1, motor_right2);
}

void pid_control(int goal){
  float err=0;
  float Pv =5.55;
  float P_val=0;

  while(1){
  real = potentiometer_Read(analogpin); 
  if(real>goal-2 && real<goal+2){
    motor_hold(motor_dir_con1, motor_dir_con2);
    break;
   }
   
  err=real-goal;
  P_val=err*Pv;

  if(P_val>0){
  motor_forward(motor_dir_con1, motor_dir_con2, 175);
  delay(abs(P_val));  
  }

  if(P_val<0){
  motor_backward(motor_dir_con1, motor_dir_con2, 175);
  delay(abs(P_val));
  }  
 }
}
