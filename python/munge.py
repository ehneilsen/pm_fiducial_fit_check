#!/bin/env python
"""Read data from all sources and merge into a single hdf5 file
"""
# imports

import sys
import io
import time
from argparse import ArgumentParser
import logging
from collections import OrderedDict

import numpy as np
import pandas as pd
from astropy.io import fits

logging.Formatter.converter = time.gmtime
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)


# constants

INVENTORY_COLUMN_NAMES = ['night', 'expid', 'ra', 'dec', 'ut', 'ha',
                          'adc1', 'adc2', 'seq', 'program']

HEADER_PARAMS = {
    'airmass': 'AIRMASS',
    'az': 'MOUNTAZ',
    'el': 'MOUNTEL',
    'zd': 'ZD',
    'q': 'PARALLAC',
    'humidity': 'HUMIDITY',
    'pressure': 'PRESSURE',
}

FOCUS_ELEMENTS = ('xtrans', 'ytrans', 'ztrans', 'xtilt', 'ytilt', 'ztilt')

#MIN_NUM_FIDUCIALS = 110
MIN_NUM_FIDUCIALS = 100
MAX_POS_RMS = 0.05

# exception classes

# interface functions

def munge(qcinv_fname, fits_dir, zth_dir):
    qcinv = load_qcinv(qcinv_fname)
    fits_params = read_fits_header_params(fits_dir, qcinv)
    zths = read_zths(zth_dir, qcinv)
    exp_params = qcinv.merge(fits_params, right_index=True, left_index=True)

    fids = exp_params.merge(zths, left_index=True, right_index=True)

    def read_num_fiducials(expid):
        fiducials = read_fvcMerge(expid, zth_dir)
        num_fiducials = len(fiducials)
        return num_fiducials

    fids['num_fiducials'] = fids['expid'].map(read_num_fiducials)
    fids['successful'] = fids.eval(f'(num_fiducials>={MIN_NUM_FIDUCIALS}) & (xrms <= {MAX_POS_RMS}) & (yrms <= {MAX_POS_RMS})')
    good_exp_params = exp_params.loc[fids['expid']]
    good_exp_params['successful'] = fids['successful'] 
    
    fids.columns = pd.MultiIndex.from_tuples(
        [x if len(x) == 3 and not isinstance(x, str) else (x, ) for x in fids.columns])

    
    return good_exp_params, fids

# classes

# internal functions & classes


def load_qcinv(fname):
    """Read the inventory data file
    """
    logging.debug(f'Reading {fname}')
    inventory_text = (open(fname, 'r')
                      .read()
                      .replace('everywhere script', 'everywhere_script'))
    qcinv = pd.read_csv(io.StringIO(inventory_text), sep='\s+',
                        names=INVENTORY_COLUMN_NAMES,
                        parse_dates=['night'])
    qcinv.set_index('expid', drop=False, inplace=True)
    qcinv = qcinv[qcinv['ut'].str.len() == 5]
    qcinv['mjd'] = (
        pd.DatetimeIndex(qcinv['night']
                         .dt.strftime('%Y-%m-%d')+"T"+qcinv['ut']+'Z')
        .to_julian_date()-2400000.5)
    return qcinv


def read_one_fits_header_params(expid, fits_dir):
    values = OrderedDict()
    values['expid'] = expid
    fname = f'{fits_dir}/{expid}/fvc-{expid:08d}.fits.fz'
    logging.debug(f'Reading {fname}')
    hdus = fits.open(fname)
    for key in HEADER_PARAMS:
        values[key] = hdus[0].header[HEADER_PARAMS[key]]

    # Parse FOCUS keyword
    focus_values = tuple(
        float(v) for v in hdus[0].header['FOCUS'].split(','))
    for elem, value in zip(FOCUS_ELEMENTS, focus_values):
        values[f'focus_{elem}'] = value
    
    result = pd.Series(values, name=expid)
    return result


def read_fits_header_params(fits_dir, qcinv):
    fits_params_rows = []
    for expid, row in list(qcinv.iterrows()):
        try:
            fits_params_rows.append(
                read_one_fits_header_params(expid, fits_dir))
        except:
            logging.exception(f'Could not read file')
    fits_params = pd.DataFrame(fits_params_rows)
    fits_params['expid'] = fits_params['expid'].astype(int)
    fits_params.set_index('expid', inplace=True)
    return fits_params


