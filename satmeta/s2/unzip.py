import os
import glob
import zipfile
import fnmatch
import logging

logger = logging.getLogger(__name__)


def unzip(infile, outdir):
    with zipfile.ZipFile(infile) as zipf:
        zipf.extractall(path=outdir)


def get_band_string(band):
    try:
        # band is integer
        return 'B{:02d}'.format(band)
    except ValueError:
        return 'B{}'.format(band)


def get_band_fnpattern(band, tile=None):
    bandstr = get_band_string(band)
    fnpattern = '*_{band}.jp2'.format(band=bandstr)
    if tile is not None:
        tile = tile.lstrip('T')
        fnpattern = '*T{tile}'.format(tile=tile) + fnpattern
    return fnpattern


def find_band_file_unzipped_SAFE(folder, band, tile=None):
    """Find band files in unzipped SAFE folder

    Parameters
    ----------
    folder : str
        path to unzipped SAFE product
    band : int or str
        band name
    tile : str, optional
        tile for multi-tile products

    Returns
    -------
    str : path to matching band file
    """
    fnpattern = get_band_fnpattern(band, tile=tile)
    if tile is None:
        granule_folder_pattern = '*'
    else:
        granule_folder_pattern = '*{}*'.format(tile)
    pattern = os.path.join(folder, 'GRANULE', granule_folder_pattern, 'IMG_DATA', fnpattern)
    try:
        files = glob.glob(pattern)
        if len(files) > 1:
            raise ValueError(
                    'Found more than one matching file: {}. Specify `tile`.'
                    .format(files))
        return files[0]
    except IndexError:
        raise RuntimeError(
                'Unable to find file for band {} (and tile {}) in folder \'{}\'.'
                ''.format(band, tile, folder))


def find_band_file_in_archive(names, band, tile=None):
    fnpattern = get_band_fnpattern(band, tile=tile)
    pattern = '*IMG_DATA/' + fnpattern
    try:
        files = list(fnmatch.filter(names, pattern))
        if len(files) > 1:
            raise ValueError(
                    'Found more than one matching file: {}. Specify `tile`.'
                    .format(files))
        return files[0]
    except IndexError:
        raise RuntimeError(
                'Unable to find file for band {} and tile {} in list {}'
                ''.format(band, tile, names))


def get_names_in_file(infile):
    with zipfile.ZipFile(infile) as zipf:
        return zipf.namelist()


def generate_member_url(infile, memberpath):
    return 'zip://' + infile + '!/' + memberpath.lstrip('/')


def get_bandfile_urls(infile, bands, tile=None):
    """Get URLs to band files in ZIP archive

    Parameters
    ----------
    infile : str
        path to .zip file
    bands : list of str
        bands to get
    tile : str, optional
        tile to get bands from
        required for old format multi-tile products
    """
    names = get_names_in_file(infile)
    urls = []
    for band in bands:
        bfpath = find_band_file_in_archive(names, band=band, tile=tile)
        url = generate_member_url(infile, bfpath)
        urls.append(url)
    return urls
