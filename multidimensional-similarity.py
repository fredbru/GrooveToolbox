import numpy as np
import csv
from LoadGrooveFromBFDPalette import *
from LoadGrooveFromMIDI import *
from Groove import *
from matplotlib import pyplot as plt

# load all of my BFD grooves from .csv into Groove objects
# 2 lists of groove objects (a and b)

namesA = []
namesB = []
palettesA = []
palettesB = []
groovesA = []
groovesB = []
differenceMatrix = []
i = 0

# with open('eval-pairings-palettes.csv') as csvfile:
#     reader = csv.reader(csvfile, delimiter=",")
#     for row in reader:
#         if i < 1000:
#             namesA.append(row[0])
#             palettesA.append(row[1]+".bfd3pal")
#             hitsMatrixA, timingMatrixA, tempoA = getGrooveFromBFDPalette(palettesA[i], namesA[i])
#             groovesA.append(NewGroove(hitsMatrixA, timingMatrixA, tempoA,
#                                       velocityType="Transform", extractFeatures=True, name=namesA[i]))
#             allFeaturesA = np.hstack([groovesA[i].rhythmFeatures.getAllFeatures(),
#                                      groovesA[i].microtimingFeatures.getAllFeatures()])
#
#             namesB.append(row[2])
#             palettesB.append(row[3]+".bfd3pal")
#             hitsMatrixB, timingMatrixB, tempoB = getGrooveFromBFDPalette(palettesB[i], namesB[i])
#             groovesB.append(NewGroove(hitsMatrixB, timingMatrixB, tempoB,
#                                       velocityType="Transform", extractFeatures=True,name=namesB[i]))
#             allFeaturesB = np.hstack([groovesB[i].rhythmFeatures.getAllFeatures(),
#                                      groovesB[i].microtimingFeatures.getAllFeatures()])
#
#             differenceMatrix.append(allFeaturesA-allFeaturesB) # 20 features total
#             print(groovesA[i].name,groovesB[i].name)
#             print(differenceMatrix[i][15:20])
#         i+=1
#
# np.save("difference matrix.npy", differenceMatrix)
np.set_printoptions(threshold=np.nan)
similarityRatings = np.zeros([80])
i = 0
with open('similarity-ratings.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for row in reader:
        similarityRatings[i] = float(row[0])
        i+=1

differenceMatrix = np.load("difference matrix.npy")
normalizedDifference = np.zeros([80,20])
differenceArray = np.zeros([80,20])
for i in range(80):
    differenceArray[i,:] = differenceMatrix[i]

for i in range(20):
    x = differenceArray[:,i]
    normalized_feature = (x - x.min(0)) / x.ptp(0)
    normalizedDifference[:,i] = normalized_feature


plt.figure()
color=iter(plt.cm.rainbow(np.linspace(0,2,40)))
for i in [1,2,3,4]:
    c=next(color)
    plt.scatter(normalizedDifference[:,i], similarityRatings,c=c)
plt.show()