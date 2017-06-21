import os
import re
import glob
import zipfile
import logging

from ..exceptions import MetaDataError

logger = logging.getLogger(__name__)


def find_metafile_in_SAFE(inSAFE):
    """Find metafile in SAFE folder"""
    def _filterfunc(fn):
        return 'INSPIRE' not in os.path.basename(fn)
    pattern = os.path.join(inSAFE, '*.xml')
    try:
        names = glob.glob(pattern)
        return list(filter(_filterfunc, names))[0]
    except IndexError:
        raise ValueError('No metafile file found in folder \'{}\''.format(inSAFE))


def read_metafile_SAFE(inSAFE):
    """Find and read metafile file in SAFE folder"""
    metafile = find_metafile_in_SAFE(inSAFE)
    with open(metafile) as f:
        return f.read()


def find_metafile_in_zip(names):
    def _filterfunc(s):
        return re.match('[\w_\.]*?\.SAFE/[\w_\.]*?\.xml', s) and 'INSPIRE' not in s
    try:
        return list(filter(_filterfunc, names))[0]
    except IndexError:
        raise RuntimeError('No metadata file found among zip file names.')


def read_metafile_ZIP(zipfilepath):
    try:
        with zipfile.ZipFile(zipfilepath) as zf:
            metafile = find_metafile_in_zip(zf.namelist())
            return zf.open(metafile).read()
    except zipfile.BadZipfile as e:
        raise MetaDataError('Unable to read zip file \'{}\': {}'.format(zipfilepath, str(e)))


def find_read_metafile(input_path):
    if os.path.isdir(input_path):
        return read_metafile_SAFE(input_path)
    else:
        return read_metafile_ZIP(input_path)


def find_granule_metafiles_in_SAFE(inSAFE):
    pattern = os.path.join(inSAFE, 'GRANULE', '*', '*.xml')
    return sorted(glob.glob(pattern))


def _granule_metafiles_in_zip_names(names):
    """Find granule metafiles in list of zip member namers"""
    def _filterfunc(s):
        return re.match('([\w_\.]*?\.SAFE)/(GRANULE)/([\w_\.]*?)/([\w_\.]*?\.xml)', s) is not None
    return list(filter(_filterfunc, names))


def read_granule_metafiles_ZIP(zipfilepath):
    try:
        with zipfile.ZipFile(zipfilepath) as zf:
            names = zf.namelist()
            metafiles = _granule_metafiles_in_zip_names(names)
            logger.debug('Found {} granule metadata files.'.format(len(metafiles)))
            for metafile in metafiles:
                yield zf.open(metafile).read()
    except zipfile.BadZipfile as e:
        raise MetaDataError('Unable to read zip file \'{}\': {}'.format(zipfilepath, str(e)))
