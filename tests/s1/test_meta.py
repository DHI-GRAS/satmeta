import pytest

EXPECTED_KEYS = [
        'title',
        'footprint',
        'relative_orbit_number',
        'sensing_start',
        'sensing_end',
        'product_type',
        'polarizations',
        'passdir']


def test_find_manifest_in_SAFE(safe_unzipped):
    import satmeta.s1.metafile as s1metafile
    s1metafile.find_manifest_in_SAFE(safe_unzipped)


def test_read_manifest_SAFE(safe_unzipped):
    import satmeta.s1.metafile as s1metafile
    content = s1metafile.read_manifest_SAFE(safe_unzipped)
    assert bool(content)


def test_parse_metadata(manifest):
    import satmeta.s1.meta as s1meta
    meta = s1meta.parse_metadata(metadatafile=manifest)
    assert isinstance(meta, dict)


def test_find_parse_metadata_zip(safe_zip):
    import satmeta.s1.meta as s1meta
    meta = s1meta.find_parse_metadata(safe_zip)
    assert isinstance(meta, dict)


def test_meta_keys(manifest):
    import satmeta.s1.meta as s1meta
    meta = s1meta.parse_metadata(metadatafile=manifest)
    for key in EXPECTED_KEYS:
        assert key in meta


def test_spacecraft(manifest):
    import satmeta.s1.meta as s1meta
    meta = s1meta.parse_metadata(metadatafile=manifest)
    assert 'spacecraft' in meta


def test_find_parse_metadata_fail():
    import satmeta.s1.meta as s1meta
    with pytest.raises(ValueError):
        s1meta.find_parse_metadata('/some/random/thing')
