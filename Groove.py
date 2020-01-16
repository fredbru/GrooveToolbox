# A groove is described here as a short drum loop of arbritary length and polyphony
# #     Vector format:
#     0 Kick
#     1 snare
#     2 Closed Hihat
#     3 Open Hihat
#     4 Ride
#     5 Crash
#     6 Extra cymbal
#     7 Low tom
#     8 Mid tom
#     9 High tom

import numpy as np
# import microtiminganalysis

class Groove():
    def __init__(self, filename):
        np.set_printoptions(precision=2)
        if filename.endswith('.npy'): #todo:build in other input formats here
            self.allParts = np.load(filename)
            try:
                self.timingMatrix = np.load(filename[0:-4] + "-timing.npy") #currently timing matrix has extra column for index
            except:
                print('Need matching timing file for .npy type - named in format GrooveName-timing.npy ')
        elif filename.endswith('.bfd3grv') or filename.endswith('.bfd2pal'):
            print("BFD groove parsing not yet implemented")

        self.groove5Parts = self._groupGroove5KitParts()
        self.groove3Parts = self._groupGroove3KitParts()

        # self.rhythmFeatures = RhythmFeatures() #need to put in matrix data
        # self.timingFeatures = MicrotimingFeatures() # need to put in matrix data
        #
        # self.transformationReduction = np.empty([])
    # todo : build in midi, BFD and audio file loading (plus any other formats)

    def _groupGroove5KitParts(self):
        # Group kit parts into 5 polyphony levels
        # Only works for groove files - not microtiming (less important to group microtiming).
        # 0 - Kick
        # 1 - Snare
        # 2 - Closed cymbals (hihat and ride)
        # 3 - Open cymbals (open hihat, crash and extra cymbal
        # 4 - Toms (low mid and high)

        kick = 0
        snare = 1
        closedhihat = 2
        openhihat = 3
        ride = 4
        crash = 5
        extraCymbal = 6
        lowTom = 7
        midTom = 8
        highTom = 9

        groove5Parts = np.zeros([self.allParts.shape[0],5])
        groove5Parts[:,0] = self.allParts[:,kick]
        groove5Parts[:,1] = np.ceil(self.allParts[:,snare],1)
        groove5Parts[:,2] = np.ceil(self.allParts[:,closedhihat] + self.allParts[:,ride],1)
        groove5Parts[:,3] = np.ceil(self.allParts[:,openhihat] + self.allParts[:,crash] + self.allParts[:,extraCymbal],1)
        groove5Parts[:,4] = np.ceil(self.allParts[:,lowTom] + self.allParts[:,midTom] + self.allParts[:,highTom],1)
        return groove5Parts

    def _groupGroove3KitParts(self):
        kick = self.groove5Parts[:, 0]
        snare = self.groove5Parts[:, 1]
        closed = self.groove5Parts[:, 2]
        open = self.groove5Parts[:, 3]
        toms = self.groove5Parts[:, 4]

        low = kick
        mid = np.nansum(np.dstack((snare, toms)), 2)
        high = np.nansum(np.dstack((closed, open)), 2)

        return np.vstack([low,mid,high])

    def getAllFeatures(self):
        pass

class RhythmFeatures():
    def __init__(self):
        self.weightedSyncopation = []
        self.polyphonicSyncopation = []
        self.lowSyncopation = []
        self.midSyncopation = []
        self.highSyncopation = []
        self.lowDensity = []
        self.midDensity = []
        self.highDensity = []
        self.totalDensity = []
        self.highness = []
        self.highsyncness = []
        self.autocorrelationSkew = []
        self.autocorrelationMaxAmplitude = []
        self.autocorrelationCentroid = []
        self.autocorrelationHarmonicity = []
        self.symmetry = []

    def getAllFeatures(self):
        # get all features. create seperate functions for feature calculations so user
        # can calculate features individually if they would like to.
        pass


class MicrotimingFeatures():
    def __init__(self):
        self.swingness = []
        self.swing = []
        self.pushness = []
        self.laidbackness = []
        self.ontopness = []
        self.averageTimingMatrix = np.empty([])

    def getAllFeatures(self):
        pass
        # get all microtiming features. have separate one for individual features.