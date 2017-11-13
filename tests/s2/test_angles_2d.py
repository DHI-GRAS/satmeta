import pytest

import satmeta.s2.angles_2d as s2angles2d
from satmeta import converters

from .data import test_data

try:
    import rasterio
    no_rasterio = False
except ImportError:
    no_rasterio = True
skip_rasterio = pytest.mark.skipif(
        no_rasterio, reason='rasterio not available')


try:
    from scipy.misc import imresize
    no_imresize = False
except ImportError:
    no_imresize = True
skip_imresize = pytest.mark.skipif(
        no_imresize, reason='imresize not available')


def test_parse_angles_keys():
    infile = test_data['new']['granule_xml']
    adict = s2angles2d.parse_angles(infile)
    assert set(adict) == {'Sun', 'Viewing_Incidence'}
    assert set(adict['Sun']) == {'Zenith', 'Azimuth'}
    assert adict['Sun']['Zenith'].any()


def test_parse_angles_shape():
    infile = test_data['old']['granule_xml']
    adict = s2angles2d.parse_angles(infile)
    assert adict['Sun']['Zenith'].shape == (23, 23)


def test_get_angles_with_gref():
    import affine
    infile = test_data['new']['granule_xml']
    root = converters.get_root(infile)
    group = s2angles2d._generate_group_name(
            angle='Sun', angle_dir='Zenith', bandId=0)
    angles, transform, crs = s2angles2d._get_angles_with_gref(
            root, group, meta=None)
    assert angles.shape == (23, 23)
    assert angles.any()
    assert isinstance(transform, affine.Affine)
    assert isinstance(crs, dict)


@skip_rasterio
def test_parse_resample_angles_rasterio():
    infile = test_data['new']['granule_xml']
    adict = s2angles2d.parse_resample_angles(
            infile, dst_res=60,
            resample_method='rasterio',
            angles=['Sun'], angle_dirs=['Zenith'])
    a = adict['Sun']['Zenith']
    assert a.shape == (1830, 1830)
    assert a.any()


@skip_imresize
def test_parse_resample_angles_imresize():
    infile = test_data['new']['granule_xml']
    adict = s2angles2d.parse_resample_angles(
            infile, dst_res=60,
            resample_method='imresize',
            angles=['Sun'], angle_dirs=['Zenith'])
    a = adict['Sun']['Zenith']
    assert a.shape == (1830, 1830)
    assert a.any()


@skip_rasterio
def test_parse_resample_angles_rasterio_dst_shape():
    dst_shape = (200, 300)
    dst_transform = None
    infile = test_data['new']['granule_xml']
    adict = s2angles2d.parse_resample_angles(
            infile,
            resample_method='rasterio',
            angles=['Sun'], angle_dirs=['Zenith'],
            dst_transform=dst_transform,
            dst_shape=dst_shape)
    a = adict['Sun']['Zenith']
    assert a.shape == dst_shape
