from satmeta.pleiades import meta as plmeta

from . import data


def test_find_parse_metadata_folder():
    metadata = plmeta.find_parse_metadata(data.PRODUCT_DIR)
    assert isinstance(metadata, dict)


def test_find_parse_metadata_file():
    metadata = plmeta.find_parse_metadata(data.DIM_XML)
    assert isinstance(metadata, dict)


def test_find_parse_metadata_file_non_utf():
    metadata = plmeta.find_parse_metadata(data.DIM_XML_NON_UTF)
    assert isinstance(metadata, dict)
