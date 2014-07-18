
// ACTUATION DEFINE
#define STEPPER_PORT  2
#define N_STEPS       200
#define STEPPER_RPM   230

#define SERVO_PORT    9

#define PUMP_PORT     1
#define PUMP_RPM      175

#define ARM_LENGTH    3.8
#define MAX_RADIUS    2.375

#define STEP_RATIO    (64.0/20.0)

#define DEFAULT_TEMP   200

#define BAUD_RATE  9600

// SERIAL POUR ORDER DEFINES
#define N_POUR_PARAMS  8
#define THETA_INITIAL  0
#define THETA_RATE     1 
#define RADIUS_INITIAL 2 
#define RADIUS_RATE    3
#define RADIUS_SCALE   4
#define TIME           5
#define PUMP           6
#define TEMP           7

// SERIAL COMMANtemp_wire
#define STOP_COMMAND         "STOP"
#define TEMP_COMMAND         "TEMP"
#define START_POUR_COMMAND   "LINEAR"
#define END_POUR_COMMAND     "END"
#define DONE_POUR_COMMAND    "END POUR"
#define TIME_COMMAND         "TIME\n"


// TEMP DEFINES
#define TEMP_PIN       10
#define TEMP_PERIOD    1000000
#define TEMP_DELTA     5

#define POUR_PERIOD    1000

// LED PIN DEFINITIONS
#define ON_SWITCH_PIN   2
#define POWER_LED_PIN   4
#define PUMP_LED_PIN    7
#define WATER_TEMP_LED_PIN  8

#include <math.h>
#include <Wire.h>
#include <OneWire.h>
#include <time.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_PWMServoDriver.h"
#include <AccelStepper.h>
#include <Servo2.h>
#include <JsonParser.h>

// pour structure
typedef struct p {
  float theta_init;
  float theta_rate;
  float radius_init;
  float radius_rate;
  float time;
  float radius_scale;
  int pump;
  int temp;
  struct p * next_pour;
} pour_t;

// function definitions
pour_t* construct_pour_sequence(JsonHashTable table);

// serial
String input_string = "";         // a string to hold incoming data
boolean string_complete = false;  // whether the string is complete
long temp_time;

int serial_bufsize;

// JSON Parser
JsonParser<36> parser;

// One Wire interface for temp senosr
OneWire temp_wire(TEMP_PIN);  // on pin 10
float temp;
float temp_setpoint;
boolean setpoint_met;

// actuators
Adafruit_MotorShield motor_shield; 
Adafruit_StepperMotor *stepper;
Adafruit_DCMotor *pump;
Servo servo;
AccelStepper Astepper1(forwartemp_wiretep1,backwartemp_wiretep1);

// projected radial position of servo arm
float arm_radius;
 
// angle of stepper
float susan_angle;

long pour_start;
long pour_time;
long pour_tic;
boolean pour_attached;
int last_sent;

// power info
boolean on_switch;

// Sequence
pour_t* seq;

// ACCEL STEPPER FUNCTION DEFS
void forwartemp_wiretep1() 
{
  stepper -> onestep(FORWARD, DOUBLE);
}
void backwartemp_wiretep1() 
{
  stepper -> onestep(BACKWARD, DOUBLE);
}


void setup()
{
  seq = NULL;
  pinMode(ON_SWITCH_PIN,INPUT);
  pinMode(POWER_LED_PIN,OUTPUT);
  pinMode(PUMP_LED_PIN,OUTPUT);
  pinMode(WATER_TEMP_LED_PIN,OUTPUT);

  actuator_setup();
  temp_setup();
  serial_setup();
  
  Serial.println("Setup Complete");
}

void stop_actuation()
{ 
  if (pour_attached) 
  {
    Astepper1.disableOutputs();
    if (seq -> pump)
    {
      digitalWrite(PUMP_LED_PIN,LOW);
      pump -> run(RELEASE);
    }
    pour_attached = false;
    pour_start = -1;
    pour_time = -1;
    last_sent = 0;
    pour_tic = -1;
    pour_t* tmp;
    while (seq != NULL)
    {
      tmp = seq -> next_pour;
      free(seq);
      seq = tmp;
    }
    seq = NULL;
  }
}

