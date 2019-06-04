import os
import re
import glob
import zipfile
import posixpath
import fnmatch
import logging

from ..exceptions import MetaDataError

logger = logging.getLogger(__name__)


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
            name = list(fnmatch.filter(zf.namelist(), '*/manifest.safe'))[0]
            return zf.open(name).read()
    except zipfile.BadZipfile as e:
        raise MetaDataError(
            'Unable to read zip file \'{}\': {}'.format(path, str(e))
        ) from e


def _get_swath_polarisation(name):
    try:
        swath, polarisation = re.match(r's1[a-z]-(iw\d?)-.*-(v[vh]).*\.xml', name).groups()
    except AttributeError:
        raise ValueError(f'Unable to find swath and polarisation in name "{name}".')
    return dict(
        polarisation=polarisation.upper(),
        swath=swath.upper()
    )


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
    annotations = {}
    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            pattern = '*/annotation/s1?-iw*-*.xml'
            found = fnmatch.filter(names, pattern)
            if not found:
                raise ValueError(f'No annotations name found with pattern "{pattern}" in {names}.')
            for name in found:
                key = '{polarisation}_{swath}'.format(
                    **_get_swath_polarisation(posixpath.basename(name))
                )
                data = zf.open(name).read()
                annotations[key] = data
    except zipfile.BadZipfile as e:
        raise MetaDataError(
            'Unable to read zip file \'{}\': {}'.format(path, str(e))
        ) from e
    return annotations


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
    pattern = os.path.join(
        path, 'annotation', 's1?-iw*-*.xml'
    )
    found = list(glob.glob(pattern))
    if not found:
        raise ValueError(f'No annotations file found with pattern "{pattern}".')
    annotations = {}
    for path in found:
        key = '{polarisation}_{swath}'.format(
            **_get_swath_polarisation(os.path.basename(path))
        )
        with open(path) as f:
            data = f.read()
        annotations[key] = data
    return annotations
