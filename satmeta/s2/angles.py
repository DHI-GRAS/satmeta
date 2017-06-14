import posixpath
from collections import defaultdict

import numpy as np
import rasterio.crs

from . import meta as s2meta
from . import utils as s2utils

from satmeta import converters


angles_tags = {
        'Viewing_Incidence': 'Viewing_Incidence_Angles_Grids[@bandId="0"]/',
        'Sun': 'Sun_Angles_Grid/'}

_all_angles = ['Viewing_Incidence', 'Sun']
_all_dirs = ['Zenith', 'Azimuth']


def get_res(root, group):
    res = {}
    for s in ['COL_STEP', 'ROW_STEP']:
        tagname = posixpath.join(group, s)
        res[s] = converters.get_instance(
                root, tagname, index=0, to_type=int)
    return res


def get_values(root, group):
    tagname = posixpath.join(group, 'Values_List/VALUES')

    def _to_type(s):
        return np.array(s.split(' '), 'f4')

    vv = converters.get_all(root, tagname, to_type=_to_type)
    values2d = np.vstack(vv)  # rows, cols
    return values2d


def resample_angles(angles,
                    src_transform,
                    src_crs,
                    dst_shape,
                    dst_transform=None,
                    dst_crs=None,
                    resampling=None):
    """Resample angles

    Parameters
    ----------
    angles : ndarray
        angles data
    src_transform : affine.Affine
        source transformation
    src_crs : dict or rasterio.crs.CRS
        source coordinate reference system
    dst_shape : tuple
        output shape
    dst_transform : affine.Affine, optional
        destination transform
        default: same as src_transform
    dst_crs : dict or rasterio.crs.CRS, optional
        destination coordinate reference system
        default: same as src_crs
    resampling : int
        resampling method from rasterio.warp.Resampling
        default: bilinear

    Returns
    -------
    ndarray : resampled angles
    """
    import rasterio.warp

    if dst_transform is None:
        dst_transform = src_transform
    if dst_crs is None:
        dst_crs = src_crs

    if resampling is None:
        resampling = rasterio.warp.Resampling.bilinear

    destination = np.zeros(dst_shape, 'f8')
    rasterio.warp.reproject(
        source=angles,
        destination=destination,
        src_transform=src_transform,
        src_crs=src_crs,
        dst_transform=dst_transform,
        dst_crs=dst_crs,
        resampling=resampling)

    return destination


def get_resample_angles(root, group, dst_res=None,
        dst_transform=None, dst_crs=None, dst_shape=None,
        meta=None):
    """Parse angles and resample to dst_res

    Parameters
    ----------
    root : lxml root
        root of granule metadata XML doc
    group : str
        path to angles tag
    dst_res : int
        target resolution

    """
    import rasterio.crs
    import rasterio.warp

    if meta is None:
        meta = s2meta.parse_granule_metadata_xml(root)
    angles_raw, src_transform, src_crs = get_angles(root, group, meta=meta)

    if dst_res is not None:
        try:
            dst_transform = meta['image_transform'][dst_res]
            dst_shape = meta['image_shape'][dst_res]
            dst_crs = src_crs
        except KeyError:
            raise ValueError(
                    'You must either specify `dst_crs` and '
                    '`dst_transform` or choose a predefined resolution ({}).'
                    ''.format(s2meta._all_res))

    if dst_crs is None:
        dst_crs = src_crs
    elif dst_crs != src_crs:
        # compute new transform and shape
        src_bounds = converters.trans_shape_to_bounds(
                src_transform, angles_raw.shape)
        src_width, src_height = angles_raw.shape
        dst_transform, dst_width, dst_height = (
                rasterio.warp.calculate_default_transform(
                    src_crs, dst_crs, src_width, src_height,
                    *src_bounds))
        dst_shape = (dst_width, dst_height)

    if dst_transform is None and dst_shape is None:
        # default: unchanged
        dst_transform = src_transform
        dst_shape = angles_raw.shape
    elif dst_transform is None or dst_shape is None:
        raise ValueError(
                '`dst_transform` and `dst_shape` '
                'must both be specified.')

    return resample_angles(
            angles_raw,
            src_transform=src_transform,
            src_crs=src_crs,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            dst_shape=dst_shape)


def generate_group_name(angle, angle_dir):
    return posixpath.join(angles_tags[angle], angle_dir)


def get_angles(root, group, meta=None):
    """Get the angles data

    Parameters
    ----------
    root : lxml root
        GRANULE XML doc root
    group : str
        path to angles tag
    meta : dict, optional
        granule meta data already
        parsed with s2meta

    Returns
    -------
    data, transform, CRS
    """
    if meta is None:
        meta = s2meta.parse_granule_metadata_xml(root)
    pos = meta['image_geoposition'][10]
    # assume that the CRS of the angles is the same as image CRS
    src_crs = rasterio.crs.CRS({'init': meta['projection']})
    res = get_res(root, group)
    src_transform = s2utils.res_pos_to_affine(res, pos)
    angles_raw = get_values(root, group)
    return angles_raw, src_transform, src_crs


def parse_angles(
        metadatafile=None, metadatastr=None,
        angles=_all_angles,
        angle_dirs=_all_dirs):
    """Parse angles from GRANULE metadata

    Parameters
    ----------
    metadatafile : str, optional
        path to metadata file
    metadatastr : str, optional
        metadata string
    angles : list of str
        angles to parse
        subset of _all_angles
    angle_dirs : list of str
        angle diretions
        subset of _all_dirs

    Returns
    -------
    ndarray : angles
    """
    root = converters.get_root(metadatafile, metadatastr)
    meta = s2meta.parse_granule_metadata_xml(root)

    angles_data = defaultdict(dict)
    for angle in angles:
        for angle_dir in angle_dirs:
            group = generate_group_name(angle, angle_dir)
            angles_data[angle][angle_dir], _, _ = (
                    get_angles(root, group, meta=meta))
    return angles_data


def parse_resample_angles(
        metadatafile=None, metadatastr=None,
        angles=_all_angles,
        angle_dirs=_all_dirs,
        **kwargs):
    """Parse angles from GRANULE metadata and resample

    Parameters
    ----------
    metadatafile : str, optional
        path to metadata file
    metadatastr : str, optional
        metadata string
    angles : list of str
        angles to parse
        subset of _all_angles
    angle_dirs : list of str
        angle diretions
        subset of _all_dirs
    **kwargs : additional keyword arguments
        passed to `get_resample_angles`

    Returns
    -------
    ndarray : angles
    """
    root = converters.get_root(metadatafile, metadatastr)
    meta = s2meta.parse_granule_metadata_xml(root)

    angles_data = defaultdict(dict)
    for angle in angles:
        for angle_dir in angle_dirs:
            group = generate_group_name(angle, angle_dir)
            angles_data[angle][angle_dir] = get_resample_angles(
                    root, group, meta=meta, **kwargs)
    return angles_data
