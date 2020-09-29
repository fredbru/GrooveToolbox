# Example use of GrooveToolbox
# Load a groove from a BFD palette file. Calculate all rhythm and microtiming features from it.

from LoadGrooveFromBFDPalette import *
from LoadGrooveFromMIDI import *
from Groove import *
from SimilarityMetrics import *
from PlotGrooveData import *

hits1, timing1, tempo1 = get_groove_from_BFD_palette("Stanton Moore JB.bfd3pal", "JB 7")

#hitsMatrixMIDI, timingMatrixMIDI, tempo = get_groove_from_MIDI_file("MIDI/JB_7.mid", tempo=120, keymap="BFD")

JB7 = NewGroove(hits1, timing1, tempo1, velocity_type="None", extract_features=True, name="Stanton Moore JB")
# JB7.rhythmFeatures.getAllFeatures()
# JB7.rhythmFeatures.printAllFeatures()

hits2, timing2, tempo2 = get_groove_from_BFD_palette("Jazz Walk Sticks.bfd3pal", "Jazz Walk Sticks 2")
JWS2 = NewGroove(hits2, timing2, tempo2, velocity_type="None", extract_features=True, name="Stanton Moore JB9")

print(weighted_Hamming_distance(JB7, JWS2))
print(structural_similarity_distance(JB7, JWS2))