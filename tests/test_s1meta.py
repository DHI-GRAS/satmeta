import os

import sentinel_meta.s1.meta as s1meta

testdatadir = os.path.join(os.path.dirname(__file__), 'data', 's1')

testSAFE = os.path.join(testdatadir, 'SAFE_with_manifest', 'S1A_IW_GRDH_1SDV_20160114T053940_20160114T054005_009486_00DC3C_4695.SAFE')

testmanifest = os.path.join(testSAFE, 'manifest.safe')


def test_find_manifest_in_SAFE():
    s1meta.find_manifest_in_SAFE(testSAFE)


def test_read_manifest_SAFE():
    content = s1meta.read_manifest_SAFE(testSAFE)
    assert bool(content)


def test_parse_manifest():
    meta = s1meta.parse_manifest(manifestfile=testmanifest)
    assert isinstance(meta, dict)
