#!/bin/env python
"""Plot fid distortion terms
"""
import sys
from argparse import ArgumentParser
import time
import logging
from collections import OrderedDict
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt


# constants


DISTORTION_NAMES = OrderedDict((
    (('xzth', 1), "scale factor (half mm at edge)"),
    (('xzth', 2), "E modes"),
    (('xzth', 3), "3rd order distortion"),
    (('xzth', 4), "higher order E modes"),
    (('xzth', 5), "5th order distortion"),
    (('yzth', 1), "rotation (half mm at edge)"),
    (('yzth', 2), "B modes"),
    (('yzth', 3), "spiral rotation")
))

DISTORTION_TERM_NAMES = OrderedDict((
    ('offset', 'offset'),
    ('s', 'sin'),
    ('c', 'cos')
))

PAGE_PARAMS = {1: tuple(DISTORTION_NAMES.keys())[:4],
               2: tuple(DISTORTION_NAMES.keys())[4:]}

HUMAN_LABELS = False

# configuration
mpl.rcParams['figure.figsize'] = (7.5, 10)
plt.style.use('ggplot')
plt.rc('font', size=7)
plt.rc('axes', titlesize=7)
plt.rc('axes', labelsize=7)
plt.rc('xtick', labelsize=7)
plt.rc('ytick', labelsize=7)
plt.rc('legend', fontsize=7)
plt.rc('figure', titlesize=12, dpi=100)

logging.Formatter.converter = time.gmtime
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

# exception classes

# interface functions


def plot_fids(exp_params, fids, xparam, distorts, stitle=None):
    nrow, ncol = len(distorts), len(DISTORTION_TERM_NAMES)
    fig, axes = plt.subplots(nrow, ncol,
                             sharex=True)
    for plot_row, distort in enumerate(distorts):
        for plot_column, term in enumerate(DISTORTION_TERM_NAMES.keys()):
            ax = axes[plot_row, plot_column]
            plot_fid(exp_params, fids, xparam,
                     distort, term, term+'_sig', ax=ax)
            if plot_row == nrow-1:
                ax.set_xlabel(xparam)
            if plot_row == 0:
                if HUMAN_LABELS:
                    ax.set_ylabel(DISTORTION_TERM_NAMES[term]
                                  + " term in "
                                  + DISTORTION_NAMES[distort])
                else:
                    ax.set_title(DISTORTION_TERM_NAMES[term])
            ax.set_ylabel(f'{distort[0]}, {distort[1]}, {term}')
    big_title = fig.suptitle(stitle, fontsize="x-large")
    plt.tight_layout()
    big_title.set_y(0.95)
    fig.subplots_adjust(top=0.90, wspace=0.3, hspace=0.1)
    return fig, axes

# classes

# internal functions & classes


def plot_fid(exp_params, fids, xcol, yterm, yparam, yerr_param, ax=None):

    df = exp_params.merge(fids[yterm], left_index=True, right_index=True)
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()
    try:
        yerr = df[yerr_param]
    except KeyError:
        yerr = 0

    ax.errorbar(df[xcol], df[yparam], yerr, linestyle='',
                marker='.', ecolor='#41B6E6', c='#002855', ms=1, lw=0.5)
    return fig, ax


def main():
    parser = ArgumentParser(description="Plot petal position and rotation")
    parser.add_argument("in_fname", type=str, help="file to read")
    parser.add_argument("xparam", type=str,
                        help="Parameter against which to plot values")
    parser.add_argument("page", type=int, help="Which page of plot to produce")
    parser.add_argument("out_fname", type=str, help="output directory name")
    args = parser.parse_args()

    in_fname = args.in_fname
    xparam = args.xparam
    params = PAGE_PARAMS[args.page]
    out_fname = args.out_fname

    logging.debug(f"Reading exp_params from {in_fname}")
    exp_params = pd.read_hdf(in_fname, 'exp_params')

    logging.debug(f"Reading fids from {in_fname}")
    fids = pd.read_hdf(in_fname, 'fids')

    stitle = 'parallactic angle' if xparam == 'q' else xparam
    fig, axes = plot_fids(exp_params, fids, xparam, params, stitle)
    fig.savefig(out_fname)

    return 0


if __name__ == '__main__':
    status = main()
    sys.exit(status)
