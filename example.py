# Example use of GrooveToolbox
# Load a groove from a BFD palette file. Calculate all rhythm and microtiming featuers from it.

from LoadGrooveFromBFDPalette import *
from Groove import *

fileName = "Stanton Moore JB.bfd3pal"
grooveName = "JB 20"

hitsMatrix, timingMatrix, tempo = getGrooveFromBFDPalette(fileName, grooveName)

JB20 = NewGroove(hitsMatrix, timingMatrix, tempo, velocityType="None", extractFeatures=True)