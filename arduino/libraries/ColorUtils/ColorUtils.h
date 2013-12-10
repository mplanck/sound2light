#ifndef _COLOR_UTILS
#define _COLOR_UTILS

// Utilities for color correcting float inputs into a perceptively linear space

// ------------------------------------------------------------------------
// STRUCTS

struct Color {
   float red;
   float green;
   float blue;
};

// ------------------------------------------------------------------------
// GLOBALS

float global_channelmin_channels[3] = {0., 0., 0.};
float global_channelmax_channels[3] = {1., 1., 1.};
float global_channelgamma_channels[3] = {3.6, 3.6, 3.6};

// ------------------------------------------------------------------------
// UTILITIES

float mapf(float x, 
           float fromLow, float fromHigh, 
           float toLow, float toHigh)
{
  return (toHigh - toLow) * ((x - fromLow) / (fromHigh - fromLow)) + toLow;
}

// Convert a float sized channel with range [0, +] to a float value that 
// maps to a perceptively linear space according to the tcl led outputs.

// Current Calibration
// Red   Gamma: 3.6
// Green Gamma: 3.6
// Blue  Gamma: 3.6

Color plspace(Color c)
{    
   Color result = {1., 1., 1.};   
   result.red = pow(mapf(c.red, 0., 1., 
                         global_channelmin_channels[0], 
                         global_channelmax_channels[0]), 
                         global_channelgamma_channels[0]); 

   result.green = pow(mapf(c.green, 0., 1., 
                           global_channelmin_channels[1], 
                           global_channelmax_channels[1]), 
                           global_channelgamma_channels[1]); 

   result.blue = pow(mapf(c.blue, 0., 1., 
                          global_channelmin_channels[2], 
                          global_channelmax_channels[2]), 
                          global_channelgamma_channels[2]); 
   return result;
}

#endif