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
from pandas import Series
from pandas.plotting import autocorrelation_plot
import matplotlib.pyplot as plt
from scipy import stats

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

        #self.rhythmFeatures = RhythmFeatures(self.groove10Parts, self.groove5Parts, self.groove3Parts)
        self.microtimingFeatures = MicrotimingFeatures(self.timingMatrix, tempo)

        if extractFeatures:
            #self.rhythmFeatures.getAllFeatures()
            self.microtimingFeatures.getAllFeatures() #todo: microtiming stuff

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

    def _groupGroove3KitParts(self): #todo: check this is working correctly for toms (same with 5 part function)
        kick = self.groove5Parts[:, 0]
        snare = self.groove5Parts[:, 1]
        closed = self.groove5Parts[:, 2]
        open = self.groove5Parts[:, 3]
        toms = self.groove5Parts[:, 4]

        low = kick
        mid = np.nansum(np.dstack((snare, toms)), 2)
        high = np.nansum(np.dstack((closed, open)), 2)

        return np.vstack([low,mid[0,:],high[0,:]]).T

class RhythmFeatures():
    def __init__(self, groove10Parts, groove5Parts, groove3Parts):
        self.groove10Parts = groove10Parts
        self.groove5Parts = groove5Parts
        self.groove3Parts = groove3Parts
        self.totalAutocorrelationCurve =  self.getTotalAutocorrelationCurve()

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
        self.getTotalSymmetry()

    def getCombinedSyncopation(self):
        # Calculate syncopation as summed across all kit parts.
        self.combinedSyncopation = 0.0
        for i in range(self.groove10Parts.shape[1]):
            self.combinedSyncopation += self.getSyncopation1Part(self.groove10Parts[:,i])
        return self.combinedSyncopation

    def getPolyphonicSyncopation(self):
        # Calculate syncopation using Witek combined drum pattern syncopation distance
        # Only look semiquaver and quaver steps ahead.

        salienceProfile = [0, -3, -2, -3, -1, -3, -2, -3, -1, -3, -2, -3, -1, -3, -2, -3,
                           0, -3, -2, -3, -1, -3, -2, -3, -1, -3, -2, -3, -1, -3, -2, -3]

        low = self.groove3Parts[:,0]
        mid = self.groove3Parts[:,1]
        high = self.groove3Parts[:,2]

        totalSyncopation = 0

        for i in range(len(low)):
            kickSync = self._getKickSync(low, mid, high, i, salienceProfile)
            snareSync = self._getSnareSync(low, mid, high, i, salienceProfile)
            totalSyncopation += kickSync * low[i]
            totalSyncopation += snareSync * mid[i]

        return totalSyncopation

    def _getKickSync(self, low, mid, high, i, salienceProfile):
        # find instances  when kick syncopates against hi hat/snare on the beat. looking for kick proceeded by another hit
        # on a weaker metrical position
        kickSync = 0
        k = 0
        nextHit = ""
        if low[i] == 1 and low[(i + 1) % 32] !=1 and low[(i+2) % 32] != 1:
            for j in i + 1, i + 2: #look one and two steps ahead only - account for semiquaver and quaver sync
                if mid[(j % 32)] == 1 and high[(j % 32)] != 1:
                    nextHit = "Mid"
                    k = j % 32
                    break
                elif high[(j % 32)] == 1 and mid[(j % 32)] != 1:
                    nextHit = "High"
                    k = j % 32
                    break
                elif high[(j % 32)] == 1 and mid[(j % 32)] == 1:
                    nextHit = "MidAndHigh"
                    k = j % 32
                    break
                # if both next two are 0 - next hit == rest. get level of the higher level rest
            if mid[(i+1)%32] + mid[(i+2)%32] == 0.0 and high[(i+1)%32] + [(i+2)%32] == 0.0:
                nextHit = "None"

            if nextHit == "MidAndHigh":
                if salienceProfile[k] >= salienceProfile[i]:  # if hi hat is on a stronger beat - syncopation
                    difference = salienceProfile[k] - salienceProfile[i]
                    kickSync = difference + 2
            elif nextHit == "Mid":
                if salienceProfile[k] >= salienceProfile[i]:  # if hi hat is on a stronger beat - syncopation
                    difference = salienceProfile[k] - salienceProfile[i]
                    kickSync = difference + 2
            elif nextHit == "High":
                if salienceProfile[k] >= salienceProfile[i]:
                    difference = salienceProfile[k] - salienceProfile[i]
                    kickSync = difference + 5
            elif nextHit == "None":
                if salienceProfile[k] > salienceProfile[i]:
                    difference = max(salienceProfile[(i + 1) % 32], salienceProfile[(i + 2) % 32]) - salienceProfile[i]
                    kickSync = difference + 6 # if rest on a stronger beat - one stream sync, high sync valuef
        return kickSync

    def _getSnareSync(self, low, mid, high, i, salienceProfile):
        # find instances  when snare syncopates against hi hat/kick on the beat
        # S = n - ndi + I
        snareSync = 0
        nextHit = ""
        k = 0
        if mid[i] == 1 and mid[(i + 1) % 32] !=1 and mid[(i+2) % 32] != 1:
            for j in i + 1, i + 2: #look one and 2 steps ahead only
                if low[(j % 32)] == 1 and high[(j % 32)] != 1:
                    nextHit = "Low"
                    k = j % 32
                    break
                elif high[(j % 32)] == 1 and low[(j % 32)] != 1:
                    nextHit = "High"
                    k = j % 32
                    break
                elif high[(j % 32)] == 1 and low[(j % 32)] == 1:
                    nextHit = "LowAndHigh"
                    k = j % 32
                    break
            if low[(i+1)%32] + low[(i+2)%32] == 0.0 and high[(i+1)%32] + [(i+2)%32] == 0.0:
                nextHit = "None"

            if nextHit == "LowAndHigh":
                if salienceProfile[k] >= salienceProfile[i]:
                    difference = salienceProfile[k] - salienceProfile[i]
                    snareSync = difference + 1  # may need to make this back to 1?)
            elif nextHit == "Low":
                if salienceProfile[k] >= salienceProfile[i]:
                    difference = salienceProfile[k] - salienceProfile[i]
                    snareSync = difference + 1
            elif nextHit == "High":
                if salienceProfile[k] >= salienceProfile[i]:  # if hi hat is on a stronger beat - syncopation
                    difference = salienceProfile[k] - salienceProfile[i]
                    snareSync = difference + 5
            elif nextHit == "None":
                if salienceProfile[k] > salienceProfile[i]:
                    difference = max(salienceProfile[(i + 1) % 32], salienceProfile[(i + 2) % 32]) - salienceProfile[i]
                    snareSync = difference + 6 # if rest on a stronger beat - one stream sync, high sync value
        return snareSync

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
                if part[(i + 1) % 32] == 0.0 and metricalProfile[(i + 1) % 32] > metricalProfile[i]:
                    syncopation = float(syncopation + (
                    abs(metricalProfile[(i + 1) % 32] - metricalProfile[i]))) # * part[i]))

                elif part[(i + 2) % 32] == 0.0 and metricalProfile[(i + 2) % 32] > metricalProfile[i]:
                    syncopation = float(syncopation + (
                    abs(metricalProfile[(i + 2) % 32] - metricalProfile[i]))) # * part[i]))
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

    def _getAutocorrelationCurve(self, part):
        plt.figure()
        ax = autocorrelation_plot(part)
        autocorrelation = ax.lines[5].get_data()[1]
        plt.plot(range(1, self.groove10Parts.shape[0]+1),
                 autocorrelation)  # plots from 1 to 32 inclusive - autocorrelation starts from 1 not 0 - 1-32
        # plt.show()
        plt.cla()
        plt.clf()
        plt.close()
        return np.nan_to_num(autocorrelation)

    def getTotalAutocorrelationCurve(self):
        # Get autocorrelation curve for all parts summed.
        self.totalAutocorrelationCurve = 0.0
        for i in range(self.groove10Parts.shape[1]):
            self.totalAutocorrelationCurve += self._getAutocorrelationCurve(self.groove10Parts[:,i])
        ax = autocorrelation_plot(self.totalAutocorrelationCurve)
        plt.plot(range(1,33),self.totalAutocorrelationCurve)
        return self.totalAutocorrelationCurve

    def getAutocorrelationSkew(self):
        self.autocorrelationSkew = stats.skew(self.totalAutocorrelationCurve)
        return self.autocorrelationSkew

    def getAutocorrelationMaxAmplitude(self):
        self.autocorrelationMaxAmplitude = self.totalAutocorrelationCurve.max()
        return self.autocorrelationMaxAmplitude

    def getAutocorrelationCentroid(self):
        pass

    def getAutocorrelationHarmonicity(self):
        pass

    def _getSymmetry(self, part):
        # Calculate symmetry for any number of parts.
        # Defined as the the number of onsets that appear in the same positions in the first and second halves
        # of the pattern, divided by the total number of onsets in the pattern. As perfectly symmetricl pattner
        # would have a symmetry of 1.0
        symmetryCount = 0.0
        part1,part2 = np.split(part,2)
        for i in range(part1.shape[0]):
            for j in range(part1.shape[1]):
                if part1[i,j] != 0.0 and part2[i,j] != 0.0:
                    symmetryCount += (1.0 - abs(part1[i,j] - part2[i,j])) # symmetry is
        symmetry = symmetryCount*2.0 / np.count_nonzero(part)
        return symmetry

    def getTotalSymmetry(self):
        self.totalSymmetry = self._getSymmetry(self.groove10Parts)
        return self.totalSymmetry

