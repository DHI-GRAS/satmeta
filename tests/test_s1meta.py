import sentinel_meta.s1.meta as s1meta
import sentinel_meta.s1.metafile as s1metafile

from .data.s1 import test_data


def test_find_manifest_in_SAFE():
    s1metafile.find_manifest_in_SAFE(test_data['SAFE'])


def test_read_manifest_SAFE():
    content = s1metafile.read_manifest_SAFE(test_data['SAFE'])
    assert bool(content)


def test_parse_manifest():
    meta = s1meta.parse_manifest(manifestfile=test_data['manifest'])
    assert isinstance(meta, dict)


def test_find_parse_manifest_zip():
    meta = s1meta.find_parse_manifest(test_data['zip'])
    assert isinstance(meta, dict)
