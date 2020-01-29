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
    def __init__(self, filename, extractFeatures=True, velocityType="Regular"):
        # Filename - name of groove file to load
        # extractFeatures - if True (default), extract all features upon groove creation.
        # Set false if you don't need all features - instead retrieve as and when you need them

        np.set_printoptions(precision=2)
        self.groove10Parts, self.timingMatrix = self._loadGrooveFile(filename)
        tempo = 120.0 #todo: fix how to deal with tempo

        if velocityType == "None":
            self.groove10Parts = np.ceil(self.groove10Parts)
        if velocityType == "Regular":
            pass
        if velocityType == "Transform":
            self.groove10Parts = np.power(self.groove10Parts, 0.2)

        self.groove5Parts = self._groupGroove5KitParts()
        self.groove3Parts = self._groupGroove3KitParts()

        self.rhythmFeatures = RhythmFeatures(self.groove10Parts, self.groove5Parts, self.groove3Parts)
        #self.microtimingFeatures = MicrotimingFeatures(self.timingMatrix, tempo)

        if extractFeatures:
            self.rhythmFeatures.getAllFeatures()
            #self.microtimingFeatures.getAllFeatures() #todo: microtiming stuff

    def _loadGrooveFile(self, filename):
        # Load groove file from filename. Accept multiple different file types
        # todo : build in midi, BFD and audio file loading (plus any other formats)
        if filename.endswith('.npy'):
            groove10Parts = np.load(filename)
            try:
                timingMatrix = np.load(filename[0:-4] + "-timing.npy") #currently timing matrix has extra column for index
            except:
                print('Need matching timing file for .npy type - named in format GrooveName-timing.npy ')
        elif filename.endswith('.bfd3grv') or filename.endswith('.bfd2pal'):
            print("BFD file input not yet implemented")
        elif filename.endswith('.midi'):
            print("Midi input not yet implemented")
        return groove10Parts, timingMatrix

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

        groove5Parts = np.zeros([self.groove10Parts.shape[0],5])
        groove5Parts[:,0] = self.groove10Parts[:,kick]
        groove5Parts[:,1] = self.groove10Parts[:,snare]
        groove5Parts[:,2] = np.clip([self.groove10Parts[:,closedhihat] + self.groove10Parts[:,ride]],0,1)
        groove5Parts[:,3] = np.clip([self.groove10Parts[:,openhihat] + self.groove10Parts[:,crash] + self.groove10Parts[:,extraCymbal]],0,1)
        groove5Parts[:,4] = np.clip([self.groove10Parts[:,lowTom] + self.groove10Parts[:,midTom] + self.groove10Parts[:,highTom]],0,1)
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

