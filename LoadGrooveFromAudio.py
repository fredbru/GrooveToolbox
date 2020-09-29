# Load groove from audio file into groovetoolbox format. Assumed whole number of bars, 4/4 time.
from ADTLib import ADT
import madmom
import numpy as np
from LoadGrooveFromBFDPalette import *

hits_matrix, timing_matrix, tempo = get_groove_from_BFD_palette("Stanton Moore JB.bfd3pal", "JB 7")

tempo_detection = madmom.features.tempo.TempoEstimationProcessor(fps=100)
beat_detection = madmom.features.beats.BeatTrackingProcessor(fps=100)
act =  madmom.features.beats.RNNBeatProcessor()('JB 7.wav')

beats = beat_detection(act) #assumes constant tempo through audio. Returns beats for all of audio

#4 equal spaces between each value in vector. Don't cut to bar length at this stage
all_metrical_positions = np.empty([0])
for i in range(beats.shape[0]-1):
    positions_in_one_beat = np.linspace(beats[i],beats[i+1],5)
    all_metrical_positions = np.hstack([all_metrical_positions,positions_in_one_beat[0:-1]])
print(beats)
onsets = ADT(["JB 7.wav"], tab='no') # returns list of dicts - one for each instrument

kicks = onsets[0].get("Kick") #need to match these to metrical grid vector. Then extend to the nearest bar.
snares = onsets[0].get("Snare")
hihats = onsets[0].get("Hihat")

print(kicks)
print(snares)
print(hihats)

#for each onset
# find the closest metrical position (seconds)
# place that onset into the index of that metrical position
groove_matrix = np.zeros([32,10]) #todo: assumes 2 bar loops

j = 0
for instrument in kicks, snares, hihats:
    for i in range(instrument.shape[0]):
        matching_metrical_position = (np.abs(all_metrical_positions-(instrument[i]))).argmin()
        if matching_metrical_position < 32: #predefined bar length
            groove_matrix[matching_metrical_position,j] = 1.0 #no velocity information
    j+=1

print(groove_matrix)
print(groove_matrix.shape)

#both onsets in seconds and beat positions in seconds. i need to map this to a metrical grid assuming 4/4
# first step - create vector of metrical positions from beat positions - use np.arange?
# Need to chop to the nearest full bar (multiple of 4). This means remove elements of the beats vector.
    # This needs to be based on where the onsets are

#transcription to do:
# convert ADT time series format to beat positions
# somehow need to build a grid.
# quantize to those beat positions (where do you place the metrical grid? place on the first beat or average?)
# To test this compare microtiming matricies of audio transcribed grooves vs BFD format parsed.
# BFD format takes 0 positions as start, with all kicks beginning on the 0 beat.

# Turn this into a function you call from example.py, with tempo as an optional argument
# Then build in MIDI loader
#