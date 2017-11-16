import os
import re
import glob
import logging
import functools

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
        logger.debug('Found %d files of format %s', len(infiles_found), fmtkey)
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
    infiles_filtered = []
    for infile in infiles:
        date = meta.dates_from_fname(infile, zero_time=True)[0]
        if start_date is not None:
            if date < start_date:
                continue
        if end_date is not None:
            if date > end_date:
                continue
        infiles_filtered.append(infile)
    return infiles_filtered


def filter_rel_orbit_numbers(infiles, rel_orbit_numbers):
    """Filter files that have an orbit number specified in rel_orbit_numbers"""
    infiles_filtered = []
    for infile in infiles:
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
    if matches and aoi is not None:
        matches &= metadata['footprint'].intersects(aoi)
    if matches and rel_orbit_numbers:
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

    filterfunc = functools.partial(_filter_infile, **filterkw)
    infiles = list(filter(filterfunc, infiles))
    return infiles
