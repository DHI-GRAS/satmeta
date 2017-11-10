import shapely.geometry

from satmeta.l8 import parser as l8parser
from satmeta import COMMON_KEYS

from .data import TESTDATA

INFILE_TXT = TESTDATA['MTL']


def test_parse_metadata():
    with open(INFILE_TXT) as fin:
        metadata = l8parser.parse_metadata(lines=fin)
    assert isinstance(metadata, dict)
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


def test_rescaling():
    with open(INFILE_TXT) as fin:
        metadata = l8parser.parse_metadata(lines=fin)
    rsd = metadata['rescaling']
    assert isinstance(rsd, dict)
    assert set(rsd) == {'RADIANCE', 'REFLECTANCE'}
    assert len(rsd['RADIANCE']['ADD']) == 11
    assert isinstance(rsd['RADIANCE']['MULT'][0], float)
