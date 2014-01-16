#define STEPPER_PORT  1
#define N_STEPS       200
#define STEPPER_RPM   100

#define SERVO_PORT    10

#define PUMP_PORT     3
#define PUMP_RPM      175

#define ARM_LENGTH    30

#include <math.h>
#include <Wire.h>
#include <Servo.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_PWMServoDriver.h"

// actuators
Adafruit_MotorShield motor_shield; 
Adafruit_StepperMotor *stepper;
Adafruit_DCMotor *pump;
Servo servo;

// projected radial position of servo arm
int arm_radius;

// angle of stepper
int susan_angle;

void setup()
{
  actuator_setup();
  Serial.begin(9600);  
}

void loop()
{
  float pour_time = 15; // in seconds;
  
  // linear scaling factor for radius
  float alpha = ((float)ARM_LENGTH)/pour_time;
  
  // linear scaling factor for rotation
  float beta = 360.0/pour_time;
  
  // perform spiral
  spiral(alpha,beta,ARM_LENGTH-10);
  
  // reset position
  delay(10);
  go_to(0,0);
  delay(1000);
}

void actuator_setup()
{
  // initialize motor shield
  motor_shield = Adafruit_MotorShield();
  motor_shield.begin();
  
  // initialize stepper
  stepper = motor_shield.getStepper(N_STEPS, STEPPER_PORT);
  stepper -> setSpeed(STEPPER_RPM);
  
  //initialize dc
  pump = motor_shield.getMotor(PUMP_PORT);
  pump -> setSpeed(PUMP_RPM);
  
  // initialzie servo
  servo.attach(SERVO_PORT);
  
  go_to(0,0);
  
}


void spiral(float alpha, float beta, float max_radius) 
{
  // begin timer
  float time = millis();
  float delta_time;
  float orig_arm_radius = arm_radius;
  float orig_susan_angle = susan_angle;
  while (arm_radius < max_radius)
  {
    delta_time = (millis() - time)/1000.0; 
    go_to(orig_arm_radius +  alpha * delta_time, 
          orig_susan_angle + beta *delta_time);
  }
}

void go_to(float r, float theta)
{
  // go to the angle that will give r
  int servo_angle = round(radius_to_angle(r,ARM_LENGTH));
  servo.write(servo_angle);
  
  // calculate number of steps for stepper motor to take
  int delta_steps = round(angle_to_steps(theta,N_STEPS) - angle_to_steps(susan_angle,N_STEPS));
  
  
  char buf[50];
  sprintf(buf, "Servo angle %d for %f\nTheta steps %d", servo_angle,r, delta_steps);
  Serial.println(buf);
  //go to steps
  stepper -> step(delta_steps, FORWARD, SINGLE);
  
  //update current radius and angle
  arm_radius = r;
  susan_angle = round(theta) % 360;
}

// servo arm calculations
float radius_to_angle(float radius,float arm_length)
{
  int sign = 1;
  if (radius < 0)
    sign = -1;
  return 90 + sign * sin(abs(radius)/arm_length)*180.0/PI;
}

// stepper calculations
int angle_to_steps(float angle, int n_steps)
{
  return round(angle/(360.0/n_steps));
}

float steps_to_angle(int steps, int n_steps)
{
  return 360.0 * ((float) steps) / ((float)  n_steps);
}