class RhythmFeatures():
    def __init__(self, groove10Parts, groove5Parts, groove3Parts):
        self.groove10Parts = groove10Parts
        self.groove5Parts = groove5Parts
        self.groove3Parts = groove3Parts

        #todo: Do I want to list names of class variables in here? So user can see them easily?

    def getAllFeatures(self):
        # get all standard features. create separate functions for feature calculations so user
        # can calculate features individually if they would like to.

        self.getCombinedSyncopation()
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

    def getCombinedSyncopation(self):
        # Calculate syncopation as summed across two parts.
        self.combinedSyncopation = 0.0
        for i in range(self.groove10Parts.shape[1]):
            self.combinedSyncopation += self.getSyncopation1Part(self.groove10Parts[:,i])
        return self.combinedSyncopation



    def getPolyphonicSyncopation(self):
        pass

    def getSyncopation1Part(self, part):
        # Using Longuet-Higgins  and  Lee 1984 metric profile.
        # Uses velocity if available
        # Assuming it's a drum loop - loops round.
        # syncopation = difference in profile weights where proceeding weight > preceeding
        metricalProfile = [5, 1, 2, 1, 3, 1, 2, 1, 4, 1, 2, 1, 3, 1, 2, 1,
                                   5, 1, 2, 1, 3, 1, 2, 1, 4, 1, 2, 1, 3, 1, 2, 1]

        syncopation = 0.0
        for i in range(len(part)):
            if part[i] != 0:
                if part[(i + 1) % 32] == 0.0 and metricalProfile[i+1] > metricalProfile[i]:
                    syncopation = float(syncopation + (
                    abs(metricalProfile[i+1] - metricalProfile[i]))) # * part[i]))

                elif part[(i + 2) % 32] == 0.0 and metricalProfile[i+2] > metricalProfile[i]:
                    syncopation = float(syncopation + (
                    abs(metricalProfile[i+2] - metricalProfile[i]))) # * part[i]))
        return syncopation

    def getLowSyncopation(self):
        self.lowSyncopation = self.getSyncopation1Part(self.groove10Parts[:,0])
        return self.lowSyncopation

    def getMidSyncopation(self):
        # sum parts here
        midParts = np.clip(self.groove10Parts[:,1] + self.groove10Parts[:,7] + self.groove10Parts[:,8] +
                             self.groove10Parts[:,9],0,1)
        self.midSyncopation = self.getSyncopation1Part(midParts)
        return self.midSyncopation

    def getHighSyncopation(self):
        # sum parts here
        highParts = np.clip(self.groove10Parts[:,2] + self.groove10Parts[:,3] + self.groove10Parts[:,4] +
                            self.groove10Parts[:, 5] + self.groove10Parts[:,6],0,1)
        self.highSyncopation = self.getSyncopation1Part(highParts)
        return self.highSyncopation

    def getDensity(self, part):
        # Get density of any single kit part or part group. Main difference to total density is that you divide by
        # number of metrical steps, instead of total number of possible onsets in the pattern
        numSteps = part.shape[0]
        numOnsets = np.count_nonzero(np.ceil(part) == 1)
        averageVelocity = part[part!=0.0].mean()

        if np.isnan(averageVelocity):
            averageVelocity = 0.0
        density = averageVelocity * float(numOnsets) / float(numSteps)
        return density

    def getLowDensity(self):
        self.lowDensity = self.getDensity(self.groove10Parts[:,0])
        return self.lowDensity

    def getMidDensity(self):
        midParts = np.vstack([self.groove10Parts[:,1], self.groove10Parts[:,7], self.groove10Parts[:,8],
                             self.groove10Parts[:,9]])
        self.midDensity = self.getDensity(midParts)
        return self.midDensity

    def getHighDensity(self):
        highParts = np.vstack([self.groove10Parts[:,2], self.groove10Parts[:,3], self.groove10Parts[:,4],
                             self.groove10Parts[:,5],self.groove10Parts[:,6]])

        self.highDensity = self.getDensity(self.groove10Parts[:,2])
        return self.highDensity

    def getTotalDensity(self):
        # for 10 parts. Note values do tend to be very low for this, due to high numbers of parts meaning sparse
        # matricies.
        numStepsTotal = self.groove10Parts.size
        numOnsets = np.count_nonzero(np.ceil(self.groove10Parts) == 1)
        averageVelocity = self.groove10Parts[self.groove10Parts!=0.0].mean()
        self.totalDensity = averageVelocity * float(numOnsets) / float(numStepsTotal)
        return self.totalDensity

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
    def __init__(self, microtimingMatrix, tempo):
        self.microtimingMatrix = microtimingMatrix
        self.tempo = tempo
        self.getSwingInfo()

    def getAllFeatures(self):
        # get all microtiming features. have separate one for individual features.

        self.isSwung = self.checkIfSwung()
        self.swingRatio = []
        self.pushness = []
        self.laidbackness = []
        self.ontopness = []
        self.averageTimingMatrix = np.empty([])

    def checkIfSwung(self):

        if self.swingness > 0.0:
            self.isSwung = True
        elif self.swingness == 0.0:
            self.isSwung = False

        return self.isSwung

    def getSwingRatio(self):
        pass

    def getSwingInfo(self):
        print(self.microtimingMatrix.shape[0])


        self.swungNotePositions = list(range(self.microtimingMatrix.shape[0]))[3::4]
        timingAverage = self.getAverageTiming()

        swingCount = 0.0
        secondQuaverLengths = np.zeros[self.microtimingMatrix.shape[0]/4]
        semiquaverStepLength = 60.0 / self.tempo / 4.0

        j = 0
        for i in self.swungNotePositions:
            if timingAverage[i] < -25.0:
                swingCount +=1
                secondQuaverLengths[j] = semiquaverStepLength - timingAverage[i]
            j+=1
        shortQuaverAverageLength = np.mean(secondQuaverLengths[secondQuaverLengths!=0])

        longQuaverAverageLength = (semiquaverStepLength*4.0) - shortQuaverAverageLength
        self.swingRatio = longQuaverAverageLength / shortQuaverAverageLength
        if np.isnan(self.swingRatio):
            self.swingRatio = 1
        self.swingness = swingCount / len(self.swungNotePositions)
        return

    def getPushness(self):
        pass

    def getLaidbackness(self):
        pass

    def getOntopness(self):
        pass

    def getAverageTiming(self):
        self.timingAverage = np.sum(np.nan_to_num(self.microtimingMatrix), axis=1)
        self.timingAverage[self.timingAverage == 0] = ['nan']
        return self.timingAverage














