import numpy as np
from LoadGrooveFromBFDPalette import *

import pretty_midi

# BFD KEY MAP
#kick = 24
#hihatClosed = 37, 30
#snare = 26

mid = pretty_midi.PrettyMIDI('JB_7.mid')

pianoroll = mid.get_piano_roll()
#hits = np.array(mid.instruments[0].notes)
print(len(mid.instruments[0].notes))
hits = np.zeros([len(mid.instruments[0].notes),4])

i = 0
for instrument in mid.instruments:
    for note in instrument.notes:
        hits[i,0] = note.start
        hits[i,1] = note.velocity
        if note.pitch == 24:
            hits[i,2] = 0
        elif note.pitch == 26:
            hits[i,2] = 1
        elif note.pitch in [37,30]:
            hits[i,2] = 2
        i+=1
