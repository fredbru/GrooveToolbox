from ADTLib import ADT
import madmom
import numpy as np

np.set_printoptions(precision=2)
np.set_printoptions(suppress=True)

proc = madmom.features.tempo.TempoEstimationProcessor(fps=100)
act =  madmom.features.beats.RNNBeatProcessor()('JB 7.wav')
tempo = proc(act)

onsets = ADT(["JB 7.wav"], tab='no')
print(onsets)