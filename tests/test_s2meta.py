import sentinel_meta.s2.meta as s2meta

from .data.s2 import test_data
from .data.s2 import test_tile_ID


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


def test_sensor_ID():
    for key in ['new', 'old']:
        for fmt in ['SAFE', 'zip']:
            infile = test_data[key][fmt]
            meta = s2meta.find_parse_metadata(infile, check_granules=True)
            assert meta['sensor_ID'] == 'S2A'
