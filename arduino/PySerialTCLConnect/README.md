# Arduino firmware and accompanying python interface for the sound2light application

<pre>The original github for this project: https://github.com/mplanck/sound2light</pre>

A Total Control Lighting strip with the PySerialTCLConnect firmware with a
python serial interface.  An example of it working:


This project tutorial assumes the user knows how to setup, compile and install
Arduino firmware, has a familiarity with python, 

## Some references:

<ul>
    <li>Where to get the arduino IDE and learning firmware: <a href="http://http://www.arduino.cc/" target="_blank">http://http://www.arduino.cc/</a>

    <li>Great resource for using the TCL library and the TCL shield: <a href="http://www.idolstarastronomer.com/Home/char-total_control_lighting" target="_blank">http://www.idolstarastronomer.com/Home/char-total_control_lighting</a>

    <li>Where to get TCL lighting strips: <a href="http://www.coolneon.com/" target="_blank">http://www.coolneon.com/</a>
</ul>

## Hardware used:

Total Control Lighting 50 LED strip (with accompanying 5V usb connection and 5V AC/DC adapter)
Seeeduino v3.0
Total Control Lighting Developer Shield v4.1

Libraries you need to import into your Arduino before compiling PySerialTCLConnect.ino.

<ul>
    <li>SPI (comes builtin with Arduino)
    <li>TCL (comes in the github for convenience - original: <a href="https://bitbucket.org/devries/arduino-tcl">https://bitbucket.org/devries/arduino-tcl</a>)
    <li>pgmStrToRAM (comes in the github for convenience - original: <a href="https://github.com/mpflaga/Arduino-MemoryFree.git">https://github.com/mpflaga/Arduino-MemoryFree.git</a>)

    <li>TCLUtils (comes in the github - original for this project)
    <li>StringUtils (comes in the github - original for this project)
    <li>ArduinoUtils (comes in the github - original for this project)
    <li>ColorUtils (comes in the github - original for this project)
</ul>