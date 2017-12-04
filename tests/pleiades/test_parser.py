from satmeta.pleiades import parser
from satmeta import COMMON_KEYS

from .data import DIM_XML


def test_parse_metadata():
    metadata = parser.parse_metadata(DIM_XML)
    assert isinstance(metadata, dict)


def test_common_keys():
    metadata = parser.parse_metadata(DIM_XML)
    missing = (set(COMMON_KEYS) - set(metadata))
    assert not missing


def test_footprint():
    metadata = parser.parse_metadata(DIM_XML)
    assert metadata['footprint'].is_valid
