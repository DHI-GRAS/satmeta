import os
import glob
import shutil
import tempfile
import logging

import satmeta.s2.metafile as s2metafile

from .data import test_data


def test_find_read_granule_metafiles_ZIP():
    for key in ['new', 'old']:
        infile = test_data[key]['zip']
        str_iter = s2metafile.find_read_granule_metafiles_ZIP(infile)
        mstrs = list(str_iter)
        assert len(mstrs) == 1
        assert b'xml' in mstrs[0]


def test_find_granule_metafiles_in_SAFE():
    for key in ['new', 'old']:
        infile = test_data[key]['SAFE']
        metafiles = s2metafile.find_granule_metafiles_in_SAFE(infile)
        assert len(metafiles) == 1


def test_find_read_granule_metafiles_ZIP_tile_name():
    for key, tile_name in [('new', '33VUC'), ('old', '33UVB')]:
        infile = test_data[key]['zip']
        str_iter = s2metafile.find_read_granule_metafiles_ZIP(infile, tile_name=tile_name)
        mstrs = list(str_iter)
        assert len(mstrs) == 1


def test_extract_all_granule_metafiles():
    for key in ['new', 'old']:
        for fmt in ['zip', 'SAFE']:
            infile = test_data[key][fmt]
            logging.info(infile)
            tempdir = tempfile.mkdtemp()
            try:
                s2metafile.extract_all_granule_metafiles(infile, outdir=tempdir)
                xmlfiles = glob.glob(os.path.join(tempdir, '*.xml'))
                logging.info(xmlfiles)
                assert len(xmlfiles) > 0
            finally:
                try:
                    shutil.rmtree(tempdir)
                except OSError:
                    pass
