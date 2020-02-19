# Example use of GrooveToolbox
# Load a groove from a BFD palette file. Calculate all rhythm and microtiming features from it.

from LoadGrooveFromBFDPalette import *
from LoadGrooveFromMIDI import *
from Groove import *
from SimilarityMetrics import *

fileName = "JB_7.midi"
grooveName = "Soul Blues 18"

hitsMatrixBFD, timingMatrixBFD, tempoBFD = getGrooveFromBFDPalette("Stanton Moore JB.bfd3pal",
                                                                   "JB 7")

hitsMatrixMIDI, timingMatrixMIDI, tempo = getGrooveFromMIDIFile("MIDI/JB_7.mid", tempo=120, keymap="BFD")

print(timingMatrixBFD)
print(timingMatrixMIDI)

JB20 = NewGroove(hitsMatrixMIDI, timingMatrixMIDI, tempo, velocityType="None", extractFeatures=True)