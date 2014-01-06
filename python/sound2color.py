#!/usr/bin/python

import time
import sys
import numpy
import time
import math
import curses

# requires pyo: https://code.google.com/p/pyo/
from pyo import *

# ------------------------------------------------------------------------
# SIGNAL UTILITIES

def clamp(val, bottom, top):
    return min(top, max(bottom, val))

def clampedmix(bottom, top, x):
    return clamp(bottom * (1. - x) + top * x, bottom, top)

def smoothstep(val, bottom, top):
    t = (clamp(val, bottom, top) - bottom) / (top - bottom);
    return 3*t*t - 2*t*t*t;

def smoothremap(val, bottom, top, targetbottom, targettop):
    s = smoothstep(val, bottom, top)
    return targettop * s + targetbottom * (1. - s)

# ------------------------------------------------------------------------
# COLOR UTILITIES

# Have a smooth ramped color gradient that has 2 knots at the extremes 
# (val=0 and val=1) and 2 floating knots that can be at any location
# in between.
def colorgrad4(c1, c2, l1, c3, l2, c4, val):

    result = numpy.array([0., 0., 0.])

    v1 = smoothremap(val, 0., l1, 0., 1.)
    result = c1 * (1. - v1) + c2 * v1
    v2 = smoothremap(val, l1, l2, 0., 1.)
    result = result * (1. - v2) + c3 * v2
    v3 = smoothremap(val, l2, 1., 0., 1.)
    result = result * (1. - v3) + c4 * v3
    return result

# Returns a firey color given a value betweeen 0 and 1
def fireramp(val):
    return colorgrad4(numpy.array([255, 2, 49]),
                 numpy.array([204, 82, 6]), .22,
                 numpy.array([226, 159, 2]), .53,
                 numpy.array([232, 249, 247]),
                 val)

# Returns a classic red->green->blue color given a value betweeen 
# 0 and 1
def rgbramp(val):
    return colorgrad4(numpy.array([255, 1, 1]),
                 numpy.array([1, 255, 1]), .45,
                 numpy.array([1, 255, 1]), .55,
                 numpy.array([1, 1, 255]),
                 val)

# Returns a red->purple->blue color given a value betweeen 0 and 1
def redtoblueramp(val):
    return colorgrad4(numpy.array([255, 1, 1]),
                 numpy.array([128, 1, 129]), .3,
                 numpy.array([20, 1, 250]), .55,
                 numpy.array([1, 1, 255]),
                 val)

# Returns a subtle ramp through an aqua blue given a value betweeen 0 and 1
def aquablueramp(val):
    return colorgrad4(numpy.array([105, 177, 244]),
                 numpy.array([12, 46, 242]), .25,
                 numpy.array([98, 88, 239]), .71,
                 numpy.array([138, 147, 247]),
                 val)

# ------------------------------------------------------------------------
# Base class used for processing sound coming through soundflower and turning
# into a 50 color array.  This 50 color array is abstract in this class but
# can be pushed out to a light display by implementing output().

# Key functions:

#   start(outputAudio=True or False) :
#     Called to start the audio server as well as create audio signal processing
#     objects that can be used in update.
#     If outputAudio is set to True, then we pipe the input audio to the output
#     speakers of the current computer.  This usually defaults to false since
#     soundflower can be responsible for piping to the right output.
#

#   shutdown( ):
#     Called to properly close down the audio server.  Can be inherited to add
#     additional objects to shutdown.  Shutdown should be called in a try:finally
#     block.

#   update( ): <-- can override to change how audio is processed
#     Called at each time step to update the internal color array state based on
#     the state of the audio server.  update is where the beat detection happen.
#

#   output( ): <-- can override to output to more than just text to the terminal
#      Called at each time step to push the colorarray data to a meaningful output
#      The default implementation prints to the terminal.  You can see that in
#      sound2light, there is an output function in the subclass
#      SoundToLightProcessor that extends output() to send serial messages to the
#      arduino

