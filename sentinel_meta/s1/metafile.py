import os
import glob
import zipfile
import posixpath
import logging

from ..exceptions import MetaDataError

logger = logging.getLogger(__name__)


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
