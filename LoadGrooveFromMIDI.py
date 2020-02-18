import numpy as np
import pretty_midi

def getGrooveFromMIDIFile(filename, tempo=None):
    # Extract a groove from a MIDI file
    midi = pretty_midi.PrettyMIDI(filename)
    if tempo == None:
        tempo = midi.estimate_tempo() #todo: tempo estimation seems to fail a lot
    hits = _getAllHitInfo(midi, tempo)

    hitsMatrix = np.zeros([32, 10])  # todo: work with loops of arbritrary length
    timingMatrix = np.zeros([32, 10])
    timingMatrix[:] = np.nan

    for j in range(hits.shape[0]):
        timePosition = int(hits[j, 0] * 4)
        kitPiecePosition = int(hits[j, 2])
        timingMatrix[timePosition % 32, kitPiecePosition] = hits[j, 3]
        hitsMatrix[timePosition % 32, kitPiecePosition] = hits[j, 1]
    return hitsMatrix, timingMatrix, tempo


def _getAllHitInfo(midi, tempo):
    # Create an array of all hits in a groove
    #Format: [quantized time index, velocity, kit piece, microtiming deviation from metronome]

    # BFD KEY MAP - Incomplete
    kickPitch = 24
    hihatClosedPitches = 37, 30, 42, 46
    snarePitches = 26, 29
    crashPitches = 41
    floorTomPitch = 31

    hits = np.zeros([len(midi.instruments[0].notes), 4])
    i = 0
    for instrument in midi.instruments:
        for note in instrument.notes:
            hits[i, 0] = note.start
            hits[i, 1] = note.velocity
            if note.pitch == kickPitch:
                hits[i, 2] = 0
            elif note.pitch in snarePitches:
                hits[i, 2] = 1
            elif note.pitch in hihatClosedPitches:
                hits[i, 2] = 2
            i += 1

    hits[:, 0] = hits[:, 0] / 60.0 * tempo
    hits[:, 1] = hits[:, 1] / 127.0
    multipliedHit = hits[:, 0] * 4.0
    roundedHits = multipliedHit.round(decimals=0) / 4.0
    microtimingVariationBeats = hits[:, 0] - roundedHits
    microtimingVariationMS = microtimingVariationBeats * 60.0 * 1000 / tempo
    hits[:, 0] = roundedHits
    hits[:, 3] = microtimingVariationMS
    return hits

