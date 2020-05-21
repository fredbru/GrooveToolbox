# Example use of GrooveToolbox
# Load a groove from a BFD palette file. Calculate all rhythm and microtiming features from it.

from LoadGrooveFromBFDPalette import *
from LoadGrooveFromMIDI import *
from Groove import *
from SimilarityMetrics import *
from PlotGrooveData import *

fileName = "JB_7.midi"
grooveName = "Soul Blues 18"

hitsMatrixBFD, timingMatrixBFD, tempoBFD = getGrooveFromBFDPalette("Stanton Moore JB.bfd3pal", "JB 7")

#hitsMatrixMIDI, timingMatrixMIDI, tempo = getGrooveFromMIDIFile("MIDI/JB_7.mid", tempo=120, keymap="BFD")

JB7 = NewGroove(hitsMatrixBFD, timingMatrixBFD, tempoBFD, velocityType="None", extractFeatures=True, name="Stanton Moore JB")
# JB7.rhythmFeatures.getAllFeatures()
# JB7.rhythmFeatures.printAllFeatures()

hits2, timing2, tempo2 = getGrooveFromBFDPalette("Jazz Walk Sticks.bfd3pal", "Jazz Walk Sticks 2")
JWS2 = NewGroove(hits2, timing2, tempo2, velocityType="None", extractFeatures=True, name="Stanton Moore JB9")

print(weightedHammingDistance(JB7, JWS2))
print(structuralSimilarity(JB7, JWS2))