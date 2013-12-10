#ifndef _TCL_UTILS
#define _TCL_UTILS

#include <ColorUtils.h>
#include <StringUtils.h>

// There are 50 LEDs in my Total Control Lighting Strand
#define NUM_LEDS 50
#define MAX_SERIAL_BUFFER_LENGTH 64

// Helper Utilities to be added on top of TCL

// ------------------------------------------------------------------------
// UTILITIES

// Convert from 3 float value Color struct representing r,g,b in perception
// space to a the energy linear space for led output, and then send the signal
// using TCL utilities.

void sendColor(const Color inColor) 
{
    Color plColor = plspace(inColor);

    byte red = byte(constrain(255. * plColor.red, 0., 255.));
    byte green = byte(constrain(255. * plColor.green, 0., 255.));
    byte blue = byte(constrain(255. * plColor.blue, 0., 255.));

    TCL.sendColor(red,green,blue);

}

// ------------------------------------------------------------------------
// CALIBRATION

// Can be used in a loop to tune the gamma correction per channel.  This
// simply outputs a linear ramp for every 10 LEDs and then allows a user
// to use the potentiometers to tune the calibration.

/*

 Start at Potentiometer on bottom left as 1 and then counter clockwise for 2-3-4
 TCL_POT1       : Potentiometer 1  
                      <- tunes the gamma of the currrent channel (R,G or B)
 TCL_POT2       : Potentiometer 2  
                      <- tune the "blackpoint" of the current channel (R,G or B)
 TCL_POT3       : Potentiometer 3  
                      <- tune the "whitepoint" of the current channel (R,G or B)
 TCL_POT4       : Potentiometer 4  
                      <- selects Red, Green or Blue to calibrate (R,G or B)
*/

// Only used when in calibration mode
byte global_channel = 0;

void calibrateLoop()
{

  global_channel = 
    byte(constrain(floor(3. * float(analogRead(TCL_POT4)/1024.)), 0, 2));
  global_channelmin_channels[global_channel] = 
    constrain(float(analogRead(TCL_POT2))/1024., 0., .5); 
  global_channelmax_channels[global_channel] = 
    constrain(float(analogRead(TCL_POT3))/1024., .5, 1.); 
  global_channelgamma_channels[global_channel] = 
    constrain(10.0 * float(analogRead(TCL_POT1))/1024., 1., 10.);     

  Serial.print("Color Channel:\t");
  Serial.print(global_channel);  
  
  Serial.print(" | Gammas:\t");
  Serial.print(global_channelgamma_channels[0]);
  Serial.print("\t");
  Serial.print(global_channelgamma_channels[1]);
  Serial.print("\t");
  Serial.print(global_channelgamma_channels[2]);
  
  Serial.print(" | Mins:\t");
  Serial.print(global_channelmin_channels[0]);
  Serial.print("\t");
  Serial.print(global_channelmin_channels[1]);
  Serial.print("\t");
  Serial.print(global_channelmin_channels[2]);
  
  Serial.print(" | Maxs:\t");
  Serial.print(global_channelmax_channels[0]);
  Serial.print("\t");
  Serial.print(global_channelmax_channels[1]);
  Serial.print("\t");
  Serial.print(global_channelmax_channels[2]);
  Serial.println("");
  
  float calibcolor[3] = { 0., 0., 0. };
  calibcolor[global_channel] = 1.;

  TCL.sendEmptyFrame();

  for (int i = 0; i < NUM_LEDS; i++) {

    int idx = i % 10;
    Color ledColor = { calibcolor[0] * float(idx)/9,
                       calibcolor[1] * float(idx)/9, 
                       calibcolor[2] * float(idx)/9 };

    sendColor(ledColor);
  }  

}


// ------------------------------------------------------------------------
// FLUSH

// Send "black" across all LEDs to flush the lights
void flushLights()
{

  TCL.sendEmptyFrame();
  for (int i = 0; i < NUM_LEDS; i++) {
    Color black = {0., 0., 0.};
    sendColor(black);
  }

}

// ------------------------------------------------------------------------
// UTILITIES