void loop()
{ 
  handle_on_switch();
    
  if (string_complete){
    parse_json();
  } 
  
  if (seq != NULL) {
    if (pour_attached)
    {
      long tmp = millis()-pour_tic;
      if (tmp >= 10)
      {
        Serial.println("executing spiral");
        spiral();
      }
    } else if (setpoint_met)
    {
      Serial.println("Setpoint met, starting pour");
      pour_attached = true;
      pour_time = millis();
      pour_tic = pour_time;
      Astepper1.enableOutputs();
      spiral();
    } else 
    {
      Serial.println("Setpoint not met");
    }
  }
  
  long tmp = millis()/1000;
  if(tmp - temp_time >= 1){
    send_temp();
    temp_time = tmp;
  }
}

void handle_on_switch(){
  on_switch = digitalRead(ON_SWITCH_PIN);
  if (on_switch) 
    digitalWrite(POWER_LED_PIN,HIGH);
  else {
    digitalWrite(POWER_LED_PIN,LOW);
    stop_actuation();
    return;
  }
}

void parse_json()
{
  // JSON Parsing
  Serial.println(input_string);
  int bufSize = input_string.length()+1;
  char input_buf[bufSize];
  input_string.toCharArray(input_buf, bufSize);
    
  JsonHashTable hashTable = parser.parseHashTable(input_buf);
  String command = hashTable.getString("Command");
  Serial.println(command);
  
  if(command == "SEQUENCE"){
    seq = construct_pour_sequence(hashTable);
    if (seq != NULL) {
      temp_setpoint = seq -> temp;
      Serial.println("Received sequence");
    } else {
      Serial.println("Received NULL sequence");
    }
    send_temp();
  } else if(command == STOP_COMMAND){
    stop_actuation();
  } else {
    Serial.println("Unrecognized Command");
  }
  
  input_string = "";
  string_complete = false;
}

pour_t* construct_pour_sequence(JsonHashTable table){
  pour_t *pour,*pour_seq = NULL;
  
  for(int i = 0; i < table.getLong("Length"); i++){
    // Allocate new pour
    pour = (pour_t*)(malloc(sizeof(pour_t)));
    memset(pour,0x0,sizeof(pour_t));
    
    // Fill in pour params
    pour -> theta_init = atof(table.getArray("ThetaInit").getString(i));
    pour -> theta_rate = atof(table.getArray("ThetaRate").getString(i));
    pour -> radius_init = atof(table.getArray("RadiusInit").getString(i));
    pour -> radius_rate = atof(table.getArray("RadiusRate").getString(i));
    pour -> radius_scale = atof(table.getArray("RadiusScale").getString(i));
    pour -> time = atof(table.getArray("Time").getString(i));
    pour -> pump = atoi(table.getArray("Pump").getString(i));
    pour -> temp = atoi(table.getArray("Temp").getString(i));
    
    // Update pour_seq structure with new pour  
    if(i == 0){
      pour_seq = pour;
    } else {
      pour_t* tmp = pour_seq;
      while (tmp -> next_pour != NULL) {
        tmp = tmp -> next_pour;
      }
      tmp -> next_pour = pour;
    } 
    
    // Clear local pour to prep for next iter
    pour = NULL;
  }
  
  return pour_seq;
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
  Astepper1.setMaxSpeed(((float) N_STEPS)*((float) STEPPER_RPM)/60.0);
  Astepper1.setAcceleration(100);
  
  susan_angle = 0;
  servo.write(90);
  arm_radius = 0;
  pour_start = -1;
}

