from satmeta.pleiades import meta as plmeta

from .data import PRODUCT_DIR
from .data import DIM_XML


def test_find_parse_metadata_folder():
    metadata = plmeta.find_parse_metadata(PRODUCT_DIR)
    assert isinstance(metadata, dict)


def test_find_parse_metadata_file():
    metadata = plmeta.find_parse_metadata(DIM_XML)
    assert isinstance(metadata, dict)
