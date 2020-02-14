import numpy as np
import math

def weightedHammingDistance(grooveA, grooveB, numberOfParts=10):
    if numberOfParts == 3:
        a = grooveA.groove3Parts
        b = grooveB.groove3Parts
    elif numberOfParts == 5:
        a = grooveA.groove5Parts
        b = grooveB.groove5Parts
    elif numberOfParts == 10:
        a = grooveA.groove10Parts
        b = grooveB.groove10Parts

    x = (a.flatten()-b.flatten())
    return math.sqrt(np.dot(x, x.T))

def getFlexibleEuclideanDistance(grooveA, grooveB, numberOfParts=10):
    # get euclidean distance, but with 1 metrical distance lookahead/back
    # 1st thing - recreate euclidean distance with iteration (not array-wise calculation)
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

    timingDifference = np.nan_to_num(aTiming - bTiming)

    x = np.zeros(a.shape)
    tempo = 120.0
    stepTimeMS = 60.0 * 1000 / tempo / 4 # semiquaver step time in ms


    timingDifferenceWeight = timingDifference / 125.
    timingDifferenceWeight = 1+np.absolute(timingDifferenceWeight)
    singletimingDifferenceWeight = 0

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


        flexDistance = math.sqrt(np.dot(x.flatten(),x.flatten().T))
    return flexDistance
    # go through a, and if hit[i] in b = 0, check hit [i+1] and [i-1]