void spiral() 
{
  if (pour_start == -1) 
  {
    pour_start = millis();
    if (seq -> pump)
    {
      pump -> setSpeed(seq -> pump);
      pump -> run(FORWARD);
      digitalWrite(PUMP_LED_PIN,HIGH);
    }
  }
  
  long elapsed_time = (millis() - pour_time)/1000 ;
  if (elapsed_time > last_sent)
  {
    Serial.print(TIME_COMMAND);
    char buf[50];
    Serial.println(elapsed_time);
    last_sent = elapsed_time;
  }
  
  // begin timer
  float delta_time,next_radius,next_angle;
  delta_time = (millis() - pour_start)/1000.0; 
  if (delta_time >= seq -> time) 
  {
    susan_angle = 0;
    if (seq == NULL)
    {
      pour_attached = false;
      Serial.println(DONE_POUR_COMMAND);
      pour_time = -1;
      //Astepper1.disableOutputs();
    }
    stepper -> release();
    pump -> run(RELEASE);
    digitalWrite(PUMP_LED_PIN,LOW);
    pour_t *tmp = seq;
    seq = seq -> next_pour;
    free(tmp);
    pour_start = -1;
    return;
  }
  
  next_radius = seq -> radius_init * seq -> radius_scale + seq -> radius_rate * seq -> radius_scale * delta_time;
  next_angle = (seq -> theta_init + seq -> theta_rate * delta_time);
  if (next_angle > 360)
    next_angle -= 360;
  go_to(next_radius, next_angle);
  Serial.println("spiraling");
}

void go_to(float r, float theta)
{
  long delta_steps;
  int delta_step_angle;
  int servo_angle;
  
  // go to the angle that will give r
  if (abs(r) > MAX_RADIUS)
    r = (r/abs(r))*MAX_RADIUS;
  servo_angle = round(radius_to_angle(r,ARM_LENGTH))-4;
  servo.write(servo_angle);
  
  // calculate number of steps for stepper motor to take
  if (susan_angle <= theta)
    delta_step_angle = (theta - susan_angle);
  else 
    delta_step_angle = (theta + 360 - susan_angle);
//  if (susan_angle <= theta)
//    delta_step_angle = (theta + susan_angle);
//  else 
//    delta_step_angle = (theta - 360 +susan_angle);
  delta_steps = (angle_to_steps(delta_step_angle,N_STEPS,STEP_RATIO));
  Serial.println(delta_step_angle);
  Serial.println(delta_steps);
  if ( delta_steps > 0) 
  {
      stepper -> step(delta_steps, FORWARD, DOUBLE);
  }
  
  //update current radius and angle
  arm_radius = round(r);
  susan_angle = ((int)theta);
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
int angle_to_steps(float angle, int n_steps,float step_ratio)
{
  return round(n_steps*step_ratio*angle/360.0);
}

void send_temp()
{  

  byte i;
  byte present = 0;
  byte data[12];
  byte addr[8];
  temp_wire.reset_search();
  if ( !temp_wire.search(addr)) {
      temp_wire.reset_search();
      return;
  }
  
  if ( OneWire::crc8( addr, 7) != addr[7]) {
      return;
  }

  else if ( addr[0] == 0x28) {
  }
  else {
      return;
  }

  temp_wire.reset();
  temp_wire.select(addr);
  temp_wire.write(0x44,1);         // start conversion, with parasite power on at the end

  present = temp_wire.reset();
  temp_wire.select(addr);    
  temp_wire.write(0xBE);         // Read Scratchpad

  for ( i = 0; i < 9; i++) {           // we need 9 bytes
    data[i] = temp_wire.read();
  }
  
  temp = ( (data[1] << 8) + data[0] )*0.0625;
  temp = temp * 1.8 + 32;
  Serial.println(TEMP_COMMAND);
  Serial.println(temp);
  if ((temp > (temp_setpoint-TEMP_DELTA)) && (temp < (temp_setpoint+TEMP_DELTA))) {
    digitalWrite(WATER_TEMP_LED_PIN,LOW);
    setpoint_met = false;
  } else {
    digitalWrite(WATER_TEMP_LED_PIN,HIGH);
    setpoint_met = true;
  }
}

void temp_setup()
{
  temp_time = millis()/1000;
  temp_setpoint = DEFAULT_TEMP;
}

void serial_setup()
{
  input_string.reserve(200);
  Serial.begin(BAUD_RATE);
}

void serialEvent() {
  while (Serial.available()) {
    if (string_complete) {
      break;
    }
    
    // get the new byte:
    char inChar = (char)Serial.read(); 
    
    // add it to the input_string:
    if (inChar == '\n') {
      string_complete = true;
      break;
    } else {
      input_string += inChar;
    }
  }
}
