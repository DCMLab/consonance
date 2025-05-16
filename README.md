# Optimising computational measures from behavioural data predicts perceived consonance


## Calculating consonance

This package contains tools for estimating consonance and dissonance based on pairwise intervals within a chord. Two functions are provided: (1) for calculating consonance using intervals (minor 2nd to octave) `interval_consonance`, and (2) using interval classes (0-6) `interval_class_consonance`.

Both accept:

1. A chord (*i.e.*, a list of MIDI pitches)
2. A list of weights (length 12 or 7 for interval and interval-class measure, respectively), or list of multiple weights' lists if conditionally excluding certain intervals (see below)
3. An aggregation method, either: `"sum"` where weights are combined by addition, or `"type"` where interval counts are first normalised.


For example, we can create a simple measure of consonance using binary consonance/dissonance classifications for each interval as weights:

```python
from consonance.consonance import interval_consonance

chord1 = [60, 64, 67]  # i.e., a C major chord
chord2 = [60, 61, 62]  # a dissonant cluster chord

binary_weights = [-1, -1, 1, 1, 1, -1, 1, 1, 1, -1, -1, 1]

interval_consonance(chord1, binary_weights, agg_method="sum")
# 3.0

interval_consonance(chord2, binary_weights, agg_method="sum")
# -3.0
```


## Optimising weights

Given a dataset of chords and ratings of consonance, optimal weights can be obtained. Again functions are provided to optimise weights for intervals (`optimise_interval_weights`) and interval classes (`optimise_interval_class_weights`).

The three datasets using in this paper are given in `./data`:

a. Bowling et al. (2018): 298 chords (all 2, 3 and 4 combinations in one octave)
b. Johnson-Laird et al. (2012): 55 three-note chords and 43 four-note chords
c. Popescu et al. (2019): 60 chords from Classical, Jazz and Avant-garde repertoire

(also see Peter Harrison's [inconData](https://github.com/pmcharrison/inconData) for A, B and further datasets)

Here, we also scale ratings, where -1 is the most dissonant value on the available rating scale, and +1 the most consonant.


```python
import pandas as pd
from optimise_weights import optimise_interval_weights

def parse_pitches(pitches_str):
    return [int(x) for x in pitches_str.split(",")]
    
def scale_ratings(rating, r_con, r_dis):
    return ((2 * (rating - r_dis)) / (r_con - r_dis)) - 1

bowling2018 = pd.read_table("data/bowling2018_consonance.tsv")

pitches = bowling2018.pitches.apply(parse_pitches)
ratings = bowling2018.rating.apply(scale_ratings, args=(4, 1))

optimise_interval_weights(pitches, ratings, agg_method="sum")
# [-0.39315701025321464,
#  -0.036022745929167974,
#  -0.005999857211278825,
#  0.047937002169191084,
#  0.13833299878214417,
#  -0.117640706624426,
#  0.15345017924359666,
#  -0.07721218728660789,
#  -0.029456392748971896,
#  -0.14381589959165952,
#  -0.19649184453467064,
#  0.24340298910163627]
```


## Conditional inclusion/exclusion of intervals

Different sets of weights can also be optimised based on the conditional inclusion/exclusion of interval(s). Intervals to exclude can be supplied as a list using `exclude_ivls`. Weights for all combinations will be optimised.

```python
weights_ex8 = optimise_interval_weights(pitches, ratings, exclude_ivls=[8], agg_method="sum")
# [[-0.3856, -0.0767, -0.0108,  0.1334, 0.1256, -0.1476, 0.1439,    None,  0.0080, -0.1758, -0.1884, 0.2332],
#  [-0.3777, -0.0068, -0.0232, -0.0548, 0.1900, -0.0887, 0.1709, -0.0933, -0.0852, -0.1306, -0.1962, 0.3980]]
```

Weights supplied as list of lists can be used in the consonance function. Weights lists must be supplied for all combinations of excluded or included intervals. Excluded weights have value of `None`.

```python
interval_consonance(chord1, weights_ex8, agg_method="sum")
# 0.2664685521562091

interval_consonance(chord2, weights_ex8, agg_method="sum")
# -0.8479383716037261
```


## References

Bowling, D. L., Purves, D., & Gill, K. Z. (2018). Vocal similarity predicts the relative attraction of musical chords. *Proceedings of the National Academy of Sciences*, *115*(1), 216–221. [https://doi.org/10.1073/pnas.1713206115](https://doi.org/10.1073/pnas.1713206115)

Johnson-Laird, P. N., Kang, O. E., & Leong, Y. C. (2012). On musical dissonance. *Music Perception*, *30*(1), 19–35. [https://doi.org/10.1525/mp.2012.30.1.19](https://doi.org/10.1525/mp.2012.30.1.19)

Popescu, T., Neuser, M. P., Neuwirth, M., Bravo, F., Mende, W., Boneh, O., Moss, F. C., & Rohrmeier, M. (2019). The pleasantness of sensory dissonance is mediated by musical style and expertise. *Scientific Reports*, *9*(1), 1070. [https://doi.org/10.1038/s41598-018-35873-8](https://doi.org/10.1038/s41598-018-35873-8)

