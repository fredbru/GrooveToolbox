import numpy as np
import csv
from LoadGrooveFromBFDPalette import *
from LoadGrooveFromMIDI import *
from Groove import *
from matplotlib import pyplot as plt

''' Order of features: 21 in total.
0 Combined syncopation
1 Poly syncopation
2 Low sync
3 Mid sync
4 High Sync
5 Low D
6 Mid D
7 High D
8 Total D
9 Hiness
10 Hisyncness
11 Autocorrelation Skew
12 Autocorrelation Max Amplitude
13 Autocorrelation Centroid
14 Autocorrelation Harmonicity
15 Total Symmetry
16 Swingness
17 Swing Ratio
18 Laidbackness
19 Ontopness
20 Pushness'''
namesA = []
namesB = []
palettesA = []
palettesB = []
groovesA = []
groovesB = []
differenceMatrix = []
i = 0

with open('eval-pairings-palettes.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for row in reader:
        if i < 1000:
            namesA.append(row[0])
            palettesA.append(row[1]+".bfd3pal")
            hitsMatrixA, timingMatrixA, tempoA = getGrooveFromBFDPalette(palettesA[i], namesA[i])
            groovesA.append(NewGroove(hitsMatrixA, timingMatrixA, tempoA,
                                      velocityType="Transform", extractFeatures=True, name=namesA[i]))
            allFeaturesA = np.hstack([groovesA[i].rhythmFeatures.getAllFeatures(),
                                     groovesA[i].microtimingFeatures.getAllFeatures()])

            namesB.append(row[2])
            palettesB.append(row[3]+".bfd3pal")
            hitsMatrixB, timingMatrixB, tempoB = getGrooveFromBFDPalette(palettesB[i], namesB[i])
            groovesB.append(NewGroove(hitsMatrixB, timingMatrixB, tempoB,
                                      velocityType="Transform", extractFeatures=True,name=namesB[i]))
            allFeaturesB = np.hstack([groovesB[i].rhythmFeatures.getAllFeatures(),
                                     groovesB[i].microtimingFeatures.getAllFeatures()])

            differenceMatrix.append(np.abs(allFeaturesA-allFeaturesB)) # 20 features total
            print(groovesA[i].name,groovesB[i].name)
            print(differenceMatrix[i][15:20])
        i+=1

np.save("difference matrix.npy", differenceMatrix)
