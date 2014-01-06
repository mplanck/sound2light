# sound2light arduino and total control lighting project

## The short and sweet:

Turn any sound flowing through my Mac into a colorful light display using the "Cool Neon" Total Control Lighting strip. 

Here it is in action:  

<a href="http://youtu.be/OuHVeVGlFm0" target="_blank">http://youtu.be/OuHVeVGlFm0</a>
<a href="http://youtu.be/OX0XfJmJ88M" target="_blank">http://youtu.be/OX0XfJmJ88M</a>

## The nerd-tastic description: 

Using soundflower to sniff audio flowing through my Mac, a python script processes this audio using pyo to find beats at different frequencies.  The python script turns the beat at each frequency into a pulse that travels from the center of the 50 LED array.  Each pulse is colored differently based on the frequency it represents.  

These color pulses are added on top of each other to represent a 50x1 LED display.  Each color is only 3 bytes (256 possible colors per red green and blue).  This colored array is then messaged via serial to an arduino.  The arduino has firmware that then turns those serial messages into SPI messages which it sends to the controllers of a 50 LED Total Control Lighting strip.  Unfortunately, I am limited to only 50 LEDs and a 30 fps refresh rate considering the slow baud rate of serial.  A future version of this tech should use the ftdi bit bang approach so we can get a lot more bits through the usb to arduino connection: <a href="http://hackaday.com/2009/09/22/introduction-to-ftdi-bitbang-mode/" target="_blank">http://hackaday.com/2009/09/22/introduction-to-ftdi-bitbang-mode/</a>

<p>
This project is a crude prototype and could use A LOT of work to make it something polished.  My hope is that it would be something I have on my desk at work.  I often listen to music on my headphones so I don't disturb others, but I thought it would be neat if people could "see" what I'm listening too using this cool tech from coolneon.  Then again, these LED lights can be pretty bright, so I just may be trading noise pollution for light pollution.  We'll see what my co-workers think.
</p>

<p>
This project tutorial assumes the user knows how to setup, compile and install Arduino firmware, has a familiarity with Mac OS (installing python modules and soundflower) and has a familiarity with python.
</p>

## First the Ingredients

### Hardware used:

* iMac 27-inch Late 2012 model (but works fine on my Late 2012 laptop as well)
* Total Control Lighting 50 LED strip (with accompanying 5V usb connection and 5V AC/DC adapter)
* Seeeduino v3.0 (connected to Mac via mini-USB)
* Total Control Lighting Developer Shield v4.1

### Software used:

