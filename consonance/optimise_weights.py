import numpy as np
from consonance import exclusion_combinations, get_octave_intervals, interval_class, count


def optimise_interval_weights(pitches_lst, ratings, exclude_ivls=[], agg_method="type"):
    """
    Optimise weights for pairwise intervals in chords, given behavioural ratings.

    :param pitches_lst: list of lists of chord MIDI pitches
    :param ratings: behavioural ratings for each chord in pitches_lst
    :params exclude_ivls: list of intervals used to split weights
    :param agg_method: "sum" or "type"
    :return: if exclude_ivls is empty, list of interval weights;
             else list of weights lists for each combiniation including/excluding given intervals
    """
    intervals_lst = np.array([get_octave_intervals(ps) for ps in pitches_lst], dtype=object)
    interval_set = set(np.concatenate(intervals_lst))

    if exclude_ivls == []:
        weights = optimise_weights(intervals_lst, ratings, interval_set, agg_method)
        weights = include_missing(weights, interval_set, range(1, 13))

    else:
        exclusions = exclusion_combinations(exclude_ivls)
        exclusions.sort(key=len, reverse=True)
        exclusion_groups = get_exclusion_groups(intervals_lst, exclusions)

        weights = []
        for i, ex in enumerate(exclusions):
            ex_ivl_set = {x for x in interval_set if x not in ex}
            mask = exclusion_groups == i
            ex_weights = optimise_weights(intervals_lst[mask], ratings[mask], ex_ivl_set, agg_method)
            ex_weights = include_missing(ex_weights, ex_ivl_set, range(1, 13))
            weights.append(ex_weights)

    return weights


def optimise_interval_class_weights(pitches_lst, ratings, exclude_ivcs=[], agg_method="type"):
    """
    Optimise weights for pairwise interval classes in chords, given behavioural ratings.

    :param pitches_lst: list of lists of chord MIDI pitches
    :param ratings: behavioural ratings for each chord in pitches_lst
    :params exclude_ivcs: list of interval classes used to split weights
    :param agg_method: "sum" or "type"
    :return: if exclude_ivcs is empty, list of interval-class weights;
             else list of weights lists for each combiniation including/excluding given classes
    """
    ivclasses_lst = np.array([
        [interval_class(ivl) for ivl in get_octave_intervals(ps)]
        for ps in pitches_lst
    ], dtype=object)
    ivclass_set = set(np.concatenate(ivclasses_lst))

    if exclude_ivcs == []:
        weights = optimise_weights(ivclasses_lst, ratings, ivclass_set, agg_method)
        weights = include_missing(weights, ivclass_set, range(7))

    else:
        exclusions = exclusion_combinations(exclude_ivcs)
        exclusions.sort(key=len, reverse=True)
        exclusion_groups = get_exclusion_groups(ivclasses_lst, exclusions)

        weights = []
        for i, ex in enumerate(exclusions):
            ex_ivc_set = {x for x in ivclass_set if x not in ex}
            mask = exclusion_groups == i
            ex_weights = optimise_weights(ivclasses_lst[mask], ratings[mask], ex_ivc_set, agg_method)
            ex_weights = include_missing(ex_weights, ex_ivc_set, range(7))
            weights.append(ex_weights)

    return weights


def optimise_weights(intervals_lst, ratings, interval_set, agg_method="type"):
    """Optimise weights by minimising sum-of-squares function."""
    if len(intervals_lst) != len(ratings):
        raise Exception("lists of chords and ratings must be same length")

    n = len(ratings)
    m = len(interval_set)
    A = np.zeros((n, m))
    for i in range(n):
        counts = count(intervals_lst[i], list(interval_set))
        if agg_method == "sum":
            A[i, :] = counts
        if agg_method == "type":
            A[i, :] = counts / len(intervals_lst[i])

    At = np.matrix.transpose(A)
    B = np.linalg.inv(np.matmul(At, A))
    weights = np.matmul(B, np.matmul(At, ratings))

    return weights.tolist()


def include_missing(weights, interval_set, full_range):
    """Return weights with missing intervals as None."""
    full_weights = []
    j = 0
    for i in full_range:
        if i in interval_set:
            full_weights.append(weights[j])
            j += 1
        else:
            full_weights.append(None)
    return full_weights


def get_exclusion_groups(intervals_lst, exclusions):
    """For each chord, find group where no chord intervals are excluded."""
    exclusion_group = np.empty(intervals_lst.size)
    for i, ivls in enumerate(intervals_lst):
        for j, ex in enumerate(exclusions):
            if all(ivl not in ex for ivl in ivls):
                exclusion_group[i] = j
                break
    return exclusion_group

