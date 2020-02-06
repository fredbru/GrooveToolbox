# Example use of GrooveToolbox
# Put in a folder of 8 example loops in numpy format - like the ones that I sent Olivier ages ago.
# Then people just starting out can have a go at doing the analysis using data that
# definitely works.

def addRelativePathToSystemPath(relPath):
    if __name__ == '__main__' and __package__ is None:
        from os import sys, path
        sys.path.append(path.join(path.dirname(path.abspath(__file__)), relPath))

addRelativePathToSystemPath("../shared")

from LoadGrooveFromBFDPalette import *
from Groove import *

fileName = "Stanton Moore JB.bfd3pal"
grooveName = "JB 20"

hitsMatrix, timingMatrix, tempo = getGrooveFromBFDPalette(fileName, grooveName)

GlamGetDown5 = NewGroove(hitsMatrix, timingMatrix, tempo, velocityType="None")

# print(GlamGetDown5.rhythmFeatures.getLowSyncopation())
# print(GlamGetDown5.rhythmFeatures.getMidSyncopation())
# print(GlamGetDown5.rhythmFeatures.getHighSyncopation())
# print(GlamGetDown5.rhythmFeatures.getPolyphonicSyncopation())
# print(GlamGetDown5.rhythmFeatures.getTotalSymmetry())
# print(GlamGetDown5.groove10Parts)
# print(GlamGetDown5.microtimingFeatures.microtimingMatrix)
