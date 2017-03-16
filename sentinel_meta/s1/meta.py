import re
import glob
import os.path
import datetime
import zipfile
import posixpath
import logging
import warnings

import lxml.etree

from .. import converters

logger = logging.getLogger('sentinel_meta.s1.meta')


class MetaDataError(Exception):
    pass


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


def find_manifest_in_SAFE(inSAFE):
    """Find manifest in SAFE folder"""
    pattern = os.path.join(inSAFE, 'manifest.safe')
    try:
        return glob.glob(pattern)[0]
    except IndexError:
        raise ValueError('No manifest file found by searching for \'{}\'.'
                ''.format(pattern))


def read_manifest_SAFE(inSAFE):
    """Find and read manifest file in SAFE folder"""
    manifest = find_manifest_in_SAFE(inSAFE)
    with open(manifest) as f:
        return f.read()


def read_manifest_ZIP(zipfilepath):
    try:
        with zipfile.ZipFile(zipfilepath) as zf:
            SAFEdir = zf.namelist()[0]
            manifest = posixpath.join(SAFEdir, 'manifest.safe')
            return zf.open(manifest).read()
    except zipfile.BadZipfile as e:
        raise MetaDataError('Unable to read zip file \'{}\': {}'.format(zipfilepath, str(e)))


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


def parse_manifest(manifestfile=None, manifeststr=None):
    if manifestfile:
        root = lxml.etree.parse(manifestfile)
    elif manifeststr:
        root = lxml.etree.fromstring(manifeststr)
    else:
        raise ValueError('Either manifestfile or manifeststr must be specified.')
    metadata = {
            'footPrint': converters.get_single_polygon(root, 'gml:coordinates'),
            'relativeOrbitNumber': xml_get_relativeOrbitNumber(root),
            'startTime': converters.get_single_date(root, 'safe:startTime'),
            'stopTime': converters.get_single_date(root, 'safe:stopTime'),
            'resource_name': converters.get_single(root, 'safe:resource', 'name'),
            'productType': converters.get_single(root, 's1sarl1:productType'),
            'polarizations': converters.get_all(root, 's1sarl1:transmitterReceiverPolarisation')}
    metadata['platform'] = get_platform_name(metadata['resource_name'])
    return metadata


def find_parse_manifest(infile):
    if infile.endswith('.SAFE'):
        mstr = read_manifest_SAFE(infile)
    elif infile.endswith('.zip'):
        mstr = read_manifest_ZIP(infile)
    return parse_manifest(manifeststr=mstr)


def get_orbit_number(infile):
    metadata = find_parse_manifest(infile)
    return metadata['orbitNumber']
