import os

import pytest

from satmeta.pleiades import metafile
from .data import PRODUCT_DIR


def test_find_metafile_in_folder():
    mpath = metafile.find_metafile_in_folder(PRODUCT_DIR)
    assert os.path.isfile(mpath)


def test_find_metafile_in_folder_fails():
    bad_dir = os.path.basename(PRODUCT_DIR)
    with pytest.raises(ValueError):
        metafile.find_metafile_in_folder(bad_dir)
