# A groove is described here as a short drum loop of arbritary length and polyphony

import numpy as np
import analyse

class Groove():
    def __init__(self,allParts, name, tempo):
        self.name = name
        self.allParts = allParts
        self.timingMatrix = self._getMicrotimingMatrix(self, tempo)
        self.split5Parts = self._splitKitParts5Ways(self)
        self.split3Parts = self._splitKitParts3Ways(self)

        self.rhythmFeatures = RhythmFeatures() #need to put in matrix data
        self.timingFeatures = MicrotimingFeatures() # need to put in matrix data

        self.transformationReduction = np.empty([])

    def _getMicrotimingMatrix(self):
        pass

    def _splitKitParts5Ways(self):
        pass

    def _splitKitParts3Ways(self):
        pass

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
        # get all microtiming features. have separate one for individual features.