import os
from xml.dom.minidom import parse
import numpy as np
from matplotlib import pyplot as plt
import csv

from fx.bfd.groove import *
from fx.common.filesystem import *

np.set_printoptions(suppress=True,precision=2)

def getAllHitInfo(hits, grooveLength):
    """ Create list of all hits in a groove and relevant information for each
    Format: [quantized time index, velocity, kit piece, microtiming deviation from metronome]

    Vector format:
    0 Kick
    1 snare
    2 Closed Hihat
    3 Open Hihat
    4 Ride
    5 Crash
    6 Extra cymbal
    7 Low tom
    8 Mid tom
    9 High tom

    :param hits:
    :param grooveLength:
    :return: grooveArray
    """
    allEvents = np.zeros([len(hits), 4])
    openHiHatArtics = {0,1,2,3,6,7,19}
    kickIndex = 0
    snareIndex = 1
    hihatIndex = 2
    floorTomIndex = 3
    midTomIndex = 4
    hiTomIndex = 5
    crashIndex = 6
    extraCymbalIndex = 7
    rideIndex = 8

    closedHiHatArtics = {10,11,14,15,16,17,18,20,8000}
    for i in range(len(hits)):

        allEvents[i,0] = hits[i].beats
        allEvents[i,1] = hits[i].velocity
        kitPieceSlot = int(hits[i].slotIndex)
        if kitPieceSlot == kickIndex:
            allEvents[i,2] == 0
        if kitPieceSlot == snareIndex:
            allEvents[i,2] =1

        # Split open and closed articulations into different categories.
        if kitPieceSlot == hihatIndex:
            if int(hits[i].articIndex) in openHiHatArtics:
                allEvents[i,2] = 3
            else:
                allEvents[i,2] = 2
        if kitPieceSlot == rideIndex:
            allEvents[i,2] = 4
        if kitPieceSlot == crashIndex:
            allEvents[i,2] = 5
        if kitPieceSlot == extraCymbalIndex:
            allEvents[i,2] = 6
        if kitPieceSlot == floorTomIndex:
            allEvents[i,2] = 7
        if kitPieceSlot == midTomIndex:
            allEvents[i,2] = 8
        if kitPieceSlot == hiTomIndex:
            allEvents[i,2] = 9

    return allEvents

def getGroovesFromBundle(grooveBundle):
    """ Get information for all grooves from within a bundle. Extract hits and
    groove names into arrays, then put grooves and names into two separate lists
    Assumes a groove is 2 bars long, 4/4
    :param grooveDom: groove object from .xml
    :return:
    """
    allGroovesHitInfo = []
    allGrooveNames =[]

    for i in range(len(grooveBundle)):
        newGroove, tempo = getGrooveFromNode(grooveBundle[i])
        grooveLength = newGroove.lengthInBeats
        allHits = getAllHitInfo(newGroove.getAudibleHits(), grooveLength)

        # round to semiquavers (0.25)
        multipliedHit = allHits[:,0]*4.0
        roundedHit = multipliedHit.round(decimals=0) / 4.0
        microtimingVariationBeats = allHits[:, 0] - roundedHit
        microtimingVariationMS = microtimingVariationBeats * 60.0 * 1000 / tempo
        allHits[:, 0] = roundedHit
        allHits[:, 3] = microtimingVariationMS
        roundedGrooveEvents = allHits

        allGroovesHitInfo.append(roundedGrooveEvents)
        allGrooveNames.append(newGroove.name)
    return allGroovesHitInfo, allGrooveNames, tempo

def getGrooveFromBFDPalette(filename, grooveName):
    # Get a single groove and its corresponding microtiming matrix in correct format
    # from extracted hit info

    pathToPalettes = "/home/fred/BFD/python/GrooveToolbox/Grooves/"
    paletteFileName = filename

    bundleNode = getGrooveBundleNode(parse((pathToPalettes + paletteFileName)))
    grooveBundle = getGrooveNodes(bundleNode)

    allGroovesHitInfo, allGrooveNames, tempo = getGroovesFromBundle(grooveBundle)

    hitsMatrix = np.zeros([32, 10])
    timingMatrix = np.zeros([32,10])
    timingMatrix[:] = np.nan

    grooveIndex = allGrooveNames.index(grooveName)
    singleGrooveHitInfo = allGroovesHitInfo[grooveIndex]

    for j in range(singleGrooveHitInfo.shape[0]):
        timePosition = int(singleGrooveHitInfo[j,0]*4)
        kitPiecePosition = int(singleGrooveHitInfo[j, 2])
        timingMatrix[timePosition%32, kitPiecePosition] = singleGrooveHitInfo[j,3]
        hitsMatrix[timePosition%32, kitPiecePosition] = singleGrooveHitInfo[j,1]

    return hitsMatrix, timingMatrix, tempo