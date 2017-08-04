import os
import re
import glob
import logging
import multiprocessing

import numpy as np

from satmeta.s1 import meta

logger = logging.getLogger(__name__)

search_patterns = {
        'SAFE': 'S1?_*.SAFE',
        'zip': 'S1?_*.zip'}


def find_input_files(indir, formats=['zip', 'SAFE'], ignore_empty=True):
    """Find sets of input files for given extensions

    Parameters
    ----------
    indir : str
        path to directory to search
    formats : list of str in ['zip', 'SAFE']
        file formats to find
    ignore_empty : bool
        ignore empty files

    Returns
    -------
    list of str : infile paths for all requested formats
    """
    infiles = []
    for fmtkey in formats:
        filepattern = os.path.join(indir, search_patterns[fmtkey])
        logger.debug('File search pattern is \'%s\'.', filepattern)
        infiles_found = glob.glob(filepattern)
        logger.info('Found %d files of format %s', len(infiles_found), fmtkey)
        if ignore_empty and fmtkey == 'zip':
            infiles_found = list(filter(os.path.getsize, infiles_found))
        infiles += infiles_found
    return infiles


def filter_infiles_by_date(infiles, start_date=None, end_date=None):
    """Filter a list of input files by date

    Parameters
    ----------
    infiles : list of str
        paths to input files
        must be standard S1 names
    start_date, end_date : datetime.datetime
        date range
    """
    if not infiles:
        return infiles
    dates = np.array([meta.dates_from_fname(fname, zero_time=True)[0] for fname in infiles])

    if start_date is None:
        start_date = dates.min()

    if end_date is None:
        end_date = dates.max()

    mask = (dates >= start_date) & (dates <= end_date)
    return list(np.array(infiles, dtype=object)[mask])


def filter_rel_orbit_numbers(infiles, rel_orbit_numbers):
    """Filter files that have an orbit number specified in rel_orbit_numbers"""
    if not rel_orbit_numbers:
        return infiles

    try:
        from tqdm import tqdm
        infile_iter = tqdm(infiles, desc='Orbit number filter', unit='input file')
    except ImportError:
        infile_iter = infiles

    infiles_filtered = []
    for infile in infile_iter:
        try:
            o = meta.get_rel_orbit_number(infile)
        except meta.MetaDataError as me:
            logger.info(
                    'Unable to get orbit number from file \'%s\'. %s. Skipping.',
                    infile, me)
            continue
        logger.debug('Input file \'%s\' has orbit number %s.', infile, o)
        if o in rel_orbit_numbers:
            infiles_filtered.append(infile)
    return infiles_filtered


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


def _metadata_matches(metadata, rel_orbit_numbers=None, aoi=None):
    matches = True
    if aoi is not None:
        matches &= metadata['footprint'].overlaps(aoi)
        if not matches:
            return matches
    if rel_orbit_numbers:
        matches &= metadata['relative_orbit_number'] in rel_orbit_numbers
    return matches


def _filter_infile(infile, **kwargs):
    metadata = meta.find_parse_metadata(infile)
    return _metadata_matches(metadata, **kwargs)


def filter_input_files(infiles, start_date=None, end_date=None, rel_orbit_numbers=[], aoi=None):
    """Filter input files by date range and orbit number

    Parameters
    ----------
    infiles : list of str
        input files to filter
    start_date, end_date : datetime.datetime
        date range
    rel_orbit_numbers : list of int
        relative orbit numbers
    aoi : shapely.geometry.Polygon
        area of interest
        in WGS84

    Note
    ----
    Filtering by rel_orbit_numbers and aoi requires
    loading the metadata for all files in date range

    Returns
    -------
    list of str : filtered list of paths
    """
    # filter by date first (fastest)
    infiles = filter_infiles_by_date(infiles, start_date=start_date, end_date=end_date)
    if not infiles:
        return []

    filterkw = {}
    if rel_orbit_numbers:
        filterkw['rel_orbit_numbers'] = rel_orbit_numbers
    if aoi is not None:
        filterkw['aoi'] = aoi

    if not filterkw:
        return infiles

    try:
        from tqdm import tqdm
        infile_iter = tqdm(infiles, desc='input file filter', unit='input file')
    except ImportError:
        infile_iter = infiles

    try:
        import joblib
        num_cores = multiprocessing.cpu_count()
        njobs = min((num_cores, 4))
        mask = joblib.Parallel(n_jobs=njobs)(
                joblib.delayed(_filter_infile)(infile, **filterkw) for infile in infile_iter)
    except ImportError:
        mask = [_filter_infile(infile, **filterkw) for infile in infiles]

    infiles = list(np.array(infiles, dtype='object')[mask])
    logger.debug(
            'Number of files matching filtering criteria: %d', len(infiles))
    return infiles
