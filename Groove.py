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

class Groove():
    def __init__(self, filename, extractFeatures=True):
        # Filename - name of groove file to load
        # extractFeatures - if True (default), extract all features upon groove creation.
        # Set false if you don't need all features - instead retrieve as and when you need them

        np.set_printoptions(precision=2)
        self.allParts, self.timingMatrix = self._loadGrooveFile(filename)
        self.groove5Parts = self._groupGroove5KitParts()
        self.groove3Parts = self._groupGroove3KitParts()

        self.rhythmFeatures = RhythmFeatures(self.allParts, self.groove5Parts, self.groove3Parts)
        self.microtimingFeatures = MicrotimingFeatures(self.timingMatrix)

        if extractFeatures:
            self.rhythmFeatures.getAllFeatures()
            self.microtimingFeatures.getAllFeatures()


    def _loadGrooveFile(self, filename):
        # Load groove file from filename. Accept multiple different file types
        # todo : build in midi, BFD and audio file loading (plus any other formats)
        if filename.endswith('.npy'):
            allParts = np.load(filename)
            try:
                timingMatrix = np.load(filename[0:-4] + "-timing.npy") #currently timing matrix has extra column for index
            except:
                print('Need matching timing file for .npy type - named in format GrooveName-timing.npy ')
        elif filename.endswith('.bfd3grv') or filename.endswith('.bfd2pal'):
            print("BFD file input not yet implemented")
        elif filename.endswith('.midi'):
            print("Midi input not yet implemented")

        return allParts, timingMatrix

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
        groove5Parts[:,1] = self.allParts[:,snare]
        groove5Parts[:,2] = np.clip([self.allParts[:,closedhihat] + self.allParts[:,ride]],0,1)
        groove5Parts[:,3] = np.clip([self.allParts[:,openhihat] + self.allParts[:,crash] + self.allParts[:,extraCymbal]],0,1)
        groove5Parts[:,4] = np.clip([self.allParts[:,lowTom] + self.allParts[:,midTom] + self.allParts[:,highTom]],0,1)
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

    def calculateAllFeatures(self):
        pass

class RhythmFeatures():
    def __init__(self, allParts, groove5Parts, groove3Parts):
        self.allParts = allParts
        self.groove5Parts = groove5Parts
        self.groove3Parts = groove3Parts

    def getAllFeatures(self):
        # get all features. create separate functions for feature calculations so user
        # can calculate features individually if they would like to.
        self.getWeightedSyncopation()
        self.getPolyphonicSyncopation()
        self.getLowSyncopation()
        self.getMidSyncopation()
        self.getHighSyncopation()
        self.getLowDensity()
        self.getMidDensity()
        self.getHighDensity()
        self.getTotalDensity()
        self.getHiness()
        self.getHiSyncness()
        self.getAutocorrelationSkew()
        self.getAutocorrelationMaxAmplitude()
        self.getAutocorrelationCentroid()
        self.getAutocorrelationHarmonicity()
        self.getSymmetry()
        print('get features')

    def getWeightedSyncopation(self):
        pass

    def getPolyphonicSyncopation(self):
        pass

    def getSyncopation1Part(self):
        pass

    def getLowSyncopation(self):
        pass

    def getMidSyncopation(self):
        pass

    def getHighSyncopation(self):
        pass

    def getDensity1Part(self):
        pass

    def getLowDensity(self):
        pass

    def getMidDensity(self):
        pass

    def getHighDensity(self):
        pass

    def getDensity1Part(self):
        pass

    def getTotalDensity(self):
        pass

    def getHiness(self):
        pass

    def getHiSyncness(self):
        pass

    def getAutocorrelationSkew(self):
        pass

    def getAutocorrelationMaxAmplitude(self):
        pass

    def getAutocorrelationCentroid(self):
        pass

    def getAutocorrelationHarmonicity(self):
        pass

    def getSymmetry(self):
        pass

class MicrotimingFeatures():
    def __init__(self, timingMatrix):
        self.swingness = []
        self.swing = []
        self.pushness = []
        self.laidbackness = []
        self.ontopness = []
        self.averageTimingMatrix = np.empty([])

    def getAllFeatures(self):
        pass
        # get all microtiming features. have separate one for individual features.