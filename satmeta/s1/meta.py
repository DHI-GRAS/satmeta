import re
import os.path
import functools
import datetime
import logging
import warnings

from . import metafile
from .. import converters

logger = logging.getLogger(__name__)


def dates_from_fname(fname, zero_time=False):
    fname = os.path.basename(fname)
    if zero_time:
        regex = '(\d{8})(?=t\d{6})'
        fmt = '%Y%m%d'
    else:
        regex = '\d{8}t\d{6}'
        fmt = '%Y%m%dt%H%M%S'
    dd = re.findall(regex, fname.lower())
    if not dd:
        raise ValueError(
            'Could not find dates of format \'{}\' '
            'in file name \'{}\'.'.format(fmt, fname))
    return [datetime.datetime.strptime(d, fmt) for d in dd]


def get_spacecraft_name(fname):
    fname = os.path.basename(fname)
    try:
        return re.match('(^S\d[AB])', fname).group()
    except AttributeError:
        raise ValueError('Unable to get spacecraft name from fname \'{}.\''.format(fname))


def get_product_date(fname):
    """Product date is the first date in file name"""
    return dates_from_fname(fname)[0].date()


def _get_relative_orbit_number(root):
    start = int(converters.get_single(root, 'safe:relativeOrbitNumber[@type=\'start\']'))
    stop = int(converters.get_single(root, 'safe:relativeOrbitNumber[@type=\'stop\']'))
    if start != stop:
        warnings.warn(
                'relativeOrbitNumber range from %s to %s. Only returning %s', start, stop, start)
    return start


def parse_metadata(metadatafile=None, metadatastr=None):
    root = converters.get_root(metadatafile, metadatastr)
    _get_single = functools.partial(converters.get_single, root)
    metadata = {
        'title': converters.get_instance(root, 'safe:resource', 'name', index=0),
        'footprint': converters.get_single_polygon_yx(root, 'gml:coordinates'),
        'relative_orbit_number': _get_relative_orbit_number(root),
        'sensing_start': converters.get_single_date(root, 'safe:startTime'),
        'sensing_end': converters.get_single_date(root, 'safe:stopTime'),
        'product_type': _get_single('s1sarl1:productType'),
        'polarizations': converters.get_all(root, 's1sarl1:transmitterReceiverPolarisation'),
        'passdir': _get_single('s1:pass'),
        'sensor_operational_mode': _get_single('s1sarl1:mode')}
    metadata['spacecraft'] = get_spacecraft_name(metadata['title'])
    metadata['sensing_time'] = metadata['sensing_start']
    return metadata


def find_parse_metadata(infile):
    """Find and parse manifest in SAFE or zip file"""
    if infile.endswith('.SAFE'):
        mstr = metafile.read_manifest_SAFE(infile)
    elif infile.endswith('.zip'):
        mstr = metafile.read_manifest_ZIP(infile)
    else:
        raise ValueError(
                'Input file/folder must end in .zip or .SAFE. '
                'Got \'{}\'.'.format(infile))
    return parse_metadata(metadatastr=mstr)