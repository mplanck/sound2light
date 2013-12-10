
/*****************************************************************************
 * PySerialTCLConnect.ino
 *
 * Firmware for listening for handshaking with a serial messaging program 
 * and sending SPI based colors to an Arduino connected to a Total Control
 * Lighting display.
 ****************************************************************************/

/*
 * Only used in calibration mode
 
 Start at Potentiometer on bottom left as 1 and then counter clockwise for 2-3-4
 TCL_POT1       : Potentiometer 1  
                      <- tunes the gamma of the currrent channel (R,G or B)
 TCL_POT2       : Potentiometer 2  
                      <- tune the "blackpoint" of the current channel (R,G or B)
 TCL_POT3       : Potentiometer 3  
                      <- tune the "whitepoint" of the current channel (R,G or B)
 TCL_POT4       : Potentiometer 4  
                      <- selects Red, Green or Blue to calibrate (R,G or B)
 TCL_MOMENTARY1 : Button 1         <- used to reset the firmware
 TCL_MOMENTARY2 : Button 2
 TCL_SWITCH1    : Two-position Switch 1 
                      <- used to put the program into calibration mode
 TCL_SWITCH2    : Two-position Switch 2
 */

#include <SPI.h>
#include <TCL.h>
#include <StringUtils.h>
#include <ColorUtils.h>
#include <TCLUtils.h>

// Handy library functions for printing strings to serial when in 
// DEBUG_MODE (included)
#include <MemoryFree.h>
#include <pgmStrToRAM.h>

// When in debug mode, assume a handshake has taken place and arduino
// is receiving color
#define DEBUG_MODE 0

// Also turn down the baud rate so we don't blast the serial port
#if DEBUG_MODE
#define BAUD_RATE 9600
#else
#define BAUD_RATE 115200
#endif

// ------------------------------------------------------------------------
// GLOBALS

// If global_error gets set to 1, then loop will display the error loop which
// cycles red.
 unsigned int                global_error = 0;
 unsigned long               global_next_ping = 0;

// This is the global handshake object that retains whether there is a valid
// handshake between a requesting program and the arduino firmware.
 HandShakeProtocol           global_handshake;

// We keep the current state of color bytes for all LEDs to handle the serial
// lag.  Since we can only get enough serial data to rates of 30 fps, we want 
// to have control over this b
 static char                 global_color_bytes[NUM_LEDS*3];

// The number of valid color bytes that are currently in the global array
 static unsigned int         global_num_color_bytes = 0;

// ------------------------------------------------------------------------
// SETUP

// setup the program by setting up the TCL developer shield, also open
// a listening Serial port that has a small delay to avoid overflow.

void setup() {
  
  TCL.begin();
  TCL.setupDeveloperShield();

  if(Serial) {

    // Allow a very short 8 millisecond timeout since we are hoping for 
    // a responsiveness of at least 30 fps, so if you miss half the time it
    // takes to hit that window, then the serial port has missed.
    Serial.begin(BAUD_RATE);
    Serial.setTimeout(8);

    resetHandshake(&global_handshake);
    global_error = 0;

    for (int i = 0; i < NUM_LEDS*3; i++) {
      global_color_bytes[i] = 0;
    }
              
    global_num_color_bytes = 0;

#if DEBUG_MODE
      global_handshake.handshakeMade = true;
      global_handshake.programName = getPSTR("DEBUG MODE");
      global_handshake.receivingColor = true;
#endif 

  } else {
    global_error = 1;
  }
  
}

// ------------------------------------------------------------------------
// LOOP

// loop as often as possible, trying to read incoming serial messages,
// digesting them, and either sending back on the serial port or
// relaying that info to the total control light display.

