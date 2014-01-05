# sound2light arduino and total control lighting project

## The short and sweet:

Turn any sound flowing through my Mac into a colorful light display using the "Cool Neon" Total Control Lighting strip.

## The nerd-tastic description: 

Using soundflower to sniff audio flowing through my Mac, a python script processes this audio using pyo to find beats at different frequencies.  The python script turns the beat at each frequency into a pulse that travels from the center of the 50 LED array.  Each pulse is colored differently based on the frequency it represents.  

These color pulses are added on top of each other to represent a 50x1 LED display.  Each color is only 3 bytes (256 possible colors per red green and blue).  This colored array is then messaged via serial to an arduino.  The arduino has firmware that then turns those serial messages into SPI messages which it sends to the controllers of a 50 LED Total Control Lighting strip.  Unfortunately, I am limited to only 50 LEDs and a 30 fps refresh rate considering the slow baud rate of serial.  A future version of this tech should use the ftdi bit bang approach so we can get a lot more bits through the baud rate: <a href="http://hackaday.com/2009/09/22/introduction-to-ftdi-bitbang-mode/">http://hackaday.com/2009/09/22/introduction-to-ftdi-bitbang-mode/</a>

Here it is in action:

<iframe width="853" height="480" src="//www.youtube-nocookie.com/embed/OuHVeVGlFm0?rel=0" frameborder="0" allowfullscreen></iframe>

<p>
This project tutorial assumes the user knows how to setup, compile and install Arduino firmware, has a familiarity with Mac OS (installing python modules and soundflower) and has a familiarity with python.
</p>

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

We are assuming by this point that you've installed all of the appropriate Arduino IDE, USB drivers, have your Total Control Lighting strip connected to your Arduino via the Total Control Lighting developer shield and have all of the python modules mentioned above.

1. You'll need to download all of the code provided in both the *arduino* and *python* directories.
2. In the *arduino* folder, you'll find a *libraries* folder that contains a list of arduino libraries that you'll need to install in your Arduino IDE.
3. With your libraries installed, connect your arduino via a usb mini-port. You'll then need to compile and load the code in the PySerialTCLConnect.ino file.  This firmware will compile to over 16K so you'll at least need an arduino that has over that amount of memory, but I really recommend sticking with an arduino that fits the Total Control Lighting shield since it's extremely convenient.
4. With the firmware loaded on your arduino, if everything is looking correct, you'll see all of the lights on your Total Control Lighting display go blue.  This indicates the arduino is in "ready" mode.
5. Now we need to open up the contents of what's in the *python* directory.  You should find 2 files, sound2light.py and sound2color.py.  sound2color.py defines the base interface for taking audio flowing through your Mac, and turning it into arrays of color.  sound2light.py inherits from the base functionality of sound2color.py to interface with your attached arduino.

If all python modules are up to date, you can make sound2light.py executable and sound2color.py readable.  sound2light.py imports sound2color.py so make sure that they are sibling files on your mac.  When you execute sound2light.py, it should try to find a live USB serial connection to your arduino.  If it does, it will signal to the arduino of its intent to start streaming color packets.  

The 50 LEDs should turn from blue to green indicating that a handshake is made, and then the lights will go dark.  The sound2light script will then be sniffing for any audio coming through your computer speakers and using some simple beat detection, start sending color data to your light array.

Here's a video of it in action:

<iframe width="853" height="480" src="//www.youtube-nocookie.com/embed/WYXbA07cIvQ?list=PLglW061yc38NzTpgAaUoSCpULON8Hp_bE" frameborder="0" allowfullscreen></iframe>

<pre>The original github for this project: https://github.com/mplanck/sound2light</pre>

