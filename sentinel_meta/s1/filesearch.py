import os
import re
import glob
import logging

import numpy as np
from tqdm import tqdm

from . import meta

logger = logging.getLogger('sentinel_meta.s1.filesearch')


def filter_infiles_by_date(infiles, start_date=None, end_date=None):
    if not infiles:
        return infiles
    dates = np.array([meta.dates_from_fname(fname, zero_time=True)[0] for fname in infiles])
    sortind = np.argsort(dates)
    dates = dates[sortind]
    infiles = np.array(infiles, dtype=object)[sortind]

    if start_date is None:
        start_date = dates[0]

    if end_date is None:
        end_date = dates[-1]

    mask = (dates >= start_date) & (dates <= end_date)
    return list(infiles[mask])


def filter_orbit_numbers(infiles, orbit_numbers):
    """Filter files that have an orbit number specified in orbit_numbers"""
    if not orbit_numbers:
        return infiles

    infiles_filtered = []
    for infile in tqdm(infiles, desc='Orbit number filter', unit='input file'):
        try:
            o = meta.get_orbit_number(infile)
        except meta.MetaDataError as me:
            logger.info('Unable to get orbit number from file \'{}\'. {}. Skipping.'.format(infile, me))
            continue
        logger.debug('Input file \'{}\' has orbit number {}.'.format(infile, o))
        if o in orbit_numbers:
            infiles_filtered.append(infile)
    return infiles_filtered


def find_input_files(indir, formats=['zip', 'SAFE']):
    """Find sets of input files for given extensions

    Parameters
    ----------
    indir : str
        path to directory to search
    formats : list of str in ['zip', 'SAFE']
        file formats to find
    """
    # file patterns to search for in wholedir
    patterns = {
            'SAFE': 'S1?_*.SAFE',
            'zip': 'S1?_*.zip'}

    filesets = []
    for fmtkey in formats:
        filepattern = os.path.join(indir, patterns[fmtkey])
        logger.debug('File search pattern is \'{}\'.'.format(filepattern))
        infiles_found = glob.glob(filepattern)
        logger.info('Found {} files of format {}'.format(len(infiles_found), fmtkey))
        if infiles_found:
            filesets.append(infiles_found)
    if len(filesets) > 1:
        raise ValueError('Input files should be of only one format in {}.'.format(formats))
    return filesets[0]


def check_same_infile_type(infiles):
    """Check whether all input files have same file type"""
    if not infiles:
        return True
    patterns = ['manifest\.safe', '.*\.zip', '.*\.SAFE']
    all_match = []
    for pattern in patterns:
        matching = [re.match(pattern, os.path.basename(infile)) is not None for infile in infiles]
        if matching:
            all_match.append(all(matching))
    if sum(all_match) == 1:
        return True
    else:
        return False


def filter_input_files(infiles, start_date=None, end_date=None, orbit_numbers=[]):
    """Filter input files by date range and orbit number"""
    infiles = filter_infiles_by_date(infiles, start_date=start_date, end_date=end_date)

    if orbit_numbers:
        infiles = filter_orbit_numbers(infiles, orbit_numbers)

    logger.debug('Number of files matching filtering criteria: {}'.format(len(infiles)))
    return infiles
