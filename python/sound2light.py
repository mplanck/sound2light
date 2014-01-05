#!/usr/bin/python

import sound2color

import time
import sys
import numpy
import math

# requires pyserial: http://pyserial.sourceforge.net/
import serial

# ------------------------------------------------------------------------
# TCLSerial CLASSES

# "Struct" class used to pass around serial state
class TCLSerialOutput(object):
    
    def __init__(self):

        self.handshakeConfirmed = False
        self.handshakeProgram   = "Unknown"
        self.serialHadOutput    = False
        self.serialMessage      = ""
        self.beginColor         = False

# Class used to manage the serial connection.  Used for sending and 
# receiving messages.

#   Valid messages to send (and corresponding responses):
#    - tcl:handextended:<program name>!
#    -- response: tcl:handreceived:<program name>\n

#    - tcl:handreceived:<program name>!
#    -- response: tcl:handshakeconfirmed:<program name>\n

#    - tcl:status!
#    -- response: tcl:handshakeconfirmed:1 or 0\ntcl:handshakeprogram:<program name>\n

#    - tcl:colorbegin!
#    -- response: tcl:colorbeginreceived:<program name>\n

class TCLSerialManager(object):
    
    def __init__(self, serialConnection):
        self.sconnect    = serialConnection



    def _FormatMessage(self, instruction, args):

        msg = "tcl:%(instruction)s" % locals()

        if args:
            msg += ":%(args)s" % locals()

        msg += "!"
        return msg



    def SendMessage(self, instruction, args=""):

        if not self.sconnect.writable():
            raise Exception("Unable to write to [ %s ]" % str(self.sconnect))

        while(self.sconnect.outWaiting()):
            print "Waiting for %s to write" % str(self.sconnect)
            time.sleep(.1)

        self.sconnect.flushInput()

        if self.sconnect.isOpen():        
            self.sconnect.write(self._FormatMessage(instruction, args))

        self.sconnect.flush()
        return True


    def SendColorBytes(self, bytesData):

        if not self.sconnect.writable():
            raise Exception("Unable to write to [ %s ]" % str(self.sconnect))

        while(self.sconnect.outWaiting()):
            print "Waiting for %s to write" % str(self.sconnect)
            time.sleep(.1)

        # The leading '*' char is a special character used by the arduino
        # firmware to know that this is a pack of color data
        rawBytes = '*' + reduce(lambda x,y:x+y, map(chr, bytesData))    
        self.sconnect.write(rawBytes)   

        return True



    def ReceiveMessage(self):

        maxNumAttempts = 5
        numAttempts = 0

        output = TCLSerialOutput()
        result = []

        while numAttempts < maxNumAttempts:

            try:
                result.extend(self.sconnect.readlines())

            except serial.SerialTimeoutException:
                print("Unable to read data from [ %s ] " % str(self.sconnect))
                return output

            validLines = []
            for line in result:

                strippedline = line.strip("\r\n")
                if strippedline:
                    validLines.append(strippedline)

            for line in validLines:

                tokens = line.split(":")

                if (len(tokens) > 2):
                    serialHeader, serialInstruction = tokens[:2]

                    if serialHeader != "tcl":
                        output.serialMessage += line + "\n"

                    if serialInstruction == "handreceived":
                        print "Success! -> " + tokens[2]
                        output.handshakeConfirmed = True
                        output.handshakeProgram = tokens[2]
                        output.serialHadOutput = True

                    if serialInstruction == "handshakeconfirmed":
                        handshake = int(tokens[2])
                        if handshake:
                            print "Handshake Confirmed!"
                        else:
                            print "Handshake Not Made!"

                        output.handshakeConfirmed = handshake
                        output.serialHadOutput = True

                    if serialInstruction == "colorbeginreceived":
                        output.handshakeProgram = tokens[2]
                        output.serialHadOutput = True
                        output.beginColor = True


                    if serialInstruction == "handshakeprogram":
                        output.handshakeProgram = tokens[2]
                        print "Handshake Made With: " + output.handshakeProgram
                        output.serialHadOutput = True

                else:
                    output.serialMessage += line + "\n"

            if output.serialHadOutput:
                break

            numAttempts += 1
        
        self.sconnect.flushInput()
        return output



    def SendMessageAndListen(self, instruction, args=""):

        output = TCLSerialOutput()
        if self.SendMessage(instruction, args):
            time.sleep(.1)
            output = self.ReceiveMessage()
            if output.serialMessage:
                print output.serialMessage

        return output