def read_zth(expid, zth_dir):
    zth_short_elems = []
    zth_long_elems = []
    for poly in ('xzth', 'yzth'):
        fname = f'{zth_dir}/{expid}/{poly}-{expid}.0.par'
        logging.debug(f'Reading {fname}')
        with open(fname, 'r') as fp:
            zth_str = (fp.read().replace('None', poly)
                       .replace(',sig', '_sig').replace(',', "\t"))

        shortlines = []
        longlines = []
        for line in zth_str.split("\n"):
            elems = line.split()
            if len(elems) == 2:
                shortlines.append(' '.join(elems))
            elif len(line.split()) == 3:
                longlines.append(' '.join([poly]+elems))
        long_str = "\n".join(longlines)
        long_df = pd.read_csv(io.StringIO(long_str),
                              names=('poly', 'order', 'term', 'value'),
                              sep=' ')
        long_df['order'] = long_df['order'].astype(int)
        long_df.set_index(['poly', 'order', 'term'], inplace=True)
        long_df.index.names = (None, None, None)
        zth_long_elems.append(long_df)

        short_str = "\n".join(shortlines)
        short_df = pd.read_csv(io.StringIO(short_str),
                               names=('term', 'value'),
                               sep=' ')
        short_df.set_index('term', inplace=True)
        short_df.index.name = None
        zth_short_elems.append(short_df)

    long_zths = pd.concat(zth_long_elems)
    short_zths = pd.concat(zth_short_elems)
    zths = pd.concat([short_zths, long_zths]).T
    zths['expid'] = expid
    zths_series = zths.T['value']
    return zths_series


def read_zths(zth_dir, qcinv):
    zth_rows = []
    for expid, row in list(qcinv.iterrows()):
        try:
            zth_rows.append(read_zth(expid, zth_dir))
        except:
            logging.exception(f'Could nor read file')
    zths = pd.DataFrame(zth_rows)
    zths['expid'] = zths['expid'].astype(int)
    zths.set_index('expid', inplace=True)
    return zths


def read_fvcMerge(expid, data_dir):
    fname = f'{data_dir}/{expid}/fvcMerge-{expid}.dat'
    try:
        fiducials = pd.read_csv(fname, sep="\s+")
        return fiducials
    except:
        pass

    fname = f'{data_dir}/{expid}/fvcMerge-{expid}.0.dat'
    try:
        fiducials = pd.read_csv(fname, sep="\s+")
    except:
        logging.exception(f'Could not read {fname}')
        return pd.DataFrame()

    return fiducials


def main():
    parser = ArgumentParser(description="Read the qcinv data file")
    parser.add_argument("qcinv_fname", type=str,
                        help="file with results of qcinv")
    parser.add_argument("data_dir", type=str, help="data directory")
    parser.add_argument("out_fname", type=str, help="file to write")
    parser.add_argument("--exp_params_fname", type=str, default=None, help="file to write")
    parser.add_argument("--fids_fname", type=str, default=None, help="file to write")
    args = parser.parse_args()

    qcinv_fname = args.qcinv_fname
    data_dir = args.data_dir
    out_fname = args.out_fname

    exp_params, fids = munge(qcinv_fname, data_dir, data_dir)
    exp_params.to_hdf(out_fname, 'exp_params')
    fids.to_hdf(out_fname, 'fids')

    if args.exp_params_fname is not None:
        exp_params.to_csv(args.exp_params_fname, sep="\t", header=True, index=False)

    if args.fids_fname is not None:
        flat_fids = fids.copy()
        def colstr(col):
            colname = col[0]
            for c in col[1:]:
                if c is None:
                    continue
                elif isinstance(c, str):
                    colname = colname + "," + c
                elif np.isfinite(c) and c == int(c):
                    colname = colname + "," + str(int(c))
                elif str(c) != 'nan':
                    colname = colname + "," + str(c)
            return colname
        
        flat_fids.columns = [colstr(col) for col in flat_fids.columns.values]
        flat_fids.to_csv(args.fids_fname, sep="\t", header=True, index=False)

    return 0


if __name__ == '__main__':
    status = main()
    sys.exit(status)
