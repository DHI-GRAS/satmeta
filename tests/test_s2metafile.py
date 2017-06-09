import satmeta.s2.metafile as s2metafile

from .data.s2 import test_data


def test_read_granule_metafiles_ZIP():
    for key in ['new', 'old']:
        infile = test_data[key]['zip']
        str_iter = s2metafile.read_granule_metafiles_ZIP(infile)
        assert len(list(str_iter)) == 1


def test_find_granule_metafiles_in_SAFE():
    for key in ['new', 'old']:
        infile = test_data[key]['SAFE']
        metafiles = s2metafile.find_granule_metafiles_in_SAFE(infile)
        assert len(metafiles) == 1
