import os
import shutil
import tempfile

from satmeta.l8 import metafile as l8metafile

from .data import TESTDATA

INFILE_TAR = TESTDATA['tar.gz']


def test_read_metafile_TAR():
    mstr = l8metafile.read_metafile_TAR(INFILE_TAR)
    assert b'LANDSAT' in mstr


def test_extract_metafile():
    tempdir = tempfile.mkdtemp()
    try:
        outfile = os.path.join(tempdir, 'MTL.txt')
        l8metafile.extract_metafile(INFILE_TAR, outfile)
        assert os.path.isfile(outfile)
    finally:
        try:
            shutil.rmtree(tempdir)
        except OSError:
            pass
