import pandas as pd
import numpy as np

from scipy import stats

import matplotlib.pyplot as plt
import seaborn as sns

__all__ = [
    'compare_ttest',
]


def compare_ttest(resultA, resultB, labels=['A', 'B'], key='val_score'):

    # Check input
    assert key in resultA, f"<resultA> has no '{key}'"
    assert key in resultB, f"<resultB> has no '{key}'"
    a = resultA[key]
    b = resultB[key]
    assert len(a) == len(b), 'Both scores must be of the same size'
    n = len(a)

    # t-test
    t, p = stats.ttest_rel(a, b)

    # Plot
    _, axes = plt.subplots(2, 2)

    # Plot box
    ax = axes[0, 0]
    sns.boxplot(labels, [a, b], linewidth=2.0, ax=ax)
    ax.grid(alpha=0.2)

    # Plot pairs
    ax = axes[1, 0]
    for x, y in zip(a, b):
        ax.plot(labels, [x, y], 'o-', color='b', alpha=0.8)
    ax.plot(labels, [np.mean(a), np.mean(b)], 'o-', color='w')
    ax.grid(alpha=0.2)

    # Plot dist
    ax = axes[0, 1]
    sns.distplot(a, 10, label=labels[0], ax=ax)
    sns.distplot(b, 10, label=labels[1], ax=ax)
    ax.grid(alpha=0.2)
    ax.legend()

    # Plot proba
    ax = axes[1, 1]
    x_abs = max(5, abs(t))
    x_min, x_max = -x_abs, +x_abs

    xx = np.arange(t, x_max, 0.001)
    yy = stats.t.pdf(xx, n-1)
    ax.plot(xx, yy, color='gray')
    ax.fill_between(xx, yy, color='gray', alpha=0.2)

    xx = np.arange(x_min, t, 0.001)
    yy = stats.t.pdf(xx, n-1)
    ax.plot(xx, yy, color='r')
    ax.fill_between(xx, yy, color='r', alpha=0.2)

    ax.legend(['t-value = {:.4f}'.format(t),
               'p-value = {:.4f}'.format(p)])
    ax.grid(alpha=0.2)

    return t, p


def compare_roc_auc(resultA, resultB):

    # Check input
    pass