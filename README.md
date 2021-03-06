# GrooveToolbox

The GrooveToolbox is a Python toolbox for analysis and comparison of symbolic drum loops, calculating rhythm features, microtiming features and similarity metrics, with functionality for plotting and loading loops from various formats.

## Dependencies

Python version: 3.5.x or 2.7.x

Numpy

Pandas

Scipy

Matplotlib

pretty_midi

## example.py
Example script for using the toolbox. Loads a loop from an example MIDI file. Extracts hit and timing information, then calculates all rhythm and microtiming features and prints them on the command line.

## Groove.py
Class containing Groove class with RhythmFeatures and MicrotimingFeatures subclasses. Contains all feature extraction functions for analysing one groove. If extractFeatures = True, automatically calculates all features upon loading the groove. Supports 3 velocity types: None (all velocities = 1), Regular (velocity from 0-1 taken directly from MIDI/BFD Groove file), Transform (velocity scaled with root 5 function to reduce its impact on feature values).

As well as calculating all the features in one go, it is possible to retrieve them individually e.g.:

```
totalDensity = MyGroove.rhythmFeatures.getTotalDensity()
swingRatio = MyGroove.microtimingFeatures.getSwingRatio()
```

## LoadGrooveFromMIDI.py
Load a MIDI drum loop into GrooveToolbox velocity and microtiming arrays. Example usage:
```
from LoadGrooveFromMIDI import *
hitsMatrixMIDI, timingMatrixMIDI, tempo = getGrooveFromMIDIFile("MyLoop.mid", tempo=120, keymap="BFD")
```

## LoadGrooveFromBFDPalette.py
Contains a set of functions for parsing a single BFD groove using some files in the fx folder. Extracts two matricies for each groove, one for velocities at each hit position and another for microtiming deviation at each hit position. Use getGroovesFromBundle to load all grooves within a bundle, or getGrooveFromBFDPalette to get a single groove from within a bundle file.

## PlotGrooveData.py
Plot piano-roll representation of a groove using matplotlib. Usage:
```
from PlotGrooveData import *
plotGrooveMatrix(JB20)
```
### SimilarityMetrics.py
3 similarity metrics for grooves: Hamming distance (velocity weighted), fuzzy Hamming distance and structural rhythm similarity. Usage:
```
from SimilarityMetrics import *
distance = weightedHammingDistance(GrooveA, GrooveB)
```
### Loading From Audio
Using the functions within LoadGrooveFromAudio, it is possible to transcribe audio drum loops to perform analysis upon using the ADTLib open-source library (https://github.com/CarlSouthall/ADTLib). Currently the transcription only works for loops with three parts - kick, snare and hihats. It doesn't differentiate between different sorts of hihat and only works for .wav files.

This library has the following additional depencencies:
madmom
tensorflow
fpdf

For any questions, please feel free to get in touch at fred.bruford@gmail.com

