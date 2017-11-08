#!/usr/bin/python

from dotstar import Adafruit_DotStar

numpixels = 300          # Number of LEDs in strip
pixelrow = 30 			# num in LEDs in one row

# Here's how to control the strip from any two GPIO pins:
datapin   = 23
clockpin  = 24
strip     = Adafruit_DotStar(numpixels, 12000000)


strip.begin()           # Initialize pins for output

# Load image in RGB format and get dimensions:


print "turning off..."

strip.clear()
strip.show()