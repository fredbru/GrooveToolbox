# Example use of GrooveToolbox
# Load a groove from a BFD palette file. Calculate all rhythm and microtiming features from it.

from LoadGrooveFromBFDPalette import *
from Groove import *

fileName = "Glam Get Down.bfd3pal"
grooveName = "Glam Get Down 7"

hitsMatrix, timingMatrix, tempo = getGrooveFromBFDPalette(fileName, grooveName)

JB20 = NewGroove(hitsMatrix, timingMatrix, tempo, velocityType="None", extractFeatures=True)
print(JB20.getReducedGroove())