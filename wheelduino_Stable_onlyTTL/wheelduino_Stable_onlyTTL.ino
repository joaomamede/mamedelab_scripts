#include <AccelStepper.h>

// General definitions
int CurrentFilter = 0;                  // Filter integer
int HallValue;                          // Hall switch variable
int Microstep = 4;

// Filter steps definitions
int CalibrationOffset = 24*Microstep;              // Steps required to move to first filter position after calibration is done
int FilterSteps = 44*Microstep;                  // Steps required to move the filter to next filter location adjust as required to suit motor wheel combination
int FilterSteps0 = 0;                   // Set filter steps for home position from calibration
int FilterSteps1 = FilterSteps;         // Set filter steps for 1st position
int FilterSteps2 = FilterSteps * 2;     // Set filter steps for 2nd position
int FilterSteps3 = FilterSteps * 3;     // Set filter steps for 3rd position
int FilterSteps4 = FilterSteps * 4;     // Set filter steps for 4th position
int FilterSteps5 = FilterSteps * 5;     // Set filter steps for 5th position
int FilterSteps6 = FilterSteps * 6;     // Set filter steps for 6th position

// Hall pin definition
#define out 9                     // PIN 12 = Hall effect switch
#define pos0 4
#define pos1 5
#define pos2 10
#define pos3 16
#define pos4 14
#define pos5 15
//const int calibrate = 3;
//const int LED_pin = 2;
// Motor definitions
// Motor pin definitions
// enum  	MotorInterfaceType {
//   FUNCTION = 0, DRIVER = 1, FULL2WIRE = 2, FULL3WIRE = 3,
//   FULL4WIRE = 4, HALF3WIRE = 6, HALF4WIRE = 8
// }
#define STEPS 1                // 28BYJ-48 steps 4 or 8


#define motorPin1  3      //Step pin3
#define motorPin2  2       //Direction pin2
#define M0 8
#define M1 7
#define M2 6



//M0 pin8
//M1 pin7
//M2 pin6
// #define motorPin3  8
// #define motorPin4  7
// #define motorPin5  6
// Initialize with pin sequence IN1-IN3-IN2-IN4 for using the AccelStepper with 28BYJ-48
AccelStepper stepper1(STEPS, motorPin1, motorPin2);
  // , motorPin2, motorPin4,motorPin5);


void setTXLED() {
  TXLED1;
}

void setup() {

//  Serial.flush();
//  Serial.begin(9600);  // Baud rate, make sure this is the same as ASCOM driver
  // stepper1.setMaxSpeed(250000.0);
  // stepper1.setAcceleration(150000.0); // Acceleration
  // stepper1.setSpeed(40000.0);
  stepper1.setMaxSpeed(1000000.0);
  stepper1.setAcceleration(300000.0); // Acceleration
  stepper1.setSpeed(40000.0);
  stepperHome(); //runs routine to home motor
//  Serial.println("1#");
  pinMode(pos0, INPUT);//pin10 pos0
  pinMode(pos1, INPUT);//pin16 pos1
  pinMode(pos2, INPUT);//pin14 pos2
  pinMode(pos3, INPUT);//pin15 pos3
  pinMode(pos4, INPUT);//pin9 pos4
  pinMode(pos5, INPUT);//pin5 pos5
//  pinMode(calibrate, INPUT);//pin2
   //TX LED macro to turn LED ON
//  pinMode(calibrate, INPUT);//pin2
  pinMode(M0, OUTPUT);
  pinMode(M1, OUTPUT);
  pinMode(M2, OUTPUT);

}


void loop() {
//  String cmd;
//   if (Serial.available() > 0) {
//     cmd = Serial.readStringUntil('#');  // Terminator so arduino knows when the message ends
//     if (cmd == "GETFILTER") {
//       Serial.println("I'm in loop mode");
//       Serial.print(CurrentFilter); Serial.println("#");  // Similarly, so ASCOM knows
//     }
//    else if (cmd == "FILTER0") MoveFilter(0); // Move Filter Routine
//    else if (cmd == "FILTER1") MoveFilter(1); // Move Filter Routine
//    else if (cmd == "FILTER2") MoveFilter(2); // Move Filter Routine
//    else if (cmd == "FILTER3") MoveFilter(3); // Move Filter Routine
//    else if (cmd == "FILTER4") MoveFilter(4); // Move Filter Routine
//    else if (cmd == "FILTER5") MoveFilter(5); // Move Filter Routine
//    else if (cmd == "FILTER6") MoveFilter(6); // Calibration Routine
//    else if (cmd == "SHOT") delay(42); // Calibration Routine
//  }
//  Serial.println("Current Reads");
//  Serial.println(digitalRead(pos0));
//  Serial.println(digitalRead(pos1));
//  Serial.println(digitalRead(pos2));
//  Serial.println(digitalRead(pos3));
//  Serial.println(digitalRead(pos4));
//  Serial.println(digitalRead(pos5));
  if(digitalRead(pos0) == HIGH) {MoveFilter(0);}
  else if (digitalRead(pos1) == HIGH) {MoveFilter(1);}
  else if (digitalRead(pos2) == HIGH) {MoveFilter(2);}
  else if (digitalRead(pos3) == HIGH) {MoveFilter(3);}
  else if (digitalRead(pos4) == HIGH) {MoveFilter(4);}
  else if (digitalRead(pos5) == HIGH) {MoveFilter(5);}
//  else if (digitalRead(calibrate) == HIGH) {MoveFilter(6);}
//  Serial.println("Hello! Can anybody hear me?");  // Print "Hello!" over hardware UART

//  digitalWrite(RXLED, HIGH);    // set the RX LED OFF


}