void loop() {

  int sw1state = digitalRead(TCL_SWITCH1);
  int mom1state = digitalRead(TCL_MOMENTARY1);

  // Only send messages every second to avoid swamping the serial output
  bool pingLoop = false; 
  if (millis() > global_next_ping) {      
    pingLoop = true;
    global_next_ping += 1000;
  }

  if (Serial && !global_handshake.handshakeMade) {
    if (pingLoop) { Serial.print(getPSTR("tcl:ready\n")); }
  }

  // 1. When the 1 momentary switch is set to LOW, reset the global
  // HandShakeProtocol (as if setup was run).
  if (mom1state == LOW) {

    flushLights();
    resetHandshake(&global_handshake);
    for (int i = 0; i < NUM_LEDS*3; i++) {
      global_color_bytes[i] = 0;
    }              
    global_num_color_bytes = 0;
    
#if DEBUG_MODE
      global_handshake.handshakeMade = true;
      global_handshake.programName = getPSTR("DEBUG MODE");
      global_handshake.receivingColor = true;
#endif 
    
  } else {
    // 1. OR process the main loop which will either be for calibration or 
    // digesting Serial input into color bytes


    // 2. If the 1 switch is flipped to HIGH, then display the calibration
    // loop which allows the user to tweak gamma, min and max for each 
    // channel (R,G, or B)
    if (sw1state == HIGH) {

      calibrateLoop();
      
    } else {      
      // 2. OR when in receiving color mode, snarf up the data from the 
      // serial port and push that info out to the light displays.  If 
      // there is an error, then cycle the error loop.

      // 3. If there is no known error, then sniff the serial port when in
      // receiving color mode and process that data into bytes we can send
      // down to the TLC controllers.
      if (global_error == 0) {
        
        if (global_handshake.receivingColor) 
        {

          if (Serial.available()) {

              unsigned char headByte = Serial.read();
              // The '*' char is special to indicate the beginning of a frame
              // of data.  So only process the serial data that follows a '*'.
              // I chose the '*' char arbitrarily, but I did want it to be in
              // the lower half of the 256 number range since the lights do
              // not have a lot of range with lower byte values.  So you won't
              // be able to tell the difference between 42, 43 or 41 
              if (headByte == 42) {

                global_num_color_bytes = Serial.readBytes(global_color_bytes, 
                                                          3*NUM_LEDS);

                if (global_num_color_bytes == 3*NUM_LEDS) {

                  TCL.sendEmptyFrame();
                  for (int i = 0; i <= NUM_LEDS; i++) 
                  {

                    byte rchannel = global_color_bytes[3*i+0];
                    byte gchannel = global_color_bytes[3*i+1];
                    byte bchannel = global_color_bytes[3*i+2];

                    Color outColor = 
                    {
                      float(rchannel)/255.0 , 
                      float(gchannel)/255.0 ,            
                      float(bchannel)/255.0 
                    };

                    // This sends the Color struct down the TLC controller
                    // pipe.  
                    sendColor(outColor);
                  }
                  

                  // Flush the global_color_bytes
                  global_num_color_bytes = 0;
                  for (int i = 0; i < NUM_LEDS*3; i++) {
                    global_color_bytes[i] = 0;
                  } 
                }

            }
          }

        } 
        else 
        {

          Color statusColor = {0.0, 0.0, 0.0};
          if (global_handshake.handshakeMade) {
            statusColor.green = 1.0;
          } else {
            statusColor.blue  = 1.0;
          }                

          if (global_handshake.receivingColor) {
            statusColor.blue = 1.0;
          }              

          TCL.sendEmptyFrame();
          for (int i = 0; i < NUM_LEDS; i++) {

            sendColor(statusColor);
          } 
        }
        

    } else {    

      // 3. If there is a known error, cycle the error loop
      errorLoop();
    }
  }

}

}

// ------------------------------------------------------------------------
// SERIAL EVENT

// Used to sniff the serial to see if a requesting program wants to handshake.
// If the arduino is in the mode of receiving color, then this function 
// early exits and we rely on the loop() to process the values from the 
// serial port.

void serialEvent() 
{
  if (Serial)
  {
    if (!global_handshake.receivingColor) 
    {
      processSerialInstruction(&global_handshake); 
    }
  }
}











