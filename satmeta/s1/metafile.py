import os
import glob
import zipfile
import posixpath
import fnmatch
import logging

from ..exceptions import MetaDataError

logger = logging.getLogger(__name__)

POLARISATIONS = ['VH', 'VV']


def find_manifest_in_SAFE(path):
    """Find manifest in SAFE folder"""
    pattern = os.path.join(path, 'manifest.safe')
    try:
        return glob.glob(pattern)[0]
    except IndexError:
        raise ValueError(
            'No manifest file found by searching for \'{}\'.'
            .format(pattern)
        )


def read_manifest_SAFE(path):
    """Find and read manifest file in SAFE folder"""
    manifest = find_manifest_in_SAFE(path)
    with open(manifest) as f:
        return f.read()


def read_manifest_ZIP(path):
    """Find and read manifest file in zip file

    Parameters
    ----------
    path : str
        path to zip file

    Returns
    -------
    str
        metadata as string
    """
    try:
        with zipfile.ZipFile(path) as zf:
            SAFEdir = zf.namelist()[0]
            manifest = posixpath.join(SAFEdir, 'manifest.safe')
            return zf.open(manifest).read()
    except zipfile.BadZipfile as e:
        raise MetaDataError(
            'Unable to read zip file \'{}\': {}'.format(path, str(e))
        ) from e


def _find_annotations_names(names):
    found_names = {}
    for polarisation in POLARISATIONS:
        pattern = f'*/annotation/s1?-*-{polarisation.lower()}-*-???.xml'
        found = fnmatch.filter(names, pattern)
        if not found:
            raise ValueError(f'No annotations name found with pattern "{pattern}".')
        elif len(found) == 1:
            found_names[polarisation] = found[0]
        else:
            raise ValueError(f'More than one annotations name found with pattern "{pattern}".')
    return found_names


def read_annotations_ZIP(path):
    """Find and read annotation files in zip file

    Parameters
    ----------
    path : str
        path to zip file

    Returns
    -------
    str
        metadata as string
    """
    try:
        data = {}
        with zipfile.ZipFile(path) as zf:
            annotation_names = _find_annotations_names(zf.namelist())
            for polarisation, zippath in annotation_names.items():
                data[polarisation] = zf.open(zippath).read()
    except zipfile.BadZipfile as e:
        raise MetaDataError(
            'Unable to read zip file \'{}\': {}'.format(path, str(e))
        ) from e
    return data


def read_annotations_SAFE(path):
    """Find and read annotation files in SAFE file

    Parameters
    ----------
    path : str
        path to SAFE file

    Returns
    -------
    str
        metadata as string
    """
    data = {}
    for polarisation in POLARISATIONS:
        pattern = os.path.join(
            path, 'annotations', f'*/annotation/s1?-*-{polarisation.lower()}-*-???.xml'
        )
        found = list(glob.glob(pattern))
        if not found:
            raise ValueError(f'No annotations file found with pattern "{pattern}".')
        elif len(found) == 1:
            with open(found[0]) as f:
                data[polarisation] = f.read()
        else:
            raise ValueError(f'More than one annotations files found with pattern "{pattern}".')
    return data