void stepperHome()
{
  //1/4 stepping settings
  digitalWrite(M0, LOW);
  digitalWrite(M1, HIGH);
  digitalWrite(M2, LOW);
//  digitalWrite(M2, LOW);

  HallValue = digitalRead(out);    // read the hall sensor value
//  digitalWrite(LED_pin, HIGH); // Flash LEDs for Move
  RXLED1;
//if HallValue == LOW:
// move=688
// else: while blablablal
// do it 6 times calculate the good stepping distance with linear regression
// then set possition
// and reset the stepping positions
  while (HallValue == HIGH)
  {
    stepper1.setAcceleration(1000.0); // Acceleration
    stepper1.setSpeed(1000.0);
    stepper1.move(5);
    stepper1.run();
    HallValue = digitalRead(out); // read the hall sensor value
  }

  stepper1.setCurrentPosition(0);
  stepper1.runToNewPosition(CalibrationOffset);
  stepper1.setCurrentPosition(0);
  stepper1.setMaxSpeed(250000.0);
  stepper1.setAcceleration(150000.0); // Acceleration
  stepper1.setSpeed(40000.0);
//  digitalWrite(LED_pin, LOW); // Disable LEDs after Move
  RXLED0;

}
void MoveFilter(int pos) {

  CurrentFilter = pos;    // Note that the position is always 0 when powered on due to calibration
  switch (CurrentFilter) {
  case 0:
//    digitalWrite(LED_pin, HIGH); // Flash LEDs for Move
    TXLED1;
    stepper1.runToNewPosition(FilterSteps0); // Goto new position
//    Serial.print(CurrentFilter); Serial.println("#"); // Notify that we sent the command
//    digitalWrite(LED_pin, LOW); // Disable LEDs after Move
    TXLED0;
  break;

  case 1:
//    digitalWrite(LED_pin, HIGH); // Flash LEDs for Move
   TXLED1;
    stepper1.runToNewPosition(FilterSteps1); // Goto new position
//     Serial.print(CurrentFilter); Serial.println("#"); // Notify that we sent the command
//    digitalWrite(LED_pin, LOW); // Disable LEDs after Move
    TXLED0;
  break;

  case 2:
//    digitalWrite(LED_pin, HIGH); // Flash LEDs for Move
    TXLED1;
    stepper1.runToNewPosition(FilterSteps2); // Goto new position
//     Serial.print(CurrentFilter); Serial.println("#"); // Notify that we sent the command
//    digitalWrite(LED_pin, LOW); // Disable LEDs after Move
    TXLED0;
  break;

  case 3:
//    digital+Write(LED_pin, HIGH); // Flash LEDs for Move
    TXLED1;
    stepper1.runToNewPosition(FilterSteps3); // Goto new position
//     Serial.print(CurrentFilter); Serial.println("#"); // Notify that we sent the command
//    digitalWrite(LED_pin, LOW); // Disable LEDs after Move
    TXLED0;
  break;

  case 4:
    TXLED1;
//    digitalWrite(LED_pin, HIGH); // Flash LEDs for Move
    stepper1.runToNewPosition(FilterSteps4); // Goto new position
//    Serial.print(CurrentFilter); Serial.println("#"); // Notify that we sent the command
//    digitalWrite(LED_pin, LOW); // Disable LEDs after Move
    TXLED0;
  break;
  case 5:
//    digitalWrite(LED_pin, HIGH); // Flash LEDs for Move
    TXLED1;
    stepper1.runToNewPosition(FilterSteps5); // Goto new position
//     Serial.print(CurrentFilter); Serial.println("#"); // Notify that we sent the command
//    digitalWrite(LED_pin, LOW); // Disable LEDs after Move
    TXLED0;
  break;
  case 6:
    stepperHome(); // Calibratio Routine
//     Serial.print(CurrentFilter); Serial.println("#"); // Notify that we sent the command
  break;
  }

}
