from satmeta import COMMON_KEYS

from . import data


def test_parse_metadata():
    import satmeta.dg.meta as dgmeta
    for key, imdfile in data.IMDFILES.items():
        sat_id = key.split('_')[0]
        metadata = dgmeta.parse_metadata(imdfile)
        assert 'sensing_time' in metadata
        assert sat_id == metadata['satId']


def test_common_keys():
    import satmeta.dg.meta as dgmeta
    for key, imdfile in data.IMDFILES.items():
        metadata = dgmeta.parse_metadata(imdfile)
        missing = (set(COMMON_KEYS) - set(metadata))
        print(metadata)
        assert not missing
