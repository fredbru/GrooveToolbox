# 3 Similarity measures for comparing drum patterns: velocity-weighted Hamming distance, fuzzy Hamming distance and
# structural similarity. See paper for more detailed descriptions. Optional beat awareness weighting for Hamming.

import numpy as np
import math

def weightedHammingDistance(grooveA, grooveB, numberOfParts=10, beatWeighting="Off"):
    if numberOfParts == 3:
        a = grooveA.groove3Parts
        b = grooveB.groove3Parts
    elif numberOfParts == 5:
        a = grooveA.groove5Parts
        b = grooveB.groove5Parts
    elif numberOfParts == 10:
        a = grooveA.groove10Parts
        b = grooveB.groove10Parts

    if beatWeighting == "On":
        a = _weightGroove(a)
        b = _weightGroove(b)



    x = (a.flatten()-b.flatten())
    return math.sqrt(np.dot(x, x.T))


def fuzzyHammingDistance(grooveA, grooveB, numberOfParts=10, beatWeighting="Off"):
    # Get fuzzy Hamming distance as velocity weighted Hamming distance, but with 1 metrical distance lookahead/back
    # and microtiming weighting
    #
    if numberOfParts == 3:
        a = grooveA.groove3Parts
        b = grooveB.groove3Parts #TODO: implement timing matrix combination in Groove.py
    elif numberOfParts == 5:
        a = grooveA.groove5Parts
        b = grooveB.groove5Parts
    elif numberOfParts == 10:
        a = grooveA.groove10Parts
        aTiming = grooveA.timingMatrix
        b = grooveB.groove10Parts
        bTiming = grooveB.timingMatrix

    if beatWeighting == "On":
        a = _weightGroove(a)
        b = _weightGroove(b)

    timingDifference = np.nan_to_num(aTiming - bTiming)

    x = np.zeros(a.shape)
    tempo = 120.0
    stepTimeMS = 60.0 * 1000 / tempo / 4 # semiquaver step time in ms


    timingDifferenceWeight = timingDifference / 125.
    timingDifferenceWeight = 1+np.absolute(timingDifferenceWeight)
    singletimingDifferenceWeight = 400

    for j in range(numberOfParts):
        for i in range(31):
            if a[i,j] != 0.0 and b[i,j] != 0.0:
                x[i,j] = (a[i,j] - b[i,j]) * (timingDifferenceWeight[i,j])
            elif a[i,j] != 0.0 and b[i,j] == 0.0:
                if b[(i+1)%32, j] != 0.0 and a[(i+1)%32, j] == 0.0:
                    singletimingDifference = np.nan_to_num(aTiming[i,j]) - np.nan_to_num(bTiming[(i+1)%32,j]) + stepTimeMS
                    if singletimingDifference < 125.:
                        singletimingDifferenceWeight = 1 + abs(singletimingDifferenceWeight/stepTimeMS)
                        x[i,j] = (a[i,j] - b[(i+1)%32,j]) * singletimingDifferenceWeight
                    else:
                        x[i, j] = (a[i, j] - b[i, j]) * timingDifferenceWeight[i, j]

                elif b[(i-1)%32,j] != 0.0 and a[(i-1)%32, j] == 0.0:
                    singletimingDifference =  np.nan_to_num(aTiming[i,j]) - np.nan_to_num(bTiming[(i-1)%32,j]) - stepTimeMS

                    if singletimingDifference > -125.:
                        singletimingDifferenceWeight = 1 + abs(singletimingDifferenceWeight/stepTimeMS)
                        x[i,j] = (a[i,j] - b[(i-1)%32,j]) * singletimingDifferenceWeight
                    else:
                        x[i, j] = (a[i, j] - b[i, j]) * timingDifferenceWeight[i, j]
                else:
                    x[i, j] = (a[i, j] - b[i, j]) * timingDifferenceWeight[i, j]

            elif a[i,j] == 0.0 and b[i,j] != 0.0:
                if b[(i + 1) % 32, j] != 0.0 and a[(i + 1) % 32, j] == 0.0:
                    singletimingDifference =  np.nan_to_num(aTiming[i,j]) - np.nan_to_num(bTiming[(i+1)%32,j]) + stepTimeMS
                    if singletimingDifference < 125.:
                        singletimingDifferenceWeight = 1 + abs(singletimingDifferenceWeight/stepTimeMS)
                        x[i,j] = (a[i,j] - b[(i+1)%32,j]) * singletimingDifferenceWeight
                    else:
                        x[i, j] = (a[i, j] - b[i, j]) * timingDifferenceWeight[i, j]

                elif b[(i-1)%32,j] != 0.0 and a[(i-1)%32, j] == 0.0:
                    singletimingDifference =  np.nan_to_num(aTiming[i,j]) - np.nan_to_num(bTiming[(i-1)%32,j]) - stepTimeMS
                    if singletimingDifference > -125.:
                        singletimingDifferenceWeight = 1 + abs(singletimingDifferenceWeight/stepTimeMS)
                        x[i,j] = (a[i,j] - b[(i-1)%32,j]) * singletimingDifferenceWeight

                    else:
                        x[i, j] = (a[i, j] - b[i, j]) * timingDifferenceWeight[i, j]

                else: # if no nearby onsets, need to count difference between onset and 0 value.
                    x[i, j] = (a[i, j] - b[i, j]) * timingDifferenceWeight[i, j]


        fuzzyDistance = math.sqrt(np.dot(x.flatten(),x.flatten().T))
    return fuzzyDistance
    # go through a, and if hit[i] in b = 0, check hit [i+1] and [i-1]
def structuralSimilarityDistance(grooveA, grooveB):
    # Simialrity calculated between reduced versions of loops, measuring whether onsets occur in
    # roughly similar parts of two loops. Calculated as hamming distance between reduced versions.
    # of grooves
    a = grooveA.getReducedGroove()
    b = grooveB.getReducedGroove()
    rowsToRemove = [1,2,3,5,6,7,9,10,11,13,14,15,17,18,19,21,22,23,25,26,27,29,30,31]
    reducedA = np.delete(a, rowsToRemove, axis=0)
    reducedB = np.delete(b, rowsToRemove, axis=0)
    x = (a.flatten()-b.flatten())
    structuralDifference = math.sqrt(np.dot(x, x.T))
    return structuralDifference


def _weightGroove(self, groove):
    # Awareness profile weighting for hamming/fuzzy distance based on Gomez-Marin metrical profile.
    # The rhythms in each beat of a bar have different significance based on GTTM.
    beatAwarenessWeighting = [1,1,1,1,
                              0.27,0.27,0.27,0.27,
                              0.22,0.22,0.22,0.22,
                              0.16,0.16,0.16,0.16,
                              1,1,1,1,
                              0.27,0.27,0.27,0.27,
                              0.22,0.22,0.22,0.22,
                              0.16,0.16,0.16,0.16,]

    for i in range(groove.shape[1]):
        groove[:,i] = groove[:,i] * beatAwarenessWeighting
    return groove