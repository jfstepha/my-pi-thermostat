#include "DHT.h"
#include <LiquidCrystal.h>
#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"
#include <DFR_Key.h>



#define DHTPIN A3     // what pin we're connected to
#define DHTTYPE DHT22   // DHT 22  (AM2302)
#define MOTIONPIN A4
#define ID 1

DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal lcd(8, 9, 4, 5, 6, 7); 
RF24 radio(A1,A2);
DFR_Key keypad;


String keyString = "";
const uint64_t pipes[2] = { 
  0xF0F0F0F0E1LL, 0xF0F0F0F0D2LL };


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


// data sent from the master to the remote thermostat
struct t_send {
  float t_set;
  short int treq_ack;
  bool heat;
  bool cool;
  bool fan;
};

t_data d;
t_send s;


unsigned long lastmotiontime;
unsigned long uptime;
unsigned long starttime;
unsigned long lsp;
float setpoint;
int treq_pending;
int localKey = 0;
unsigned long prev_sensor_read;
unsigned long prev_display_update;

float h;
float t;
int keyDown = 0;

#define SENSOR_UPDATE_PERIOD 3000
#define DISPLAY_UPDATE_PERIOD 1000



//////////////////////////////////////////////////////////////
void setup() {
//////////////////////////////////////////////////////////////
  lcd.begin(16, 2);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Thermostat startup");

  Serial.begin(9600); 
  Serial.println("Thermostat startup");
 
  dht.begin();

  //
  // Setup and configure rf radio
  //

  radio.begin();
  radio.setRetries(15,15);
  radio.setPayloadSize(sizeof(t_data));
  radio.openWritingPipe(pipes[0]);
  radio.openReadingPipe(1,pipes[1]);

  //radio.startListening();

  pinMode( MOTIONPIN, INPUT);
  lastmotiontime = 0;
  starttime = millis();
  lsp=0;
  setpoint=70;
  treq_pending = 0;
  
  prev_sensor_read = 0;
  prev_display_update = millis();
  keypad.setRate(10);

}

//////////////////////////////////////////////////////////////
void read_DHT_sensor() {
//////////////////////////////////////////////////////////////
      prev_sensor_read = millis();
      h = dht.readHumidity();
      t = dht.readTemperature(true);
  
      if (isnan(h) || isnan(t)) {
        Serial.println("Failed to read from DHT sensor!");
        return;
      }
      
      uptime = (millis() - starttime) / 1000;
      lsp += 1;
}

//////////////////////////////////////////////////////////////
void update_display (){
//////////////////////////////////////////////////////////////
      prev_display_update = millis();

      Serial.print("Humidity: "); 
      Serial.print(h);
      Serial.print(" %\t");
      Serial.print("Temperature: "); 
      Serial.print(t);
      Serial.print(" *F\t");
      Serial.print(" lastmotion: ");
      Serial.print( (millis() - lastmotiontime) / 1000 );
      Serial.print(" uptime: ");
      Serial.print( uptime );
      Serial.print(" lsp: ");
      Serial.print( lsp );
      Serial.println();
  
      lcd.clear();
      lcd.setCursor(0,1);
      lcd.print(t);
      lcd.print("F ");
      lcd.print(h);
      lcd.print("% ");
      lcd.setCursor(0,0);
      lcd.print("Set:");
      if (treq_pending != 0) {
        lcd.print( treq_pending);
        lcd.print(" *");
      } else {
        lcd.print( setpoint + treq_pending);
      }        
      if ((millis() - lastmotiontime) < 5000) {
        lcd.setCursor(15,0);
        lcd.print("*");
      }
      if ( s.heat ){ 
        lcd.setCursor(15,1);
        lcd.print("h");
      }
      if ( s.cool ){ 
        lcd.setCursor(15,1);
        lcd.print("c");
      }
      if ( s.fan ){ 
        lcd.setCursor(14,1);
        lcd.print("f");
      }
}

//////////////////////////////////////////////////////////////
void read_keypad() {
//////////////////////////////////////////////////////////////
  //
  // keypad stuff
  //
  localKey = keypad.getKey();
  if (localKey != SAMPLE_WAIT)
  {
    if (localKey == 3 & keyDown != 3) { // up
        if (treq_pending == 0) 
          treq_pending = setpoint + 1;
        else
          treq_pending += 1;
        keyDown = 3;
        update_display();      

    }
    if (localKey == 4 & keyDown != 4) { // down
        if (treq_pending == 0)
          treq_pending = setpoint - 1;
        else
          treq_pending -= 1;
        keyDown = 4;
        update_display();      
    }
    if (localKey == 0) {
      keyDown = 0;
    }
  }

}
//////////////////////////////////////////////////////////////
void send_radio_status() {
//////////////////////////////////////////////////////////////

      // First, stop listening so we can talk
      radio.stopListening();
      
      d.id = ID;
      d.t = t;
      d.h = h;
      d.lastmotion = (millis() - lastmotiontime) / 1000;
      d.uptime = uptime;
      d.lsp = lsp;
      d.treq_pending = treq_pending;
      d.treq_user = d.treq_user;
 
      radio.write( &d, sizeof(t_data) );
      Serial.print(" Sent id:");
      Serial.print(d.id);
      Serial.print(" t:");
      Serial.print(d.t);
      Serial.print(" h:");
      Serial.print(d.h); 
      Serial.print(" lastmotion: ");
      Serial.print(d.lastmotion);
      Serial.print(" uptime: ");
      Serial.print(d.uptime);
      Serial.print(" lsp: ");
      Serial.print(d.lsp);
      Serial.print(" treq_pending: ");
      Serial.print(d.treq_pending);
      Serial.println();  

      
      // reset loops since ping
      lsp = 0;




}
//////////////////////////////////////////////////////////////
void get_radio_response () {
//////////////////////////////////////////////////////////////
      // Now, resume listening so we catch the next packets.
      radio.startListening();
      delay(20);

      // if there is data ready
    if ( radio.available() )
    {
      // Dump the payloads until we've gotten everything
      unsigned long got_time;
      bool done = false;
      while (!done)
      {
        // Fetch the payload, and see if this was the last one.
        done = radio.read( &s, sizeof(t_send) );

        // Spew it
        Serial.print("Got response t_set: ");
        Serial.print( s.t_set);
        Serial.print(" t_ack: ");
        Serial.print( s.treq_ack);
        Serial.println();
        
        if (s.treq_ack == treq_pending) {
          setpoint = s.treq_ack;
          treq_pending = 0;
        }
        if (treq_pending == 0) {
          setpoint = s.t_set;
        }

        // Delay just a little bit to let the other unit
        // make the transition to receiver
        delay(20);
               
      }
    }
}

//////////////////////////////////////////////////////////////
void loop () {
//////////////////////////////////////////////////////////////
  if( digitalRead( MOTIONPIN ) == 0) {
      lastmotiontime = millis();
  }
  if (millis() - prev_sensor_read > SENSOR_UPDATE_PERIOD) {
    read_DHT_sensor();
    send_radio_status();
    get_radio_response();

  }
  if (millis() - prev_display_update > DISPLAY_UPDATE_PERIOD) {
    update_display();      
  }
  read_keypad();
  
  


}