# ------------------------------------------------------------------------
# TCLSerial CLASS

# This processor finds the serial connection to a connected arduino device
# and then overrides it's parent's output method to turn the color array
# data into serial messages to the TCL device.

class SoundToLightProcessor(sound2color.SoundToColorProcessor):

    def __init__(self):

        import serial.tools.list_ports
        self.serialPort = None

        ttys = serial.tools.list_ports.comports()

        for tty in ttys:
            portName = tty[0] 
            if "usbserial" not in portName:
                continue

            print "Testing usbserial port [ %s ]" % portName

            try:
                self.sconnect = serial.Serial(portName, 115200, 
                                                bytesize=serial.EIGHTBITS)

                if not self.sconnect.isOpen():
                    print "Could not open port"

                self.sconnect.setTimeout(.1)

                if not self._checkTCLReady():
                    print("Unable to connect [ %s ] could not get a tcl:ready "
                        "message " % str(self.sconnect))
                else:
                    self.serialPort = portName 
                    break

            except Exception, e:
                print("Could not connect to light display using port [ %s ]" % 
                    portName)

        if self.serialPort:
            print "Using serial port [ %s ]" % self.serialPort
        else:
            print "Unable to find a usb serial port that could be serving display"
            sys.exit(1)

        self.serialmgr = TCLSerialManager(self.sconnect)

        output = self.serialmgr.SendMessageAndListen("handextended", "sound2light")
        if output.handshakeConfirmed:
            self.serialmgr.SendMessageAndListen("status")

        output = self.serialmgr.SendMessageAndListen("colorbegin")

        sound2color.SoundToColorProcessor.__init__(self)

    def _checkTCLReady(self):
        
        maxNumAttempts = 10
        attempts = 0
        while (attempts < maxNumAttempts):
            line = self.sconnect.readline()
            strippedline = line.strip()
            print strippedline
            if strippedline == "tcl:ready":
                time.sleep(.5)
                return True

            time.sleep(.1)
            attempts += 1

        return False

    @staticmethod
    def convertToByte(x):
        byte = int(sound2color.clamp(math.floor(x), 0, 255))

        # 42 is a special byte that declares the head of a frame
        # of lights, so we avoid outputting that byte as a color
        if byte == 42:
            return 43
        else:
            return byte

    def shutdown(self):
        sound2color.SoundToColorProcessor.shutdown(self)
        self.sconnect.flush()
        self.sconnect.close()

    def output(self):

        # Simple extension of output to take the colorarray processed in 
        # update and turn output it via 
        superResult = sound2color.SoundToColorProcessor.output(self)

        colorData = list(numpy.ravel(map(SoundToLightProcessor.convertToByte, 
                                         self.colorarray.ravel())))

        if not self.serialmgr.SendColorBytes(colorData):
            return False
        else:
            return superResult


if __name__ == "__main__":
    s2lprocessor = SoundToLightProcessor()
    s2lprocessor.start(outputAudio=False)

    try:
        while True:

            s2lprocessor.update()
            s2lprocessor.output()
            # Since we are bound by the baudrate of serial, we can at best
            # get 30 fps when sending 3 bytes * 50 LED colors per frame of 
            # color set.
            time.sleep(1./30.)

    finally:
        s2lprocessor.shutdown()
