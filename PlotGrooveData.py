#todo: autocorrelation plot?
#todo: plot of reduced form of groove as well as unreduced.
#todo: microtiming deviation stats plot
#todo: correlation/similarity plots between loops or features?

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.ticker as mticker


def plotGrooveMatrix(groove, numberOfParts=10, reduced=False):

    if reduced == True:
        grooveMatrix = groove.getReducedGroove()
    else:
        grooveMatrix = groove.groove10Parts

    plt.close()
    plt.figure()
    plt.grid(which="both")
    plt.title(groove.name)
    yLabels = ["Kick", "Snare", "Closed Hihat", "Open Hihat", "Ride", "Crash",
               "Extra Cymbal", "Low Tom", "Mid Tom", "High Tom"]
    xLabelsMinor = ["","","","", "2","","","", "3","","","","4","","","","","","","","2","","","","3","","","",
                    "4","","","","","","","","2"]

    for i in range(grooveMatrix.shape[0]):
        for j in range(grooveMatrix.shape[1]):
            if grooveMatrix[i,j] != 0.:
                plt.scatter((i)/4.,j, marker='d', color='k', s=30)
    plt.gca().yaxis.set_major_locator(mticker.MultipleLocator(1))
    plt.gca().xaxis.set_minor_locator(mticker.MultipleLocator(0.25))

    plt.gca().set_ylim([-0.5,10])
    plt.yticks([0,1,2,3,4,5,6,7,8,9], yLabels)
    tickPoints = np.linspace(0,9,37)
    plt.gca().set_xticks(tickPoints, minor=True)
    plt.gca().set_xticklabels(xLabelsMinor, minor=True, fontdict={'color':"gray"})

    plt.gca().set_xticks([0,4,8], minor=False)
    plt.gca().set_xticklabels(["1","2","3"], minor=False,fontdict={'fontsize':20})

    plt.hold()
    plt.show()

def plotMicrotimingDeviation(groove, instrument):
    pass

#todo: plot reduced groove?
#todo: for some reason this doesn't work when I try to use it twice?