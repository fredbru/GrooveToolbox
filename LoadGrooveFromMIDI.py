import numpy as np
import pretty_midi

def getGrooveFromMIDIFile(filename, tempo=None, keymap="GM"):
    # Extract a groove from a MIDI file
    midi = pretty_midi.PrettyMIDI(filename)
    if tempo == None:
        tempo = midi.estimate_tempo() #todo: tempo estimation seems to fail a lot

    keymap = _setMIDIKeyMap(keymap)
    hits = _getAllHitInfo(midi, tempo, keymap)

    hitsMatrix = np.zeros([32, 10])  # todo: work with loops of arbritrary length
    timingMatrix = np.zeros([32, 10])
    timingMatrix[:] = np.nan

    for j in range(hits.shape[0]):
        timePosition = int(hits[j, 0] * 4)
        kitPiecePosition = int(hits[j, 2])
        timingMatrix[timePosition % 32, kitPiecePosition] = hits[j, 3]
        hitsMatrix[timePosition % 32, kitPiecePosition] = hits[j, 1]
    return hitsMatrix, timingMatrix, tempo

def _getAllHitInfo(midi, tempo, keymap):
    # Create an array of all hits in a groove
    #Format: [quantized time index, velocity, kit piece, microtiming deviation from metronome]

    hits = np.zeros([len(midi.instruments[0].notes), 4])
    i = 0
    for instrument in midi.instruments:
        for note in instrument.notes:
            hits[i, 0] = note.start
            hits[i, 1] = note.velocity
            if note.pitch in keymap["kick"]:
                hits[i, 2] = 0
            elif note.pitch in keymap["snare"]:
                hits[i, 2] = 1
            elif note.pitch in keymap["closed hihat"]:
                hits[i, 2] = 2
            elif note.pitch in keymap["open hihat"]:
                hits[i,2] = 3
            elif note.pitch in keymap["ride"]:
                hits[i,2] = 4
            elif note.pitch in keymap["crash"]:
                hits[i,2] = 5
            elif note.pitch in keymap["extra cymbal"]:
                hits[i,2] = 6
            elif note.pitch in keymap["low tom"]:
                hits[i,2] = 7
            elif note.pitch in keymap["mid tom"]:
                hits[i,2] = 8
            elif note.pitch in keymap["high tom"]:
                hits[i,2] = 9
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

def _setMIDIKeyMap(keymap):
    #todo: how to deal with custom keymaps?
    # Set key map to be used for MIDI transcription. Only deals with 10 core drum kit parts - kick, snare, closed/pedal hihat,
    # open hihat, ride, crash, extra cymbal (any other cymbal e.g. china, splash), low tom, mid tom, high tom. All other
    # percussion is ignored
    # See here for a link to General MIDI key map to see exactly which instruments are mapped where:
    # https://musescore.org/sites/musescore.org/files/General%20MIDI%20Standard%20Percussion%20Set%20Key%20Map.pdf

    BFDKeymap = {"kick":[24,84], "snare":[25,26,27,28,29,86,88],"closed hihat":[30,32,37,42,44,46,49,51,54,58],
                 "open hihat":[34,39,56],"ride":[50,60,71,81,87],"crash":[41,43,52,53,62,64,72,74,75,78],
                 "extra cymbal":[45,47,48,55,57,59,65,67,69,76,77,79,80,82,85],"low tom":[31,33,61,63,89,90],
                 "mid tom":[35,36,66,68,91,92], "high tom":[38,40,70,73,93,94]}

    GMKeymap = {"kick":[35,36], "snare":[37, 38, 40],"closed hihat":[42,44],"open hihat":[46],"ride":[51,53,59],
                "crash":[49,57],"extra cymbal":[52,55], "low tom":[41,43,45], "mid tom":[47,48], "high tom":[50]}

    if keymap == "BFD":
        keymap = BFDKeymap
    if keymap == "GM":
        keymap = GMKeymap

    return keymap
