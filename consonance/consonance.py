import numpy as np
from itertools import combinations


def interval_consonance(pitches, weights, agg_method="type"):
    """
    Measure of consonance based on pairwise intervals in a chord.

    :param pitches: list of chord MIDI pitches
    :param weights: consonance contribution for intervals 1-12
    :param agg_method: "sum" or "type"
    :return: consonance value
    """
    intervals = get_octave_intervals(pitches)
    counts = count(intervals, range(1, 13))

    if type(weights[0]) == list:
        check_weight_exclusions(weights)
        weights = get_inclusion_weights(counts, weights)

    if len(weights) != 12:
        raise Exception("weights must be of length 12")

    if agg_method == "sum":
        score = np.inner(counts, weights)
    if agg_method == "type":
        score = np.inner(counts / len(intervals), weights)

    return score


def interval_class_consonance(pitches, weights, agg_method="type"):
    """
    Measure of consonance based on pairwise interval classes in a chord.

    :param pitches: list of chord MIDI pitches
    :param weights: consonance contribution for intervals 0-6
    :param agg_method: "sum" or "type"
    :return: consonance value
    """
    intervals = get_octave_intervals(pitches)
    interval_classes = [interval_class(ivl) for ivl in intervals]
    counts = count(interval_classes, range(7))

    if type(weights[0]) == list:
        check_weight_exclusions(weights)
        weights = get_inclusion_weights(counts, weights)

    if len(weights) != 7:
        raise Exception("weights must be of length 7")


    if agg_method == "sum":
        score = np.inner(counts, weights)
    if agg_method == "type":
        score = np.inner(counts / len(intervals), weights)

    return score


def check_weight_exclusions(weights_lsts):
    """
    Checks properties of list of weights when excluding intervals.
    Weights lists must have matching lengths.
    All possible exclusions of chosen intervals must be given.
    """
    # Check lengths
    size_first = len(weights_lsts[0])
    for lst in weights_lsts[1:]:
        if len(lst) != size_first:
            raise Exception("weights lists must all have the same length")

    # Check exclusions
    lst_ixs = [
        sorted([i for i, w in enumerate(weights) if w == None])
        for weights in weights_lsts
    ]
    lst_ixs.sort()
    ixs = []
    for lst in lst_ixs:
        for ix in lst:
            if ix not in ixs:
                ixs.append(ix)
    test_ixs = exclusion_combinations(ixs)
    if lst_ixs != test_ixs:
        raise Exception("exclusion combinations are not complete")


def exclusion_combinations(exclusion_ixs):
    """Return all combinations of excluded indices."""
    output = [[]]
    output += [
        sorted(list(c)) for i in range(1, len(exclusion_ixs) + 1)
        for c in combinations(exclusion_ixs, i)
    ]
    output.sort()
    return output


def get_inclusion_weights(counts, weights_lsts):
    """Return weights set for chord interval counts."""
    lst_ixs = [
        sorted([i for i, w in enumerate(weights) if w == None])
        for weights in weights_lsts
    ]
    order = np.flip(np.argsort([len(l) for l in lst_ixs]))
    for i in order:
        if not any(counts[j] > 0 for j in lst_ixs[i]):
            return [0 if x is None else x for x in weights_lsts[i]]


def get_octave_intervals(pitches):
    """Calculate all pairwise intervals, constrained to one octave."""
    raw_intervals = [p2 - p1 for p1, p2 in combinations(pitches, 2)]
    oct_intervals = [ivl % 12 for ivl in raw_intervals]
    for i, ivl in enumerate(oct_intervals):
        if ivl == 0:
            oct_intervals[i] = 12
    oct_intervals.sort()
    return oct_intervals


def interval_class(interval):
    return min(interval, 12 - interval)


def count(lst, items):
    """Return counts for every item in lst."""
    counts = np.zeros(len(items))
    for x in lst:
        counts[items.index(x)] += 1
    return counts

