# sound2light arduino and total control lighting project

<pre>The original github for this project: https://github.com/mplanck/sound2light</pre>

## The short and sweet:

Turn any sound flowing through my Mac into a colorful light display using the "Cool Neon" Total Control Lighting strip.

## The nerd-tastic description: 

Using soundflower to sniff audio flowing through my Mac, I wrote a python script that processes this audio using pyo and finds beats at different frequencies.  It creates a color array display that it then messages to my arduino via serial.  The arduino has firmware that then turns those serial messages into SPI messages which it sends to the controllers of a 50 LED Total Control Lighting strip.  Unfortunately, I am limited to only 50 LEDs and a 30 fps refresh rate considering the slow baud rate of serial.  A future version of this tech should use the ftdi bit bang approach so we can get a lot more bits through the baud rate: <a href="http://hackaday.com/2009/09/22/introduction-to-ftdi-bitbang-mode/">http://hackaday.com/2009/09/22/introduction-to-ftdi-bitbang-mode/</a>

Here it is in action:


<pre>
This project tutorial assumes the user knows how to setup, compile and install
Arduino firmware, has a familiarity with Mac OS (installing python modules and soundflower) and has a familiarity with python.
</pre>

## Some online references I used to put this together

* Where to get the arduino IDE and learning firmware: <a href="http://http://www.arduino.cc/" target="_blank">http://http://www.arduino.cc/</a>

* Great resource for using the TCL library and the TCL shield: <a href="http://www.idolstarastronomer.com/Home/char-total_control_lighting" target="_blank">http://www.idolstarastronomer.com/Home/char-total_control_lighting</a>

* Where to get TCL lighting strips: <a href="http://www.coolneon.com/" target="_blank">http://www.coolneon.com/</a>

* Numpy reference: <a href="http://docs.scipy.org/doc/numpy/reference/" target="_blank">http://docs.scipy.org/doc/numpy/reference/</a>

* Pyo reference: <a href="http://docs.scipy.org/doc/numpy/reference/" target="_blank">http://docs.scipy.org/doc/numpy/reference/</a>

## First the Ingredients

### Hardware used:

* iMac 27-inch Late 2012 model (but works fine on my Late 2012 laptop as well)
* Total Control Lighting 50 LED strip (with accompanying 5V usb connection and 5V AC/DC adapter)
* Seeeduino v3.0 (connected to Mac via mini-USB)
* Total Control Lighting Developer Shield v4.1

### Software used:

* Mac OS X 10.8.5 
* Arduino IDE (download here: <a href="http://http://www.arduino.cc/" target="_blank">http://http://www.arduino.cc/</a>) 
** Note you'll also need to download the FTDI USB drivers to setup an arduino (http://arduino.cc/en/Guide/Howto)
* Sublime Text 2 (my editor of choice: <a href="http://www.sublimetext.com/" target="_blank">http://www.sublimetext.com/</a> )
* Soundflower v1.6.6 ( <a href="https://www.macupdate.com/app/mac/14067/soundflower" target="_blank">https://www.macupdate.com/app/mac/14067/soundflower</a> )
* python2.7
* 

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

## Connecting up the hardware

The 

