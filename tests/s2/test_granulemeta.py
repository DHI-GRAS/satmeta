import satmeta.s2.meta as s2meta

from .data import test_data


def test_image_shape():
    infile = test_data['new']['granule_xml']
    meta = s2meta.parse_granule_metadata(infile)
    assert meta['image_shape'][10] == [10980, 10980]
