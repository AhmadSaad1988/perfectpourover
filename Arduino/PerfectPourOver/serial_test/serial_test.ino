#include <OneWire.h>

#define N_POUR_PARAMS  6
#define THETA_INITIAL  0
#define THETA_RATE     1 
#define RADIUS_INITIAL 2 
#define RADIUS_RATE    3
#define TIME           4
#define PUMP           5

#define TEMP_PIN      10

#define TEMP_HEADER "TEMP"


char serial_buf[50];
int serial_bufsize;
byte temp_addr[8];


OneWire temp_wire(TEMP_PIN);  // on pin 10

typedef struct p {
  float theta_init;
  float theta_rate;
  float radius_init;
  float radius_rate;
  float time;
  int pump;
  struct p * next_pour;
} pour_t;

void setup()
{
  serial_bufsize = 50;
  Serial.begin(9600);
  setup_temp();
}

void loop()
{
  Serial.readBytesUntil('\n', serial_buf, serial_bufsize);
  if (strcmp(serial_buf,"Pour Sequence") == 0)
    receive_pour_sequence();
    
}

void receive_pour_sequence()
{
  pour_t *pour,*seq = NULL;
  Serial.readBytesUntil('\n', serial_buf, serial_bufsize);
  while (strcmp(serial_buf,"End") != 0)
  {
    pour = (pour_t*)(malloc(sizeof(pour_t)));
    memset(pour,0x0,sizeof(pour_t));
    for (int i = 0; i < N_POUR_PARAMS; i++) 
    {
      Serial.readBytesUntil('\n', serial_buf, serial_bufsize);
      switch(i) 
      {
        case THETA_INITIAL:
          sscanf(serial_buf,"%d\n",&pour -> theta_init);  
          break;
        case THETA_RATE:
          sscanf(serial_buf,"%f\n",&pour -> theta_rate);  
          break;
        case RADIUS_INITIAL:
          sscanf(serial_buf,"%f\n",&pour -> radius_init);  
          break;
        case RADIUS_RATE:
          sscanf(serial_buf,"%f\n",&pour -> radius_rate);  
          break;
        case TIME:
          sscanf(serial_buf,"%f\n",&pour -> time);  
          break;
        case PUMP:
          sscanf(serial_buf,"%d\n",&pour -> pump);
          break;
      }
    }
    if (seq == NULL)
      seq = pour;
     else 
       seq -> next_pour = pour;
     pour = NULL;
    Serial.readBytesUntil('\n', serial_buf, serial_bufsize);
  }
}

void setup_temp()
{
   if ( !temp_wire.search(temp_addr)) {
      //Serial.print("No more addresses.\n");
      temp_wire.reset_search();
      return;
  }
}
void send_temp()
{
  byte i;
  byte present = 0;
  byte data[12];
  float temp;
  temp_wire.reset();
  temp_wire.select(temp_addr);
  temp_wire.write(0x44,1); // start conversion, with parasite power on at the end

  delay(1000); // maybe 750ms is enough, maybe not
  temp_wire.select(temp_addr);    
  temp_wire.write(0xBE); // Read Scratchpad

  for ( i = 0; i < 9; i++) {           // we need 9 bytes
    data[i] = temp_wire.read();
  }
  
  temp = ( (data[1] << 8) + data[0] )*0.0625;
  temp = temp * 1.8 + 32;
  
  Serial.println(TEMP_HEADER);
  Serial.println(temp);
}
