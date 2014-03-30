#include <OneWire.h>

int onSwitchPin = 2;
int greenLEDPin = 4;
int blueLEDPin = 7;
int redLEDPin = 8;

// DS18S20 Temperature chip i/o
OneWire ds(10);  // on pin 10
float temp;
int onSwitchReading;
long time;

void setup(void) {
  // initialize inputs/outputs
  pinMode(onSwitchPin, INPUT);
  pinMode(redLEDPin, OUTPUT);
  pinMode(blueLEDPin, OUTPUT);
  pinMode(greenLEDPin, OUTPUT);
  
  time = millis();
  
  // start serial port
  Serial.begin(9600);
}

void loop(void) {
  // Read Switch
  onSwitchReading = digitalRead(onSwitchPin);
  //Serial.print("Power: ");
  //Serial.println(onSwitchReading);
  
  if(onSwitchReading){
    digitalWrite(greenLEDPin, HIGH); 
  } else {
    digitalWrite(greenLEDPin, LOW); 
  }
  
  if(temp > 75.0){
    digitalWrite(redLEDPin, HIGH); 
  } else {
    digitalWrite(redLEDPin, LOW); 
  }
  
  if(millis() - time > 1000){
    check_temp();
    time = millis();
  }
}

void check_temp(){
  // Read temp
  byte i;
  byte present = 0;
  byte data[12];
  byte addr[8];

  if ( !ds.search(addr)) {
      //Serial.print("No more addresses.\n");
      ds.reset_search();
      return;
  }

  //Serial.print("R=");
  for( i = 0; i < 8; i++) {
    //Serial.print(addr[i], HEX);
    //Serial.print(" ");
  }

  if ( OneWire::crc8( addr, 7) != addr[7]) {
      Serial.print("CRC is not valid!\n");
      return;
  }

  if ( addr[0] == 0x10) {
      //Serial.print("Device is a DS18S20 family device.\n");
  }
  else if ( addr[0] == 0x28) {
      //Serial.print("Device is a DS18B20 family device.\n");
  }
  else {
      //Serial.print("Device family is not recognized: 0x");
      //Serial.println(addr[0],HEX);
      return;
  }

  ds.reset();
  ds.select(addr);
  ds.write(0x44,1);         // start conversion, with parasite power on at the end

  //delay(1000);     // maybe 750ms is enough, maybe not
  // we might do a ds.depower() here, but the reset will take care of it.

  present = ds.reset();
  ds.select(addr);    
  ds.write(0xBE);         // Read Scratchpad

  //Serial.print("P=");
  //Serial.print(present,HEX);
  //Serial.print(" ");
  for ( i = 0; i < 9; i++) {           // we need 9 bytes
    data[i] = ds.read();
    //Serial.print(data[i], HEX);
    //Serial.print(" ");
  }
  
  temp = ( (data[1] << 8) + data[0] )*0.0625;
  temp = temp * 1.8 + 32;
  Serial.print("Temp: ");
  Serial.println(temp);
    
  //Serial.print(" CRC=");
  //Serial.print( OneWire::crc8( data, 8), HEX);
  //Serial.println();
}
