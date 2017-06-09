import satmeta.s1.meta as s1meta
import satmeta.s1.metafile as s1metafile

from .data.s1 import test_data


def test_find_manifest_in_SAFE():
    s1metafile.find_manifest_in_SAFE(test_data['SAFE'])


def test_read_manifest_SAFE():
    content = s1metafile.read_manifest_SAFE(test_data['SAFE'])
    assert bool(content)


def test_parse_metadata():
    meta = s1meta.parse_metadata(metadatafile=test_data['manifest'])
    assert isinstance(meta, dict)


def test_find_parse_metadata_zip():
    meta = s1meta.find_parse_metadata(test_data['zip'])
    assert isinstance(meta, dict)


def test_meta_keys():
    meta = s1meta.parse_metadata(metadatafile=test_data['manifest'])
    for key in ['pass']:
        assert key in meta