class MicrotimingFeatures():
    def __init__(self, microtimingMatrix, tempo):
        self.microtimingMatrix = microtimingMatrix

        self.tempo = tempo
        self.averageTimingMatrix = self.getAverageTimingDeviation()
        self._getSwingInfo()


    def getAllFeatures(self):
        # get all microtiming features. have separate one for individual features.
        # need to decide how to deal with this when most of the features are calculated automatically

        self.isSwung = self.checkIfSwung()
        self._getMicrotimingEventProfile1Bar()
        # self.swingRatio = []
        # self.pushness = []
        # self.laidbackness = []
        # self.ontopness = []

    def checkIfSwung(self):

        if self.swingness > 0.0:
            self.isSwung = True
        elif self.swingness == 0.0:
            self.isSwung = False

        return self.isSwung

    def getSwingRatio(self):
        return self.swingRatio

    def getSwingness(self):
        return self.swingness

    def _getSwingInfo(self):
        swungNotePositions = list(range(self.averageTimingMatrix.shape[0]))[3::4]

        swingCount = 0.0
        secondQuaverLengths = np.zeros([self.averageTimingMatrix.shape[0]/4])
        semiquaverStepLength = 60.0 / self.tempo / 4.0

        j = 0
        for i in swungNotePositions:
            if self.averageTimingMatrix[i] < -25.0:
                swingCount +=1
                secondQuaverLengths[j] = semiquaverStepLength - self.averageTimingMatrix[i]
            j+=1

        if np.count_nonzero(secondQuaverLengths) == 0:
            shortQuaverAverageLength = semiquaverStepLength * 2.0
        else:
            shortQuaverAverageLength = np.mean(secondQuaverLengths[secondQuaverLengths != 0])

        longQuaverAverageLength = (semiquaverStepLength*4.0) - shortQuaverAverageLength
        self.swingRatio = longQuaverAverageLength / shortQuaverAverageLength
        if np.isnan(self.swingRatio):
            self.swingRatio = 1
        self.swingness = swingCount / len(swungNotePositions)

    def _getMicrotimingEventProfile1Bar(self):
        # Get profile of timing events for use in pushness/laidbackness/ontopness features
        microtimingToGridProfile = np.zeros([8])
        microtimingToCymbalProfile = np.zeros([8])
        threshold = 15.0
        kickTiming1 = self.microtimingMatrix[0, 0]
        hihatTiming1 = self.microtimingMatrix[0, 2]
        snareTiming2 = self.microtimingMatrix[4, 1]
        hihatTiming2 = self.microtimingMatrix[4, 2]
        kickTiming3 = self.microtimingMatrix[8, 0]
        hihatTiming3 = self.microtimingMatrix[8, 2]
        snareTiming4 = self.microtimingMatrix[12, 1]
        hihatTiming4 = self.microtimingMatrix[12, 2]

        if kickTiming1 > threshold or hihatTiming1 > threshold:
            microtimingToGridProfile[0] = 1
        if kickTiming1 < -threshold or hihatTiming1 < -threshold:
            microtimingToGridProfile[1] = 1
        if snareTiming2 > threshold or hihatTiming2 > threshold:
            microtimingToGridProfile[2] = 1
        if snareTiming2 < -threshold or hihatTiming2 < -threshold:
            microtimingToGridProfile[3] = 1

        if kickTiming3 > threshold or hihatTiming3 > threshold:
            microtimingToGridProfile[4] = 1
        if kickTiming3 < -threshold or hihatTiming3 < -threshold:
            microtimingToGridProfile[5] = 1
        if snareTiming4 > threshold or hihatTiming4 > threshold:
            microtimingToGridProfile[6] = 1
        if snareTiming4 < -threshold or hihatTiming4 < -threshold:
            microtimingToGridProfile[7] = 1

        if kickTiming1 > hihatTiming1 + threshold:
            microtimingToCymbalProfile[0] = 1
        if kickTiming1 < hihatTiming1 - threshold:
            microtimingToCymbalProfile[1] = 1
        if snareTiming2 > hihatTiming2 + threshold:
            microtimingToCymbalProfile[2] = 1
        if snareTiming2 < hihatTiming2 - threshold:
            microtimingToCymbalProfile[3] = 1

        if kickTiming3 > hihatTiming3 + threshold:
            microtimingToCymbalProfile[4] = 1
        if kickTiming3 < hihatTiming3 - threshold:
            microtimingToCymbalProfile[5] = 1
        if snareTiming4 > hihatTiming4 + threshold:
            microtimingToCymbalProfile[6] = 1
        if snareTiming4 < hihatTiming4 - threshold:
            microtimingToCymbalProfile[7] = 1

        self.microtimingEventProfile = np.hstack([microtimingToGridProfile,microtimingToCymbalProfile])
        print(self.microtimingEventProfile)

    def getPushness(self):
        pass

    def getLaidbackness(self):
        pass

    def getOntopness(self):
        pass

    def getAverageTimingDeviation(self):
        #self.averageTimingMatrix = np.sum(np.nan_to_num(self.microtimingMatrix), axis=1)
        self.averageTimingMatrix = np.zeros([self.microtimingMatrix.shape[0]])
        for i in range(self.microtimingMatrix.shape[0]):
            rowSum = 0.0
            hitCount = 0.0
            rowIsEmpty = np.all(np.isnan(self.microtimingMatrix[i,:]))
            if rowIsEmpty:
                self.averageTimingMatrix[i] = np.nan
            else:
                for j in range(self.microtimingMatrix.shape[1]):
                    if np.isnan(self.microtimingMatrix[i,j]):
                        pass
                    else:
                        rowSum += self.microtimingMatrix[i,j]
                        hitCount += 1.0
                self.averageTimingMatrix[i] = rowSum / hitCount
        return self.averageTimingMatrix














