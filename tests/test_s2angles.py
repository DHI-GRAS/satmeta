import pytest

import satmeta.s2.angles as s2angles
from satmeta import converters

from .data.s2 import test_data

try:
    import rasterio
    no_rasterio = False
except ImportError:
    no_rasterio = True
    pytestmark = pytest.mark.skipif(
            no_rasterio, reason='rasterio not available')


def test_parse_angles_keys():
    infile = test_data['new']['granule_xml']
    adict = s2angles.parse_angles(infile)
    assert set(adict) == {'Sun', 'Viewing_Incidence'}
    assert set(adict['Sun']) == {'Zenith', 'Azimuth'}
    assert adict['Sun']['Zenith'].any()


def test_parse_angles_shape():
    infile = test_data['old']['granule_xml']
    adict = s2angles.parse_angles(infile)
    assert adict['Sun']['Zenith'].shape == (23, 23)


def test_get_angles_with_gref():
    import rasterio.crs
    import affine
    infile = test_data['new']['granule_xml']
    root = converters.get_root(infile)
    group = s2angles.generate_group_name(
            angle='Sun', angle_dir='Zenith', bandId=0)
    angles, transform, crs = s2angles.get_angles_with_gref(
            root, group, meta=None)
    assert angles.shape == (23, 23)
    assert angles.any()
    assert isinstance(transform, affine.Affine)
    assert isinstance(crs, rasterio.crs.CRS)


def test_parse_resample_angles():
    infile = test_data['new']['granule_xml']
    adict = s2angles.parse_resample_angles(
            infile, dst_res=60,
            angles=['Sun'], angle_dirs=['Zenith'])
    a = adict['Sun']['Zenith']
    assert a.shape == (1830, 1830)
    assert a.any()