class SoundToColorProcessor(object):

    NUM_FREQUENCY_BANDS = 16
    NUM_AVERAGE_SAMPLES = 80

    def __init__(self):

        self.beatstored = numpy.ndarray(SoundToColorProcessor.NUM_FREQUENCY_BANDS) 
        self.colorarray = numpy.zeros([50,3])
        self.perpitcharray = numpy.zeros([SoundToColorProcessor.NUM_FREQUENCY_BANDS,50])

        # allow up to 300 beats, each beat captures        
        # 0 index := position on the slider of the current beat
        # 1 index := power/velocity of the current beat
        # 2 index := [0,NUM_FREQUENCY_BANDS] value that captures the pitch of 
        #     the beat (lower value means more of a bass)

        self.beatwave = numpy.zeros([300,3])

        self.stdscr = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()

        # This is the pyo sound server that will be grabbing color from the 
        # soundflower input.
        self.server = Server(sr=44100, nchnls=2, buffersize=1024)

        self.inputDeviceIdx = -1;
        self.outputDeviceIdx = -1;

        inputs, outputs = pa_get_devices_infos()
        for idx,info in inputs.iteritems():
            sound2color2ch = 'Soundflower (2ch)'
            if sound2color2ch == info.get('name', None):
                print "Found input device ( %(sound2color2ch)s ]: %(idx)i " % locals()
                self.inputDeviceIdx = idx

        for idx,info in outputs.iteritems():      
            builtinOutput = 'Built-in Output'      
            if 'Built-in Output' == info.get('name', None):
                print "Found input device [ %(builtinOutput)s ]: %(idx)i " % locals()
                self.outputDeviceIdx = idx


        self.server.setInputDevice(self.inputDeviceIdx)
        self.server.setOutputDevice(self.outputDeviceIdx)

        self.server.boot()
        self.starttime = time.time()

        # This is the color ramp function that we will use to process the sound
        # beats into color based on pitch.
        self.colorramp = fireramp

    def start(self, outputAudio=False):
        # Fire up the pyo sound server and prepare the audio inputs so that 
        # it is split up into frequency bands.  Also create simple sound 
        # analysis objects that we will use for beat detection.

        # beat detection algorithm inspired by:
        # http://archive.gamedev.net/archive/reference/programming/features/beatdetection/index.html

        self.server.start()

        self.leftinput = Input(chnl=1)
        self.rightinput = Input(chnl=0)

        self.leftbands = BandSplit(self.leftinput, 
            num=SoundToColorProcessor.NUM_FREQUENCY_BANDS, min=20, max=18000)
        self.rightbands = BandSplit(self.rightinput, 
            num=SoundToColorProcessor.NUM_FREQUENCY_BANDS, min=20, max=18000)

        self.leftinstamp = Average( Follower( self.leftbands ), size=1024 )
        self.rightinstamp = Average( Follower( self.rightbands ), size=1024 )

        self.energysamples = numpy.ndarray([SoundToColorProcessor.NUM_FREQUENCY_BANDS,
            SoundToColorProcessor.NUM_AVERAGE_SAMPLES])

        self.energysamples.fill(-1.)

        if outputAudio:
            self.leftinput.out(chnl=1)
            self.rightinput.out(chnl=0)

    def shutdown(self):
        # Called when closing the app
        curses.echo()
        curses.nocbreak()
        curses.endwin()      

    def _processBeat(self):

        leftsamps = numpy.array(self.leftinstamp.get(all=True))
        rightsamps = numpy.array(self.rightinstamp.get(all=True))

        energyinsts = leftsamps*leftsamps + rightsamps*rightsamps;

        # right shift by 1 along the axis for number of samples, 
        # there is a set of samples per band.
        self.energysamples = numpy.roll(self.energysamples, 1, axis=1)
        self.energysamples.transpose()[0] = energyinsts

        # if we haven't buffered up NUM_AVERAGE_SAMPLES samples, then
        # we don't have enough data yet
        if self.energysamples[0][-1] < 0.:
            return

        energyavgs = numpy.average(self.energysamples, axis=1)        

        # if the sound is so soft, then don't consider it worth
        # processing.
        if numpy.max(energyavgs) < .00001:
            return

        variances = self.energysamples - energyavgs.reshape((energyavgs.shape[0],1))
        variances *= variances;

        Vs = numpy.average(variances, axis=1)        
        Cs = -1000000. * Vs + 1.5

        currtime = time.time()
        for i in range(energyinsts.shape[0]):
            energyinst = energyinsts[i]
            energyavg = energyavgs[i]
            if ( energyinst > energyavg * Cs[i]):
                energyratio = energyinst / (energyavg * Cs[i])
                if (self.beatstored[i] < energyratio):
                    self.beatstored[i] = energyratio

    def _addBeat(self, power, pitch):

        # shift another beat onto the queue
        self.beatwave = numpy.roll(self.beatwave, 1, axis=0)

        self.beatwave[0][0] = 0.;
        self.beatwave[0][1] = power/100.;
        self.beatwave[0][2] = pitch

    def _updateColorRamp(self):
        elapsed = time.time() - self.starttime;

        reltime = elapsed%120
        if reltime <= 30:
            self.colorramp = fireramp
        elif reltime > 30 and reltime <= 60:
            self.colorramp = aquablueramp
        elif reltime > 60 and reltime <= 90:
            self.colorramp = redtoblueramp
        elif reltime > 90 and reltime <= 120:
            self.colorramp = rgbramp

    def update(self):

        # Called during every frame color update to find beats across all 
        # frequencies.  This will update the self.colorarray internal member
        # data which stores the values of the 50 colors we play to push out 
        # to the TLC controller

        self._updateColorRamp()
        self._processBeat()

        maxbeatpower = 0.;
        maxbeatpitch = 0.;
        for i in range(self.beatstored.shape[0]):        
            amp = 0.
            if self.beatstored[i] > 0.:
                amp = self.beatstored[i]
                self.beatstored[i] = 0.

            beatpower = smoothremap(amp, 1., 1.5, 0., 100.)
 
            self._addBeat(beatpower, i)

        self.colorarray.fill(0)  
        self.perpitcharray.fill(0)  

        for i in range(self.beatwave.shape[0]):

            beatpower = self.beatwave[i][1]
            beatpitch = int(self.beatwave[i][2])
            beatcolor = self.colorramp(float(beatpitch)/SoundToColorProcessor.NUM_FREQUENCY_BANDS)

            if beatpower > 0.:
                beatpos = clamp(int(self.beatwave[i][0]), 0, 24)

                self.perpitcharray[beatpitch][25 + beatpos] = beatpower;
                self.perpitcharray[beatpitch][24 - beatpos] = beatpower;

                redcolors = numpy.zeros(50)
                greencolors = numpy.zeros(50)
                bluecolors = numpy.zeros(50)

                # Have the beats travel from the center out to the left and right
                # in a mirrored way
                redcolors[25 + beatpos] = beatcolor[0]
                redcolors[24 - beatpos] = beatcolor[0]

                greencolors[25 + beatpos] = beatcolor[1]
                greencolors[24 - beatpos] = beatcolor[1]
                
                bluecolors[25 + beatpos] = beatcolor[2]
                bluecolors[24 - beatpos] = beatcolor[2]

                # Spread the travelling beat across 3 color leds using a convolve
                ckernel = 3. * (1./float(SoundToColorProcessor.NUM_FREQUENCY_BANDS)) * numpy.array([1., 1., 1.])

                self.colorarray.transpose()[0] += numpy.convolve(redcolors, ckernel, mode="same")
                self.colorarray.transpose()[1] += numpy.convolve(greencolors, ckernel, mode="same")
                self.colorarray.transpose()[2] += numpy.convolve(bluecolors, ckernel, mode="same")              

                # update the beatwave position with the velocity/power of the beat
                # slow down the power of the beat at every update using a "drag" plus
                # plus a small constant
                self.beatwave[i][0] = clamp(self.beatwave[i][0] + 3. * self.beatwave[i][1], 0, 24)
                self.beatwave[i][1] = max(0., self.beatwave[i][1] - .08 * self.beatwave[i][1] - .01);

    def _getColorPair(self, idx):

        coloridx = idx+1
        fg, bg = curses.pair_content(coloridx)
        if (fg + bg) == 0:

            nidx = float(idx)/SoundToColorProcessor.NUM_FREQUENCY_BANDS
            fg = int(7 * nidx + 1)
            bg = curses.COLOR_BLACK

            curses.init_pair(coloridx, fg, bg)

        return coloridx

    def output(self):       

        ramptxt = "Color Ramp Name: %s" % self.colorramp.func_name
        self.stdscr.addstr(0, 0, ramptxt) 

        for pitchIdx in range(self.perpitcharray.shape[0]):
            coloridx = self._getColorPair(pitchIdx)
            ascii = "%(pitchIdx)i\t| " % locals()

            for ledIdx in range(self.perpitcharray.shape[1]-1,0,-1):
                power = self.perpitcharray[pitchIdx][ledIdx]

                if power < 0.1:
                    ascii += "-"
                elif power < 0.2:
                    ascii += "*"
                elif power < 0.3:
                    ascii += "O"
                elif power < 0.4:
                    ascii += "0"
                else:
                    ascii += "@"

            ascii += " |\n"
            self.stdscr.addstr(pitchIdx+1,0,ascii, curses.color_pair(coloridx))

        self.stdscr.refresh()

        return True


    def gui(self):
        self.server.gui(self.__dict__)

if __name__ == "__main__":
    s2cprocessor = SoundToColorProcessor()
    s2cprocessor.start(outputAudio=False)

    try:
        while True:

            s2cprocessor.update()
            s2cprocessor.output()
            time.sleep(1./30.)

    finally:
        s2cprocessor.shutdown()

