import os
import re
import glob
import shutil
import zipfile
import logging

from ..exceptions import MetaDataError

logger = logging.getLogger(__name__)


def _ensure_str(s):
    try:
        return s.decode('utf-8')
    except AttributeError:
        return s


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
        mstr = f.read()
    return _ensure_str(mstr)


def find_metafile_in_zip(names):
    compiled_pattern = re.compile(r'[\w_\.]*?\.SAFE/[\w_\.]*?\.xml')

    def _filterfunc(s):
        return compiled_pattern.match(s) and 'INSPIRE' not in s

    try:
        return list(filter(_filterfunc, names))[0]
    except IndexError:
        raise RuntimeError('No metadata file found among zip file names.')


def read_metafile_ZIP(zipfilepath):
    """Find and read metadata file in zip file

    Parameters
    ----------
    zipfilepath : str
        path to zip file

    Returns
    -------
    str
        metadata as string
    """
    try:
        with zipfile.ZipFile(zipfilepath) as zf:
            metafile = find_metafile_in_zip(zf.namelist())
            mstr = zf.open(metafile).read()
            return _ensure_str(mstr)
    except zipfile.BadZipfile as e:
        raise MetaDataError('Unable to read zip file \'{}\': {}'.format(zipfilepath, e))


def find_read_metafile(input_path):
    """Find and read metadata file in input file (SAFE or ZIP)

    Parameters
    ----------
    input_path : str
        path to input file or folder

    Returns
    -------
    str
        metadata as string
    """
    if os.path.isdir(input_path):
        return read_metafile_SAFE(input_path)
    else:
        return read_metafile_ZIP(input_path)


def find_granule_metafiles_in_SAFE(inSAFE, tile_glob_pattern='*', tile_name=None):
    """Find granule metadata files in SAFE

    Paramters
    ---------
    inSAFE : str
        path to .SAFE folder
    tile_glob_pattern : str, optional
        granule glob search pattern
        e.g. '32???'
    tile_name : str, optional
        granule name
        e.g. '32UPF'
        overrides tile_glob_pattern

    Returns
    -------
    list of str
        paths to granule metadata files
    """
    if tile_name is not None:
        tile_glob_pattern = tile_name
    tile_glob_pattern = '*_T{}*'.format(tile_glob_pattern.upper().lstrip('T'))
    pattern = os.path.join(inSAFE, 'GRANULE', tile_glob_pattern, '*.xml')
    return sorted(glob.glob(pattern))


def find_granule_metafiles_in_zip_names(names, tile_regex='', tile_name=None):
    """Find granule metadata files in SAFE

    Paramters
    ---------
    inSAFE : str
        path to .SAFE folder
    tile_regex : str, optional
        granule search pattern
        e.g. '32[A-Z]{3}'
    tile_name : str, optional
        granule name
        e.g. '32UPF'
        overrides tile_glob_pattern

    Returns
    -------
    list of str
        paths of members in zipfile
    """
    if tile_name is not None:
        tile_regex = 'T{}'.format(tile_name.upper().lstrip('T'))
    """Find granule metafiles in list of zip member namers"""
    pattern = (
            r'([\w_\.]*?\.SAFE)/GRANULE/([\w_\.]*?)' +
            tile_regex +
            r'([\w_\.]*?)/([\w_\.]*?\.xml)')
    compiled_pattern = re.compile(pattern)

    def _filterfunc(s):
        return compiled_pattern.match(s) is not None

    members = list(filter(_filterfunc, names))
    if not members:
        raise ValueError(
                'No granule metadata files found in \'{}\' with tile pattern \'{}\'.'
                .format(names, tile_regex))
    return members


def find_read_granule_metafiles_ZIP(zipfilepath, **findkwargs):
    """Read granule metadata files in ZIP archive

    Parameters
    ----------
    zipfilepath : str
        path to zip file
    **findkwargs : additional keyword arguments
        passed to find_granule_metafiles_in_zip_names

    Yields
    ------
    str
        metadata file contents as string
    """
    try:
        with zipfile.ZipFile(zipfilepath) as zf:
            names = zf.namelist()
            metafiles = find_granule_metafiles_in_zip_names(names, **findkwargs)
            logger.debug('Found %d granule metadata files.', len(metafiles))
            for metafile in metafiles:
                mstr = zf.open(metafile).read()
                yield _ensure_str(mstr)
    except zipfile.BadZipfile as e:
        raise MetaDataError('Unable to read zip file \'{}\': {}'.format(zipfilepath, str(e)))


def find_read_granule_metafiles(input_path, tile_name=None, **findkwargs):
    """Find and read granule metadata files in ZIP or SAFE

    Parameters
    ----------
    input_path : str
        path to SAFE folder or ZIP file
    tile_name : str
        tile name
    **findkwargs : additional keyword arguments
        passed to find_granule_metafiles_in_zip_names
        or find_granule_metafiles_in_SAFE

    Yields
    ------
    str
        metadata file contents as string
    """
    if os.path.isdir(input_path):
        for fn in find_granule_metafiles_in_SAFE(
                input_path, tile_name=tile_name, **findkwargs):
            with open(fn) as fin:
                mstr = fin.read()
            yield _ensure_str(mstr)
    else:
        for mstr in find_read_granule_metafiles_ZIP(
                input_path, tile_name=tile_name, **findkwargs):
            yield _ensure_str(mstr)


def extract_metafile(input_path, outfile):
    """Extract and save metadata file"""
    mstr = find_read_metafile(input_path)
    with open(outfile, 'w') as fout:
        fout.write(mstr)


def extract_single_granule_metafile(input_path, outfile, tile_name):
    """Extract and save single granule metadata file"""
    try:
        mstr = list(find_read_granule_metafiles(input_path, tile_name=tile_name))[0]
    except IndexError:
        raise ValueError(
                'No granule metadata file found in \'{}\' '
                'for tile name \'{}\'.'.format(input_path, tile_name))
    with open(outfile, 'w') as fout:
        fout.write(mstr)


def extract_granule_metafiles_ZIP(zipfilepath, outdir, tile_name=None, **findkwargs):
    """Extract granule metafiles from ZIP archive

    Parameters
    ----------
    zipfilepath : str
        path to zip file
    outdir : str
        path to output directory
    tile_name : str
        tile name
    **findkwargs : additional keyword arguments
        passed to find_granule_metafiles_in_zip_names
        or find_granule_metafiles_in_SAFE
    """
    with zipfile.ZipFile(zipfilepath) as zf:
        names = zf.namelist()
        members = find_granule_metafiles_in_zip_names(
                names, tile_name=tile_name, **findkwargs)
        logger.debug(members)
        for member in members:
            outfile = os.path.join(outdir, os.path.basename(member))
            source = zf.open(member)
            destination = open(outfile, 'wb')
            with source, destination:
                shutil.copyfileobj(source, destination)


def extract_all_granule_metafiles(input_path, outdir, tile_name=None, **findkwargs):
    """Extract granule metafiles from ZIP archive or SAFE folder

    Parameters
    ----------
    input_path : str
        path to zip file
    outdir : str
        path to output directory
    tile_name : str
        tile name
    **findkwargs : additional keyword arguments
        passed to find_granule_metafiles_in_zip_names
        or find_granule_metafiles_in_SAFE
    """
    if os.path.isdir(input_path):
        fns = find_granule_metafiles_in_SAFE(
                input_path, tile_name=tile_name, **findkwargs)
        for fn in fns:
            shutil.copy(fn, outdir)
    else:
        extract_granule_metafiles_ZIP(input_path, outdir, tile_name=tile_name, **findkwargs)
