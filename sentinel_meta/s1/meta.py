import re
import glob
import os.path
import datetime
import zipfile
import posixpath
import logging
from collections import defaultdict
from collections import OrderedDict

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


def read_manifest_SAFE(inSAFE):
    pattern = os.path.join(inSAFE, 'manifest.safe')
    try:
        manifest = glob.glob(pattern)[0]
    except IndexError:
        raise ValueError('No manifest file found by searching for \'{}\'.'
                ''.format(pattern))
    with open(manifest) as f:
        return f.read().split('\n')


def read_manifest_ZIP(zipfilepath):
    try:
        with zipfile.ZipFile(zipfilepath) as zf:
            SAFEdir = zf.namelist()[0]
            manifest = posixpath.join(SAFEdir, 'manifest.safe')
            return zf.open(manifest).read().split('\n')
    except zipfile.BadZipfile as e:
        raise MetaDataError('Unable to read zip file \'{}\': {}'.format(zipfilepath, str(e)))


def get_orbit_number(infile):
    if infile.endswith('.SAFE'):
        lines = read_manifest_SAFE(infile)
    elif infile.endswith('.zip'):
        lines = read_manifest_ZIP(infile)
    return find_orbit_number(lines)


def find_orbit_number(manifestlines):
    pattern = "\s*<safe:relativeOrbitNumber type=\"start\">(.*)<\/safe:relativeOrbitNumber>"
    for line in manifestlines:
        match = re.match(pattern, line)
        if match:
            return int(match.group(1))
    raise ValueError('No orbit number found in manifest.')


def find_date_groups(infiles):
    """Group files by date (ignoring time)"""
    date_groups = defaultdict(list)
    for fname in sorted(infiles):
        date = dates_from_fname(fname)[0].date()
        date_groups[date].append(fname)
    return OrderedDict(sorted(date_groups.items()))


def get_platform_name(fname):
    fname = os.path.basename(fname)
    try:
        return re.match('(^S\d[AB])', fname).group()
    except AttributeError:
        raise ValueError('Unable to get platform name from fname \'{}.\''.format(fname))


def get_product_date(fname):
    """Product date is the first date in file name"""
    return dates_from_fname(fname)[0].date()
