# Load groove from audio file into groovetoolbox format. Assumed whole number of bars, 4/4 time.
from ADTLib import ADT
import madmom
import numpy as np
from LoadGrooveFromBFDPalette import *

hitsMatrix, timingMatrix, tempo = getGrooveFromBFDPalette("Stanton Moore JB.bfd3pal", "JB 7")

#np.set_printoptions(precision=2)
np.set_printoptions(suppress=True)

tempoDetection = madmom.features.tempo.TempoEstimationProcessor(fps=100)
beatDetection = madmom.features.beats.BeatTrackingProcessor(fps=100)
act =  madmom.features.beats.RNNBeatProcessor()('Rock 17.wav')

beats = beatDetection(act) #assumes constant tempo through audio. Returns beats for all of audio

#4 equal spaces between each value in vector. Don't cut to bar length at this stage
allMetricalPositions = np.empty([0])
for i in range(beats.shape[0]-1):
    positionsInOneBeat = np.linspace(beats[i],beats[i+1],5)
    allMetricalPositions = np.hstack([allMetricalPositions,positionsInOneBeat[0:-1]])
print(beats)
onsets = ADT(["Rock 17.wav"], tab='no') # returns list of dicts - one for each instrument

kicks = onsets[0].get("Kick") #need to match these to metrical grid vector. Then extend to the nearest bar.
snares = onsets[0].get("Snare")
hihats = onsets[0].get("Hihat")

#for each onset
# find the closest metrical position (seconds)
# place that onset into the index of that metrical position
grooveMatrix = np.zeros([32,10]) #todo: assumes 2 bar loops

j = 0
for instrument in kicks, snares, hihats:
    for i in range(instrument.shape[0]):
        matchingMetricalPosition = (np.abs(allMetricalPositions-(instrument[i]))).argmin()
        if matchingMetricalPosition < 32: #predefined bar length
            grooveMatrix[matchingMetricalPosition,j] = 1.0 #no velocity information
    j+=1

print(grooveMatrix)

#both onsets in seconds and beat positions in seconds. i need to map this to a metrical grid assuming 4/4
# first step - create vector of metrical positions from beat positions - use np.arange?
# Need to chop to the nearest full bar (multiple of 4). This means remove elements of the beats vector.
    # This needs to be based on where the onsets are

#transcription to do:
# convert ADT time series format to beat positions
# somehow need to build a grid.
# Can madmom build a grid of tempo on top of the waveform...? yes, using BeatDetectionProcessor. also assumes constant tempo
# quantize to those beat positions (where do you place the metrical grid? place on the first beat or average?)
# To test this compare microtiming matricies of audio transcribed grooves vs BFD format parsed.
# BFD format takes 0 positions as start, with all kicks beginning on the 0 beat.

# Turn this into a function you call from example.py, with tempo as an optional argument
# Then build in MIDI loader
#