* Mac OS X 10.8.5 
* Arduino IDE (download here: <a href="http://http://www.arduino.cc/" target="_blank">http://www.arduino.cc/</a>)
  
  <i>Note you'll also need to download the FTDI USB drivers to setup an arduino (<a href="http://arduino.cc/en/Guide/Howto" target="_blank">http://arduino.cc/en/Guide/Howto</a>)</i>

* Sublime Text 2 (my editor of choice: <a href="http://www.sublimetext.com/" target="_blank">http://www.sublimetext.com/</a> )
* Soundflower v1.6.6 ( <a href="https://www.macupdate.com/app/mac/14067/soundflower" target="_blank">https://www.macupdate.com/app/mac/14067/soundflower</a> )
* python2.7

### Libraries you need to import into your Arduino before compiling PySerialTCLConnect.ino.

* SPI - used to send packeted information down the TCL bus (comes builtin with Arduino)
* TCL - simple wrapper for sending SPI data using a more user friendly interface (comes in the github for convenience - original: <a href="https://bitbucket.org/devries/arduino-tcl" target="_blank">https://bitbucket.org/devries/arduino-tcl</a>)
* pgmStrToRAM - used to minimize memory consumption on the arduino stack when sending serial prints (comes in the github for convenience - original: <a href="https://github.com/mpflaga/Arduino-MemoryFree.git" target="_blank">https://github.com/mpflaga/Arduino-MemoryFree.git</a>)

* TCLUtils - helper methods for turning serial messages into TCL commands (comes in the github - original for this project)
* ArduinoUtils - some tokenizing string utilities(comes in the github - original for this project)
* ColorUtils - simple utilities for defining a color struct and then methods for warping the struct through a gamma curve(comes in the github - original for this project)
</ul>

### Python modules you need:

* numpy (should come standard with python 2.7 or above)
* curses (should come standard with python 2.7 or above)
* pyserial (repo and how to install: <a href="http://pyserial.sourceforge.net/" target="_blank">http://pyserial.sourceforge.net/</a>)
* pyo (code repo and docs: <a href="https://code.google.com/p/pyo/" target="_blank">https://code.google.com/p/pyo/</a>)

## Putting it together

We are assuming by this point that you've installed all of the appropriate Arduino IDE, USB drivers, have your Total Control Lighting strip connected to your Arduino via the Total Control Lighting developer shield, have soundflower installed and setup so that your mac is piping to soundflower as its output (refer to this very handy tutorial from sylvan advantage: <a href="http://www.sylvanadvantage.com/index.php/support/how-tos/65-3rd-party-applications-info/188-how-to-use-sound-flower" target="_blank">http://www.sylvanadvantage.com/index.php/support/how-tos/65-3rd-party-applications-info/188-how-to-use-sound-flower</a> ) and have all of the python modules mentioned above.

1. You'll need to download all of the code provided in both the *arduino* and *python* directories.
2. In the *arduino* folder, you'll find a *libraries* folder that contains a list of arduino libraries that you'll need to install in your Arduino IDE.
3. With your libraries installed, connect your arduino via a usb mini-port. You'll then need to compile and load the code in the PySerialTCLConnect.ino file.  This firmware will compile to over 16K so you'll at least need an arduino that has over that amount of memory, but I really recommend sticking with an arduino that fits the Total Control Lighting shield since it's extremely convenient.
4. With the firmware loaded on your arduino, if everything is looking correct, you'll see all of the lights on your Total Control Lighting display go blue.  This indicates the arduino is in "ready" mode.
5. Now we need to open up the contents of what's in the *python* directory.  You should find 2 files, sound2light.py and sound2color.py.  sound2color.py defines the base interface for taking audio flowing through your Mac, and turning it into arrays of color.  sound2light.py inherits from the base functionality of sound2color.py to interface with your attached arduino.

If all python modules are up to date, you can make sound2light.py executable and sound2color.py readable.  sound2light.py imports sound2color.py so make sure that they are sibling files on your mac.  When you execute sound2light.py, it should try to find a live USB serial connection to your arduino.  If it does, it will signal to the arduino of its intent to start streaming color packets.  

6. The 50 LEDs should turn from blue to green indicating that a handshake is made, and then the lights will go dark.  The sound2light script will then be sniffing for any audio coming through your computer speakers and using some simple beat detection, start sending color data to your light array.  

Here's a video of it in action (while listening to one of my favorite soundtracks from HBO's Band of Brothers):

http://youtu.be/WYXbA07cIvQ

The startup sequence for sound2light.py should look something like this:

<pre>
[HQ:git-repos/sound2light/python] mplanck% ./sound2light.py
pyo version 0.6.8 (uses single precision)
Testing usbserial port [ /dev/cu.usbserial-AH00ZL7N ]







tcl:ready
Using serial port [ /dev/cu.usbserial-AH00ZL7N ]
Success! -> sound2light
Handshake Confirmed!
Handshake Made With:  sound2light

Color Ramp Name: redtoblueramp
0       | *O----*-------@*-@*---@----@---*@-*@-------*----O |
1       | *O------*------*-*----@*--*@----*-*------*------O |
2       | *O--------*-----@0-@----------@-0@-----*--------O |
3       | *O-O-O------@---@------*@@*------@---@------O-O-O |                                                           
4       | -*O-0-----*O@----@---@------@---@----@O*-----0-O* |
5       | -----O-O--@-@----@---@--@@--@---@----@-@--O-O---- |
6       | ---------*@*@-@-@-----@O@@O@-----@-@-@*@*-------- |
7       | ------------@-@0@------O--O------@0@-@----------- |
8       | ------------@-@-@----------------@-@-@----------- |
9       | ------------@-@-@----------------@-@-@----------- |
10      | ------------@-@-@----------------@-@-@----------- |
11      | *------O-O--@------0-0------0-0------@--O-O------ |
12      | **-*-O-O----------------------------------O-O-*-* |
13      | *O----O-O--------------------------------O-O----O |
14      | *O--------*-*------------------------*-*--------O |
15      | *O----------**----------------------**----------O |                                                                      
</pre>

## What's going on in the audio processing?

I decided that I wanted the lights to "do something cool" whenever there was a beat in any audio playing through the speakers.  I could have done something much simpler where I just had the lights display the magnitude of an amplitude envelope.  In fact, that may be a future alternate script that I'll add to this project.

So I began with this very helpful article on how to find beat's in audio: <a href="http://archive.gamedev.net/archive/reference/programming/features/beatdetection/index.html" target="_blank">http://archive.gamedev.net/archive/reference/programming/features/beatdetection/index.html</a>

I massaged a lot of the suggested numbers as well as avoided working in decibels (which admittedly could have been a mistake) as there are still a lot of songs that give unpredictable results with this approach.

The overall idea is that I keep a running average of the amplitude of each frequency band for a period of time.  If there is a spike in the amplitude of the audio in which that spike exceeds a certain percentage of the average, then I consider that a beat.  In the cases where I'm listening to audio that has variance, I soften the threshold at which I determine something is a beat directly proportional to the amount of variance.

So when I do find a "beat" that exceeds a spike threshold, I mark the power of the beat by how much it exceeds that threshold.  For every beat detected at one of 16 evenly distributed frequencies (within the range of 20 hz to 18000 hz), the "intensity" or "impulse" of the beat is recorded as a "beat wave". 

## What's a beat wave?

The "beat wave" contains 3 meaningful numbers as its data - the current position of the wave (a float ranging from 0 to 24), the current velocity/power of the wave (a float ranging from 0 to 1), and the pitch/frequency band the beat wave represents (an integer ranging from 0 to 15).  When the beat wave is translated into color across 50 virtual lights, the position of the beat wave maps to a position on the array of colors as if the wave was eminating from the center of the 50 colors and then spreads out in a mirrored fashion towards the ends.  All beat waves start with position=0, and will begin their journey as a color at the center of the 50 color array, and when a beat has position=24, it will map to color on both the right and left ends of the array.  The velocity/power of each beat wave determines how fast that beat is travelling from the center of the 50 color array to the extremes as well as the intensity of the color to be displayed.  The pitch/frequency band index (0 -> 15) that the beat wave represents will be used to determine the base color that the wave will be turned into when placed on the 50 color array.  There is a linear 4 color gradient ramp that determines how the pitch index is turned into a color.  Every 30 seconds of the script, a new linear gradient ramp is selected and the script cycles through 4 presets - fire, aquablue, redtoblue, rgb.  You can easily add your own or modify the existing ramps by changing the code in sound2color.py ( search for fireramp ).

During each time step of the script (30 every second), beats are detected across the 16 frequency bands and added to a queue of beat waves (the script can have up to 300 beat waves at any given time and "old" beat waves are ejected to make room for .  All beat waves are turned into color on the 50 color array based on position, power and pitch as described above.  Then, each beat wave's position and velocity are updated.  The position is incremented by the simple formula p = v * dt where dt is arbitrarily chosen based on the selected ranges of position and velocity.  The velocity of each beat wave is updated so that it decreases by a percentage with each time step (like air drag), using the simple formula v = v - k * v * dt - c * dt, where k << 1 and c is a small constant (dt in this case is absorbed into k and c in my code and k*dt and c*dt are chosen arbitrarily for effect).

## sound2color and sound2light?

All of the logic above lives in the sound2color.py module so it tends to be the work horse of this setup.

sound2light.py implements the simple bit of taking this 50 color array and sending it as a compact packet of 50x3 bytes via serial to my attached arduino.  The firmware on the arduino then turns the byte data into SPI signals that lights up my 50 LED string of lights.

## Some online references I used to put this together

* Where to get the arduino IDE and learning firmware: <a href="http://www.arduino.cc/" target="_blank">http://www.arduino.cc/</a>

* Great resource for using the TCL library and the TCL shield: <a href="http://www.idolstarastronomer.com/Home/char-total_control_lighting" target="_blank">http://www.idolstarastronomer.com/Home/char-total_control_lighting</a>

* Where to get TCL lighting strips: <a href="http://www.coolneon.com/" target="_blank">http://www.coolneon.com/</a>

* Numpy reference: <a href="http://docs.scipy.org/doc/numpy/reference/" target="_blank">http://docs.scipy.org/doc/numpy/reference/</a>

* Pyo reference: <a href="https://code.google.com/p/pyo/" target="_blank">https://code.google.com/p/pyo/</a>

* Soundflower reference: <a href="http://www.sylvanadvantage.com/index.php/support/how-tos/65-3rd-party-applications-info/188-how-to-use-sound-flower" target="_blank">http://www.sylvanadvantage.com/index.php/support/how-tos/65-3rd-party-applications-info/188-how-to-use-sound-flower</a> 

* A handy break down of how to implement a crude beat detection: <a href="http://archive.gamedev.net/archive/reference/programming/features/beatdetection/index.html" target="_blank">http://archive.gamedev.net/archive/reference/programming/features/beatdetection/index.html</a>

<pre>The original github for this project: https://github.com/mplanck/sound2light</pre>

