from satmeta import COMMON_KEYS
import satmeta.s2.meta as s2meta

from .data import test_data
from .data import test_tile_ID


def test_parse_metadata():
    for key in ['new', 'old']:
        infile = test_data[key]['xml']
        meta = s2meta.parse_metadata(infile)
        assert isinstance(meta, dict)


def test_parse_granule_metadata():
    for key in ['new', 'old']:
        infile = test_data[key]['granule_xml']
        meta = s2meta.parse_granule_metadata(infile)
        assert isinstance(meta, dict)


def test_find_parse_granule_metadata():
    for key in ['new', 'old']:
        for fmt in ['SAFE', 'zip']:
            infile = test_data[key][fmt]
            gmeta = s2meta.find_parse_granule_metadata(infile)
            assert isinstance(gmeta, dict)
            assert test_tile_ID[key] in gmeta


def test_find_parse_metadata():
    for key in ['new', 'old']:
        for fmt in ['SAFE', 'zip']:
            infile = test_data[key][fmt]
            meta = s2meta.find_parse_metadata(infile, check_granules=True)
            assert isinstance(meta, dict)
            assert 'granules' in meta
            assert test_tile_ID[key] in meta['granules']


def test_spacecraft():
    for key in ['new', 'old']:
        for fmt in ['SAFE', 'zip']:
            infile = test_data[key][fmt]
            meta = s2meta.find_parse_metadata(infile, check_granules=True)
            assert meta['spacecraft'] == 'S2A'


def test_common():
    for key in ['new', 'old']:
        for fmt in ['SAFE', 'zip']:
            infile = test_data[key][fmt]
            metadata = s2meta.find_parse_metadata(infile, check_granules=True)
            missing = (set(COMMON_KEYS) - set(metadata))
            assert not missing
