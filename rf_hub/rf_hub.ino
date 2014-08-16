
/**
 * Example RF Radio Ping Pair
 *
 * Borrowed from an example of how to use the RF24 class.  
 */

#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"
#include "printf.h"

//
// Hardware configuration
//

// Set up nRF24L01 radio on SPI bus plus pins 9 & 10

RF24 radio(9,10);

// Radio pipe addresses for the 2 nodes to communicate.
const uint64_t pipes[2] = { 0xF0F0F0F0E1LL, 0xF0F0F0F0D2LL };

float h;
float t;

struct t_data {
  short int id;
  float t;
  float h;
  unsigned long lsp;
  unsigned long uptime;
  unsigned long lastmotion;
  short int treq_user;
  short int treq_pending;
};

struct t_send {
  float t_set;
  short int treq_ack;
  bool heat;
  bool cool;
  bool fan;
};

    
t_data d;
t_send s;

int sensor_id = 0;

void setup(void)
{
  //
  // Print preamble
  //

  Serial.begin(57600);
  printf_begin();
  printf("\n\rRF24/examples/pingpair/\n\r");

  //
  // Setup and configure rf radio
  //

  radio.begin();

  // optionally, increase the delay between retries & # of retries
  radio.setRetries(15,15);

  // optionally, reduce the payload size.  seems to
  // improve reliability
  s.t_set = 70;
  s.heat = 0;
  s.cool = 1;
  s.fan = 1;
  radio.setPayloadSize(sizeof(t_data));

  //
  // Open pipes to other nodes for communication
  //

  // This simple sketch opens two pipes for these two nodes to communicate
  // back and forth.
  // Open 'our' pipe for writing
  // Open the 'other' pipe for reading, in position #1 (we can have up to 5 pipes open for reading)

  radio.openWritingPipe(pipes[1]);
  radio.openReadingPipe(1,pipes[0]);

  //
  // Start listening
  //

  radio.startListening();

  //
  // Dump the configuration of the rf unit for debugging
  //

  radio.printDetails();
}

void loop(void)
{
    // First, stop listening so we can talk.
    
    if(Serial.available() != 0){
    
    // Message format:
    // <sensor_id> <temp setpoint> <treq_ack> <heat> <cool> <fan>
    
      sensor_id = Serial.parseInt();
      if(Serial.available()) s.t_set = Serial.parseFloat();
      if(Serial.available()) s.treq_ack = Serial.parseInt();
      if(Serial.available()) s.heat = Serial.parseInt();
      if(Serial.available()) s.cool = Serial.parseInt();
      if(Serial.available()) s.fan = Serial.parseInt();
      
      if( sensor_id < 1 || sensor_id > 1) {
          Serial.print("Sensor_id ");
          Serial.print( sensor_id );
          Serial.println("invalid");
      }
      Serial.print("Sensor_id: ");
      Serial.print( sensor_id );    
      Serial.print(" Sending t_set: ");
      Serial.print( s.t_set);
      Serial.print(" treq_ack: ");
      Serial.print( s.treq_ack );
    }
    
    if (radio.available()) {
      Serial.print("radio data available");
      radio.read( &d, sizeof(t_data) );

      // Spew it
      Serial.print(" got id: ");
      Serial.print(d.id);
      Serial.print(" t: ");
      Serial.print(d.t);
      Serial.print(" h: ");
      Serial.print(d.h);
      Serial.print(" lsp: ");
      Serial.print(d.lsp);
      Serial.print(" lastmotion: ");
      Serial.print(d.lastmotion);
      Serial.print(" uptime: ");
      Serial.print(d.uptime);
      Serial.print(" treq_pending: ");
      Serial.print(d.treq_pending);
      Serial.print(" treq_user: ");
      Serial.print(d.treq_user);

      if (d.treq_pending != 0) {
        s.treq_ack = d.treq_pending;
        s.t_set = d.treq_pending;
      } else {
        s.treq_ack = 0;
      }
      radio.stopListening();
    
    Serial.print(" sending response:");
    bool ok = radio.write( &s, sizeof(t_send) );
    
    if (ok)
      Serial.print(" ok.\n\r");
    else
      Serial.println(" failed.\n\r");
    radio.startListening();
  }

  delay(10);

}
// vim:cin:ai:sts=2 sw=2 ft=cpp
