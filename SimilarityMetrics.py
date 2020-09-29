# 3 Similarity measures for comparing drum patterns: velocity-weighted Hamming distance, fuzzy Hamming distance and
# structural similarity. See paper for more detailed descriptions. Optional beat awareness weighting for Hamming.

import numpy as np
import math

def weighted_Hamming_distance(grooveA, grooveB, parts_count=10, beat_weighting="Off"):
    if parts_count == 3:
        a = grooveA.groove_3_Parts
        b = grooveB.groove_3_Parts
    elif parts_count == 5:
        a = grooveA.groove_5_Parts
        b = grooveB.groove_5_Parts
    elif parts_count == 10:
        a = grooveA.groove_10_Parts
        b = grooveB.groove_10_Parts

    if beat_weighting == "On":
        a = _weight_groove(a)
        b = _weight_groove(b)



    x = (a.flatten()-b.flatten())
    return math.sqrt(np.dot(x, x.T))


def fuzzy_Hamming_distance(grooveA, grooveB, parts_count=10, beat_weighting="Off"):
    # Get fuzzy Hamming distance as velocity weighted Hamming distance, but with 1 metrical distance lookahead/back
    # and microtiming weighting
    #
    if parts_count == 3:
        a = grooveA.groove_3_Parts
        b = grooveB.groove_3_Parts #TODO: implement timing matrix combination in Groove.py
    elif parts_count == 5:
        a = grooveA.groove_5_Parts
        b = grooveB.groove_5_Parts
    elif parts_count == 10:
        a = grooveA.groove_10_Parts
        a_timing = grooveA.timing_matrix
        b = grooveB.groove_10_Parts
        b_timing = grooveB.timing_matrix

    if beat_weighting == "On":
        a = _weight_groove(a)
        b = _weight_groove(b)

    timing_difference = np.nan_to_num(a_timing - b_timing)

    x = np.zeros(a.shape)
    tempo = 120.0
    steptime_ms = 60.0 * 1000 / tempo / 4 # semiquaver step time in ms


    difference_weight = timing_difference / 125.
    difference_weight = 1+np.absolute(difference_weight)
    single_difference_weight = 400

    for j in range(parts_count):
        for i in range(31):
            if a[i,j] != 0.0 and b[i,j] != 0.0:
                x[i,j] = (a[i,j] - b[i,j]) * (difference_weight[i,j])
            elif a[i,j] != 0.0 and b[i,j] == 0.0:
                if b[(i+1)%32, j] != 0.0 and a[(i+1)%32, j] == 0.0:
                    single_difference = np.nan_to_num(a_timing[i,j]) - np.nan_to_num(b_timing[(i+1)%32,j]) + steptime_ms
                    if single_difference < 125.:
                        single_difference_weight = 1 + abs(single_difference_weight/steptime_ms)
                        x[i,j] = (a[i,j] - b[(i+1)%32,j]) * single_difference_weight
                    else:
                        x[i, j] = (a[i, j] - b[i, j]) * difference_weight[i, j]

                elif b[(i-1)%32,j] != 0.0 and a[(i-1)%32, j] == 0.0:
                    single_difference =  np.nan_to_num(a_timing[i,j]) - np.nan_to_num(b_timing[(i-1)%32,j]) - steptime_ms

                    if single_difference > -125.:
                        single_difference_weight = 1 + abs(single_difference_weight/steptime_ms)
                        x[i,j] = (a[i,j] - b[(i-1)%32,j]) * single_difference_weight
                    else:
                        x[i, j] = (a[i, j] - b[i, j]) * difference_weight[i, j]
                else:
                    x[i, j] = (a[i, j] - b[i, j]) * difference_weight[i, j]

            elif a[i,j] == 0.0 and b[i,j] != 0.0:
                if b[(i + 1) % 32, j] != 0.0 and a[(i + 1) % 32, j] == 0.0:
                    single_difference =  np.nan_to_num(a_timing[i,j]) - np.nan_to_num(b_timing[(i+1)%32,j]) + steptime_ms
                    if single_difference < 125.:
                        single_difference_weight = 1 + abs(single_difference_weight/steptime_ms)
                        x[i,j] = (a[i,j] - b[(i+1)%32,j]) * single_difference_weight
                    else:
                        x[i, j] = (a[i, j] - b[i, j]) * difference_weight[i, j]

                elif b[(i-1)%32,j] != 0.0 and a[(i-1)%32, j] == 0.0:
                    single_difference =  np.nan_to_num(a_timing[i,j]) - np.nan_to_num(b_timing[(i-1)%32,j]) - steptime_ms
                    if single_difference > -125.:
                        single_difference_weight = 1 + abs(single_difference_weight/steptime_ms)
                        x[i,j] = (a[i,j] - b[(i-1)%32,j]) * single_difference_weight

                    else:
                        x[i, j] = (a[i, j] - b[i, j]) * difference_weight[i, j]

                else: # if no nearby onsets, need to count difference between onset and 0 value.
                    x[i, j] = (a[i, j] - b[i, j]) * difference_weight[i, j]


        fuzzy_distance = math.sqrt(np.dot(x.flatten(),x.flatten().T))
    return fuzzy_distance

def structural_similarity_distance(grooveA, grooveB):
    # Simialrity calculated between reduced versions of loops, measuring whether onsets occur in
    # roughly similar parts of two loops. Calculated as hamming distance between reduced versions.
    # of grooves
    a = grooveA.reduce_groove()
    b = grooveB.reduce_groove()
    rows_to_remove = [1,2,3,5,6,7,9,10,11,13,14,15,17,18,19,21,22,23,25,26,27,29,30,31]
    reducedA = np.delete(a, rows_to_remove, axis=0)
    reducedB = np.delete(b, rows_to_remove, axis=0)
    x = (a.flatten()-b.flatten())
    structural_difference = math.sqrt(np.dot(x, x.T))
    return structural_difference


def _weight_groove(self, groove):
    # Metrical awareness profile weighting for hamming distance.
    # The rhythms in each beat of a bar have different significance based on GTTM.
    beat_awareness_weighting = [1,1,1,1,
                              0.27,0.27,0.27,0.27,
                              0.22,0.22,0.22,0.22,
                              0.16,0.16,0.16,0.16,
                              1,1,1,1,
                              0.27,0.27,0.27,0.27,
                              0.22,0.22,0.22,0.22,
                              0.16,0.16,0.16,0.16,]

    for i in range(groove.shape[1]):
        groove[:,i] = groove[:,i] * beat_awareness_weighting
    return groove