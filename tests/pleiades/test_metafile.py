import os

from satmeta.pleiades import metafile

from .data import PRODUCT_DIR


def test_find_metafile_in_folder():
    mpath = metafile.find_metafile_in_folder(PRODUCT_DIR)
    assert os.path.isfile(mpath)

