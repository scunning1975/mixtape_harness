#!/usr/bin/env python3
"""Randomization inference for a two-group difference in means.

Permutes the treatment labels to build the null distribution of the
difference in means, then reports how often a permuted difference is as
extreme as the one we actually observed. Use this for the falsification
step of the DiD checklist when the design has few treated units and the
usual asymptotic standard errors are not trustworthy.
"""
import numpy as np


def ri_pvalue(y, treat, n_perm=1000):
    """Return the randomization-inference p-value for a difference in means.

    y      : outcome, one value per unit
    treat  : 1 for treated units, 0 for control units
    n_perm : number of label permutations to draw (default 10,000)
    """
    y = np.asarray(y, dtype=float)
    treat = np.asarray(treat, dtype=float)
    obs = y[treat == 1].mean() - y[treat == 0].mean()

    count = 0
    for _ in range(n_perm):
        perm = np.random.permutation(treat)
        diff = y[perm == 1].mean() - y[perm == 0].mean()
        if diff > obs:
            count += 1
    return count / n_perm


if __name__ == "__main__":
    # quick smoke test: a real effect should land near p = 0
    y = [1, 1, 1, 0, 1, 0, 0, 0]
    treat = [1, 1, 1, 1, 0, 0, 0, 0]
    print("p =", ri_pvalue(y, treat))
