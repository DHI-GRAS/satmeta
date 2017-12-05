import sys

import pytest
import numpy as np

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

skip_python2 = pytest.mark.skipif(sys.version_info < (3, 5),
                                  reason="requires python3.5")

try:
    import scipy
    no_scipy = False
except ImportError:
    no_scipy = True
skip_scipy = pytest.mark.skipif(
        no_scipy, reason='scipy not available')

try:
    from scipy.misc import imresize
    no_imresize = False
except ImportError:
    no_imresize = True
skip_imresize = pytest.mark.skipif(
        no_imresize, reason='imresize not available')

RESAMPLE_TEST_KW = dict(
    dst_res_predefined=60,
    angles=['Sun'],
    angle_dirs=['Zenith'],
    extrapolate=False)


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


@skip_python2
@skip_rasterio
def test_parse_resample_angles_rasterio():
    infile = test_data['new']['granule_xml']
    adict = s2angles2d.parse_resample_angles(
        infile, resample_method='rasterio', **RESAMPLE_TEST_KW)
    a = adict['Sun']['Zenith']
    assert a.shape == (1830, 1830)
    assert a.any()


@skip_scipy
@skip_imresize
def test_parse_resample_angles_imresize():
    infile = test_data['new']['granule_xml']
    adict = s2angles2d.parse_resample_angles(
        infile, resample_method='imresize', **RESAMPLE_TEST_KW)
    a = adict['Sun']['Zenith']
    assert a.shape == (1830, 1830)
    assert a.any()


@skip_scipy
def test_parse_resample_angles_zoom():
    infile = test_data['new']['granule_xml']
    adict = s2angles2d.parse_resample_angles(
        infile, resample_method='zoom', **RESAMPLE_TEST_KW)
    a = adict['Sun']['Zenith']
    assert a.shape == (1830, 1830)
    assert a.any()


@skip_python2
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
            dst_shape=dst_shape,
            extrapolate=False)
    a = adict['Sun']['Zenith']
    assert a.shape == dst_shape


@skip_python2
@skip_rasterio
@skip_scipy
def test_parse_resample_angles_rasterio_extrapolate():
    infile = test_data['new']['granule_xml']
    kw = dict(
        metadatafile=infile,
        dst_res_predefined=60,
        resample_method='rasterio',
        angles=['Viewing_Incidence'],
        angle_dirs=['Zenith'])
    adict = s2angles2d.parse_resample_angles(extrapolate=False, **kw)
    a_noextr = adict['Viewing_Incidence']['Zenith']
    # NaN before
    assert np.any(np.isnan(a_noextr))
    adict = s2angles2d.parse_resample_angles(extrapolate=True, **kw)
    a_extr = adict['Viewing_Incidence']['Zenith']
    # no NaN after
    assert np.all(np.isfinite(a_extr))