// cycle through red when the program is entered an error state

void errorLoop() {
  
    TCL.sendEmptyFrame();
    float intensity = pow(0.4 * sin(2. * float(millis())/500.0) + 0.6, 10.);
        
    for (int i = 0; i < NUM_LEDS; i++) {
      
      Color errColor = { 
        intensity * errColor.red   , 
        intensity * errColor.green , 
        intensity * errColor.blue  };
  
      sendColor(errColor);
    }
}


// ------------------------------------------------------------------------
// SERIAL Connections

// Functions and structs used to manage serial input and output to the 
// Arduino

//  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// STRUCTS

struct HandShakeProtocol {
   String programName; // name of the program messaging the arduino
   bool handshakeMade; // bit on whether a handshake is successful
   bool receivingColor; // is the handshake in receiving color mode
};


void resetHandshake(HandShakeProtocol* protocol)
{
  protocol->handshakeMade  = false;
  protocol->receivingColor = false;
  protocol->programName    = "Unknown";
}

// Look at what message is on the serial line and use that to update
// the HandShakeProtocol object passed in.  
//  Valid messages to process:
//   - tcl:handextended:<program name>!
//     Used to initiate a handshake with the arduino and declare the
//     requesting program name.  This program name can be used to
//     filter through other types of serial signals (although that
//     filtering function is not implemented yet)
//
//   * returns tcl:handreceived:<program name>\n

//   - tcl:handreceived:<program name>!
//     Used by the requesting program to confirm the handshake is made.
//
//   * returns tcl:handshakeconfirmed:<program name>\n

//   - tcl:status!
//     Sent by the requesting program to ask for the current program
//     name as the arduino knows it and whether or not the requesting
//     program and the arduino are in a successful handshake.
//
//   * returns tcl:handshakeconfirmed:<program name>\n

//   - tcl:colorbegin!

//     Sent by the requesting program to declare that it is sending
//     lots of color data.  XXX: would be nice to be able to exit this
//     mode via some serial message, but in practice, we tend to reset
//     the firmware of  the arduino program when we open a new
//     requesting program.
//
//   * returns tcl:colorbeginreceived:<program name>\n


//  So to behave as a valid TLC python program, you need to send the
//  following serial messages:
//  "tcl:handexteded:<program name>!"
//  "tcl:handreceived:<program name>!"
//  "tcl:colorbegin!"

void processSerialInstruction(HandShakeProtocol* handshake)
{

  char inputChars[MAX_SERIAL_BUFFER_LENGTH];
  int numChars = Serial.readBytesUntil('!', inputChars, MAX_SERIAL_BUFFER_LENGTH);

  String inputString = String(inputChars);     
  inputString = inputString.substring(0, numChars);
  inputString.trim();

  StringArray tokens = StringTokenize(inputString, ':');
  if (tokens.numStrings >= 2) {

    String serialHeader = tokens.strings[0];
    String serialInstruction = tokens.strings[1];
    
    if (!serialHeader.equals("tcl")) {
      return;
    }

    if (serialInstruction.equals("handextended") && tokens.numStrings == 3) {

      handshake->handshakeMade = true;
      handshake->programName = tokens.strings[2];
      
      String output = String("tcl:handreceived:" + handshake->programName + "\n");
      Serial.print(output);

    }

    if (handshake->handshakeMade) {
      if (serialInstruction.equals("status")) {

        Serial.print("tcl:handshakeconfirmed:" + String(handshake->handshakeMade) + "\n");
        if (handshake->handshakeMade) {
          Serial.print("tcl:handshakeprogram: " + handshake->programName + "\n");
        }
      }

      if (serialInstruction.equals("colorbegin")) {

        handshake->receivingColor = true;

        Serial.print("tcl:colorbeginreceived:" + String(handshake->programName) + "\n");
      }
      
    }

  }

  // Make sure that any serial message we're sending back to the requesting
  // program ends in a newline.
  Serial.println();

  // Clean out the rest of what's in the serial buffer
  while (Serial.available()) {
    Serial.read();
  }

}

#endif