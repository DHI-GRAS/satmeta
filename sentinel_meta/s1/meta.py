import re
import os.path
import datetime
import logging
import warnings

import lxml.etree

from . import metafile
from .. import converters

logger = logging.getLogger('sentinel_meta.s1.meta')


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
        raise ValueError('Could not find dates if format \'{}\' '
                'in file name \'{}\'.'.format(fmt, fname))
    return [datetime.datetime.strptime(d, fmt) for d in dd]


def get_platform_name(fname):
    fname = os.path.basename(fname)
    try:
        return re.match('(^S\d[AB])', fname).group()
    except AttributeError:
        raise ValueError('Unable to get platform name from fname \'{}.\''.format(fname))


def get_product_date(fname):
    """Product date is the first date in file name"""
    return dates_from_fname(fname)[0].date()


def xml_get_relativeOrbitNumber(root):
    start = int(converters.get_single(root, 'safe:relativeOrbitNumber[@type=\'start\']'))
    stop = int(converters.get_single(root, 'safe:relativeOrbitNumber[@type=\'stop\']'))
    if start != stop:
        warnings.warn('relativeOrbitNumber range from {} to {}. Only returning {}'.format(start, stop, start))
    return start


def get_orbit_number(infile):
    metadata = find_parse_metadata(infile)
    return metadata['orbitNumber']


def parse_metadata(metadatafile=None, metadatastr=None):
    if metadatafile:
        root = lxml.etree.parse(metadatafile).getroot()
    elif metadatastr:
        root = lxml.etree.fromstring(metadatastr)
    else:
        raise ValueError('Either metadatafile or metadatastr must be specified.')
    metadata = {
            'footPrint': converters.get_single_polygon(root, 'gml:coordinates'),
            'relativeOrbitNumber': xml_get_relativeOrbitNumber(root),
            'startTime': converters.get_single_date(root, 'safe:startTime'),
            'stopTime': converters.get_single_date(root, 'safe:stopTime'),
            'resource_name': converters.get_instance(root, 'safe:resource', 'name'),
            'productType': converters.get_single(root, 's1sarl1:productType'),
            'polarizations': converters.get_all(root, 's1sarl1:transmitterReceiverPolarisation')}
    metadata['platform'] = get_platform_name(metadata['resource_name'])
    return metadata


def find_parse_metadata(infile):
    """Find and parse manifest in SAFE or zip file"""
    if infile.endswith('.SAFE'):
        mstr = metafile.read_manifest_SAFE(infile)
    elif infile.endswith('.zip'):
        mstr = metafile.read_manifest_ZIP(infile)
    return parse_metadata(metadatastr=mstr)
