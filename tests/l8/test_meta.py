from satmeta.l8 import meta as l8meta

from .data import TESTDATA


def test_find_parse_metadata():
    for path in TESTDATA.values():
        metadata = l8meta.find_parse_metadata(path)
        assert isinstance(metadata, dict)
