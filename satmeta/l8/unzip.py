import os
import glob
import shutil
import tarfile
import fnmatch
import logging

logger = logging.getLogger(__name__)


def unzip(infile, outdir, bands=None):
    try:
        with tarfile.open(infile) as tar:
            tar.extractall(path=outdir)
    except:
        try:
            shutil.rmtree(outdir)
        except OSError:
            pass
        raise


def find_mtl_unzipped(folder):
    try:
        return glob.glob(os.path.join(folder, '*_MTL.txt'))[0]
    except IndexError:
        raise RuntimeError('Unable to find MTL in folder {}.'.format(folder))


def get_band_fnpattern(band):
    return '*_B{}.TIF'.format(band)


def find_band_file_unzipped(folder, band):
    fnpattern = get_band_fnpattern(band)
    pattern = os.path.join(folder, fnpattern)
    try:
        return glob.glob(pattern)[0]
    except IndexError:
        raise RuntimeError('Unable to find file for band {} in folder {}'.format(band, folder))


def find_band_file(names, band):
    fnpattern = get_band_fnpattern(band)
    try:
        return fnmatch.filter(names, fnpattern)[0]
    except IndexError:
        raise RuntimeError('Unable to find file for band {} in list {}'.format(band, names))


def open_band_in_archive(tar, band):
    names = tar.getnames()
    name = find_band_file(names, band)
    logger.debug('Found file {} for band {}.'.format(name, band))
    return tar.extractfile(name)


def open_bandfiles_in_archive(infile, bands):
    with tarfile.open(infile) as tar:
        for band in bands:
            logger.info('Reading band {} from tar file {} ...'.format(band, infile))
            yield open_band_in_archive(tar, band)


def _get_names_in_file(infile):
    with tarfile.open(infile) as tar:
        return tar.getnames()


def generate_member_url(infile, memberpath):
    return 'tar://' + infile + '!/' + memberpath.lstrip('.').lstrip('/')


def get_bandfile_urls(infile, bands):
    """Get URLs to band files in TAR archive

    Parameters
    ----------
    infile : str
        path to .tar(.gz) file
    bands : list of str
        bands to get
    """
    names = _get_names_in_file(infile)
    urls = []
    for band in bands:
        bfpath = find_band_file(names, band=band)
        url = generate_member_url(infile, bfpath)
        urls.append(url)
    return urls
