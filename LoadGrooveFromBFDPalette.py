import os
from xml.dom.minidom import parse
import numpy as np
import csv

from fx.bfd.groove import *
from fx.common.filesystem import *

np.set_printoptions(suppress=True,precision=2)

def get_all_hit_info(hits, groove_len):
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
    :param groove_len:
    :return: grooveArray
    """
    all_events = np.zeros([len(hits), 4])
    open_hihat_artics = {0,1,2,3,6,7,19}
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

        all_events[i,0] = hits[i].beats
        all_events[i,1] = hits[i].velocity
        kit_piece_slot = int(hits[i].slotIndex)
        if kit_piece_slot == kickIndex:
            all_events[i,2] == 0
        if kit_piece_slot == snareIndex:
            all_events[i,2] =1

        # Split open and closed articulations into different categories.
        if kit_piece_slot == hihatIndex:
            if int(hits[i].articIndex) in open_hihat_artics:
                all_events[i,2] = 3
            else:
                all_events[i,2] = 2
        if kit_piece_slot == rideIndex:
            all_events[i,2] = 4
        if kit_piece_slot == crashIndex:
            all_events[i,2] = 5
        if kit_piece_slot == extraCymbalIndex:
            all_events[i,2] = 6
        if kit_piece_slot == floorTomIndex:
            all_events[i,2] = 7
        if kit_piece_slot == midTomIndex:
            all_events[i,2] = 8
        if kit_piece_slot == hiTomIndex:
            all_events[i,2] = 9
    return all_events

def get_grooves_from_bundle(grooveBundle):
    """ Get information for all grooves from within a bundle. Extract hits and
    groove names into arrays, then put grooves and names into two separate lists
    Assumes a groove is 2 bars long, 4/4
    :param grooveDom: groove object from .xml
    :return:
    """
    #todo: write this properly
    all_grooves_hit_info = []
    all_groove_names =[]

    for i in range(len(grooveBundle)):
        new_groove, tempo = getGrooveFromNode(grooveBundle[i])
        groove_len = new_groove.lengthInBeats
        all_hits = get_all_hit_info(new_groove.getAudibleHits(), groove_len)

        # round to semiquavers (0.25)
        multiplied_hit = all_hits[:,0]*4.0
        rounded_hits = multiplied_hit.round(decimals=0) / 4.0
        microtiming_variation_Beats = all_hits[:, 0] - rounded_hits
        microtiming_variation_MS = microtiming_variation_Beats * 60.0 * 1000 / tempo
        all_hits[:, 0] = rounded_hits
        all_hits[:, 3] = microtiming_variation_MS
        rounded_groove_events = all_hits

        all_grooves_hit_info.append(rounded_groove_events)
        all_groove_names.append(new_groove.name)
    return all_grooves_hit_info, all_groove_names, tempo

def get_groove_from_BFD_palette(filename, groove_name):
    # Get a single groove and its corresponding microtiming matrix in correct format
    # from extracted hit info.
    # Input = name of palette file + name of groove within that palette you want to use

    path_to_palettes = "Grooves/"
    palette_filename = filename

    bundle_node = getGrooveBundleNode(parse((path_to_palettes + palette_filename)))
    grooveBundle = getGrooveNodes(bundle_node)

    all_grooves_hit_info, all_groove_names, tempo = get_grooves_from_bundle(grooveBundle)

    hits_matrix = np.zeros([32, 10])
    timing_matrix = np.zeros([32,10])
    timing_matrix[:] = np.nan

    groove_index = all_groove_names.index(groove_name)
    single_groove_hit_info = all_grooves_hit_info[groove_index]

    for j in range(single_groove_hit_info.shape[0]):
        time_position = int(single_groove_hit_info[j,0]*4)
        kit_piece_position = int(single_groove_hit_info[j, 2])
        timing_matrix[time_position%32, kit_piece_position] = single_groove_hit_info[j,3]
        hits_matrix[time_position%32, kit_piece_position] = single_groove_hit_info[j,1]

    return hits_matrix, timing_matrix, tempo

def get_all_grooves_from_BFD_palette(filename):
    path_to_palettes = ""
    palette_filename = filename

    hits_matricies = []
    timing_matricies = []
    names = []
    bundle_node = getGrooveBundleNode(parse((path_to_palettes + palette_filename)))
    grooveBundle = getGrooveNodes(bundle_node)

    all_grooves_hit_info, all_groove_names, tempo = get_grooves_from_bundle(grooveBundle)

    for i in range(len(all_grooves_hit_info)):
        hits_matrix = np.zeros([32, 10])
        timing_matrix = np.zeros([32, 10])
        timing_matrix[:] = np.nan

        single_groove_hit_info = all_grooves_hit_info[i]
        for j in range(single_groove_hit_info.shape[0]):
            time_position = int(single_groove_hit_info[j, 0] * 4)
            kit_piece_position = int(single_groove_hit_info[j, 2])
            timing_matrix[time_position % 32, kit_piece_position] = single_groove_hit_info[j, 3]
            hits_matrix[time_position % 32, kit_piece_position] = single_groove_hit_info[j, 1]
        hits_matricies.append(hits_matrix)
        timing_matricies.append(timing_matrix)
    return hits_matricies, timing_matricies, all_groove_names

def get_groove_list_format(filename, groove_name):
    path_to_palettes = "Grooves/"
    palette_filename = filename
    bundle_node = getGrooveBundleNode(parse((path_to_palettes + palette_filename)))
    grooveBundle = getGrooveNodes(bundle_node)

    all_grooves_hit_info = []
    all_groove_names =[]

    for i in range(len(grooveBundle)):
        new_groove, tempo = getGrooveFromNode(grooveBundle[i])
        groove_len = new_groove.lengthInBeats
        all_hits = get_all_hit_info(new_groove.getAudibleHits(), groove_len)
        all_hits[:,0] = all_hits[:,0] * 60.0 * 1000 / 120.0
        all_grooves_hit_info.append(all_hits[:,0:3])
        all_groove_names.append(new_groove.name)

    groove_index = all_groove_names.index(groove_name)
    single_groove_hit_list = all_grooves_hit_info[groove_index]
    print(groove_name, single_groove_hit_list)
    return single_groove_hit_list
