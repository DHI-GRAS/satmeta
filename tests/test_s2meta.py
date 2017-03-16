import sentinel_meta.s2.meta as s2meta

from data.s2 import test_data


def test_parse_metadata():
    meta = s2meta.parse_metadata(test_data['xml'])
    assert isinstance(meta, dict)


def test_parse_granule_metadata():
    meta = s2meta.parse_granule_metadata(test_data['granule_xml'])
    assert isinstance(meta, dict)
