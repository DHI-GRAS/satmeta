import shapely.geometry

from satmeta.l8 import parser as l8parser
from satmeta import COMMON_KEYS

from .data import TESTDATA

INFILE_TXT = TESTDATA['MTL']


def test_parse_metadata():
    with open(INFILE_TXT) as fin:
        metadata = l8parser.parse_metadata(lines=fin)
    assert isinstance(metadata, dict)
    assert 'row' in metadata
    assert isinstance(metadata['row'], int)


def test_common_keys():
    with open(INFILE_TXT) as fin:
        metadata = l8parser.parse_metadata(lines=fin)
    missing = (set(COMMON_KEYS) - set(metadata))
    assert not missing


def test_footprint():
    with open(INFILE_TXT) as fin:
        metadata = l8parser.parse_metadata(lines=fin)
    assert isinstance(metadata['footprint'], shapely.geometry.Polygon)
    assert isinstance(metadata['footprint_projected'], shapely.geometry.Polygon)
