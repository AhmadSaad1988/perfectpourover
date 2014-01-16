#include <Wire.h>
#include <Servo.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_PWMServoDriver.h"

// Servo Variables
Servo test_servo;
int servo_port;
int servo_angle;
boolean servo_increment;

// Motor Shield Variables
Adafruit_MotorShield motor_shield; 


// Stepper Motor Variables
Adafruit_StepperMotor *test_stepper;
int n_steps;
int stepper_port;
int stepper_rpm;
int stepper_dir;
int step_type;
int steps_to_take;

// DC Motor Variables
Adafruit_DCMotor *test_dc;
int dc_port;
int dc_speed;
int dc_dir;


void setup() 
{ 
  
  // Motor Shield setup

  motor_shield = Adafruit_MotorShield();
  motor_shield.begin();
  // Servo setup 
//  servo_angle = 0;
//  servo_increment = true;
//  servo_port = 10;
//  test_servo.attach(servo_port);  // attaches the servo on pin 9 to the servo object 
//  
//  // Stepper Motor setup
//  n_steps = 200;
//  stepper_port = 1;
//  stepper_rpm = 250;
//  test_stepper = motor_shield.getStepper(n_steps, stepper_port);
//  test_stepper -> setSpeed(stepper_rpm);
//  stepper_dir = BACKWARD;
//  step_type = SINGLE;
//  steps_to_take = 2;
//  
  // DC Motor setup
  dc_port = 3;
  dc_speed = 250;
  test_dc = motor_shield.getMotor(dc_port);
  test_dc -> setSpeed(dc_speed);
  dc_dir = FORWARD;
} 
 
 
void loop()
{
  // Servo example
//  if (servo_increment)
//    servo_angle++;
//  else
//    servo_angle--;
//  if (servo_angle == 179 || servo_angle == 0)
//    servo_increment = !servo_increment;
//    
//  test_servo.write(servo_angle);
//  
  // Stepper example
//  test_stepper -> step(steps_to_take, stepper_dir, step_type);
//  
  // DC Motor example
  test_dc->run(dc_dir);
  delay(100);
  
}
 

