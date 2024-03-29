from __future__ import division
import posixpath
from collections import defaultdict

import numpy as np

from . import meta as s2meta
from . import utils as s2utils
from .. import utils, converters

ANGLES_TAGS = {
        'Viewing_Incidence': (
            'Viewing_Incidence_Angles_Grids[@bandId="{bandId}"]'),
        'Sun': 'Sun_Angles_Grid'}

ALL_ANGLES = ['Viewing_Incidence', 'Sun']
ALL_DIRS = ['Zenith', 'Azimuth']


def _get_res(root, group):
    """Get resolution from XML root and data group"""
    res = {}
    for s in ['COL_STEP', 'ROW_STEP']:
        tagname = posixpath.join(group, s)
        res[s] = converters.get_instance(
                root, tagname, index=0, to_type=int
        )
    return res


def _get_values(root, group):
    """Get VALUES from group in XML root

    Parameters
    ----------
    root : lxml XML root
        root of XML document
    group : str
        tag name of data
        see `_generate_group_name`
    """
    tagname = posixpath.join(group, 'Values_List/VALUES')

    def _to_type(s):
        return np.array(s.split(' '), 'f4')

    vv = converters.get_all(root, tagname, to_type=_to_type)
    values2d = np.vstack(vv)  # rows, cols
    return values2d


def _get_values_merged_detectors(root, group):
    """Get VALUES from Viewing_Incidence grids and merge them

    Parameters
    ----------
    root : lxml XML root
        root of XML document
    group : str
        tag name of data
        see `_generate_group_name`
    """
    pargroup, child = posixpath.split(group)
    ee = root.findall('.//' + pargroup)

    pargroup_detector = pargroup + '[@detectorId="{detectorId}"]'
    pargroup_detector_fmt = posixpath.join(pargroup_detector, child)

    aa = []
    for e in ee:
        group_detector = pargroup_detector_fmt.format(**e.attrib)
        a = _get_values(root, group_detector)
        aa.append(a)

    a_merged = np.empty_like(aa[0])
    a_merged[:] = np.nan
    for a in aa:
        mask = np.isfinite(a)
        a_merged[mask] = a[mask]

    return a_merged


def _get_angles_any_type(root, group):
    """Common interface for Viewing_Incidence and Sun angles

    Parameters
    ----------
    root : lxml XML root
        root of XML document
    group : str
        tag name of data
        see `_generate_group_name`
    """
    if 'Viewing_Incidence' in group:
        return _get_values_merged_detectors(root, group)
    else:
        return _get_values(root, group)


def _get_angles_with_gref(root, group, meta=None):
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
    data, transform, crs dict
    """
    if meta is None:
        meta = s2meta.parse_granule_metadata_xml(root)
    pos = meta['image_geoposition'][10]
    # assume that the CRS of the angles is the same as image CRS
    src_crs = {'init': meta['projection']}
    res = _get_res(root, group)
    src_transform = s2utils.res_pos_to_affine(res, pos)
    angles_raw = _get_angles_any_type(root, group)
    return angles_raw, src_transform, src_crs


def _extrapolate_nan(a_raw):
    """Fill NaN with bivariate splite fit"""
    import scipy.interpolate
    good = np.isfinite(a_raw)
    if np.all(good):
        return a_raw
    x, y = np.where(good)
    f = scipy.interpolate.Rbf(x, y, a_raw[good])
    xbad, ybad = np.where(~good)
    a_raw_filled = a_raw.copy()
    a_raw_filled[~good] = f(xbad, ybad)
    return a_raw_filled


def _get_resample_angles_rasterio(
        root, group, dst_res=None, dst_transform=None,
        dst_crs=None, dst_shape=None, extrapolate=True,
        resampling=None, meta=None
):
    """Parse angles and resample to dst_res

    Parameters
    ----------
    root : lxml root
        root of granule metadata XML doc
    group : str
        path to angles tag
    dst_res : int, optional
        target resolution
    dst_transform : Affine, optional
        transform to resample to
    dst_crs : dict or CRS, optional
        destination CRS
    dst_shape : tuple, optional
        destinatinon shape
    extrapolate : bool
        extrapolate to fill NaN areas
    resampling : int, optional
        resampling method
        see rasterio.warp.Resampling
        default: Resampling.bilinear
    meta : dict, optional
        granule metadata
        to avoid parsing twice
    """
    import rasterio.crs
    import rasterio.warp

    if resampling is None:
        resampling = rasterio.warp.Resampling.bilinear

    angles_raw, src_transform, src_crs = _get_angles_with_gref(
        root, group, meta=meta
    )

    # convert to rasterio CRS for safe comparison
    src_crs = rasterio.crs.CRS(src_crs)
    if dst_crs is not None:
        dst_crs = rasterio.crs.CRS(dst_crs)

    if dst_crs is None:
        dst_crs = src_crs

    if dst_crs != src_crs or dst_res is not None:
        # compute new transform and shape
        src_bounds = converters.trans_shape_to_bounds(
                src_transform, angles_raw.shape)
        src_width, src_height = angles_raw.shape
        dst_transform, dst_width, dst_height = (
                rasterio.warp.calculate_default_transform(
                    src_crs, dst_crs, src_width, src_height,
                    *src_bounds,
                    resolution=dst_res)
        )
        dst_shape = (dst_width, dst_height)

    if dst_transform is None:
        dst_transform = src_transform

    if extrapolate:
        angles_raw = _extrapolate_nan(angles_raw)
    return utils.resample(
        angles_raw,
        src_transform=src_transform,
        src_crs=src_crs,
        dst_transform=dst_transform,
        dst_crs=dst_crs,
        dst_shape=dst_shape,
        resampling=resampling,
        src_nodata=np.nan,
        dst_nodata=np.nan
    )


def _get_resample_angles_imresize(
        root, group, dst_shape, interp='bilinear', extrapolate=True
):
    """Parse angles and resample with scipy.misc.imresize

    Parameters
    ----------
    root : lxml root
        root of granule metadata XML doc
    group : str
        path to angles tag
    dst_shape : tuple, optional
        destination shape
    interp : str
        interpolation method
    extrapolate : bool
        extrapolate to fill NaN areas
    """
    from scipy.misc import imresize
    angles_raw = _get_angles_any_type(root, group)
    if extrapolate:
        angles_raw = _extrapolate_nan(angles_raw)
    return imresize(angles_raw, dst_shape, interp=interp, mode='F')


def _get_resample_angles_zoom(
        root, group, dst_shape=None, zoom=None, order=3, extrapolate=True
):
    """Parse angles and resample with scipy.ndimage.zoom

    Parameters
    ----------
    root : lxml root
        root of granule metadata XML doc
    group : str
        path to angles tag
    dst_shape : tuple, optional
        destination shape
    zoom : tuple or int, optional
        used instead of dst_shape
    order : int
        spline interpolation order
    extrapolate : bool
        extrapolate to fill NaN areas
    """
    import scipy.ndimage
    angles_raw = _get_angles_any_type(root, group)
    if extrapolate:
        angles_raw = _extrapolate_nan(angles_raw)
    if zoom is None:
        zoom = np.array(dst_shape) / np.array(angles_raw.shape)
    return scipy.ndimage.zoom(angles_raw, zoom=zoom, order=order, cval=np.nan)


def _generate_group_name(angle, angle_dir, bandId):
    tag = ANGLES_TAGS[angle].format(bandId=bandId)
    return posixpath.join(tag, angle_dir)


def parse_angles(
        metadatafile=None, metadatastr=None,
        angles=ALL_ANGLES,
        angle_dirs=ALL_DIRS,
        bandId=0
):
    """Parse angles from GRANULE metadata

    Parameters
    ----------
    metadatafile : str, optional
        path to metadata file
    metadatastr : str, optional
        metadata string
    angles : list of str
        angles to parse
        subset of ALL_ANGLES
    angle_dirs : list of str
        angle diretions
        subset of ALL_DIRS
    bandId : int
        use this band to retrieve
        viewing angles
        default: 0

    Returns
    -------
    ndarray : angles
    """
    root = converters.get_root(metadatafile, metadatastr)
    angles_data = defaultdict(dict)
    for angle in angles:
        for angle_dir in angle_dirs:
            group = _generate_group_name(angle, angle_dir, bandId=bandId)
            angles_data[angle][angle_dir] = _get_angles_any_type(root, group)
    return angles_data


def parse_resample_angles(
        metadatafile=None, metadatastr=None,
        angles=ALL_ANGLES,
        angle_dirs=ALL_DIRS,
        bandId=0,
        dst_res_predefined=None,
        resample_method='rasterio',
        **resample_kwargs
):
    """Parse angles from GRANULE metadata and resample

    Parameters
    ----------
    metadatafile : str, optional
        path to metadata file
    metadatastr : str, optional
        metadata string
    angles : list of str
        angles to parse
        subset of ALL_ANGLES
    angle_dirs : list of str
        angle diretions
        subset of ALL_DIRS
    bandId : int
        use this band to retrieve
        viewing angles
        default: 0
    dst_res_predefined : int, optional
        predefined destination resolution
        one of 10, 20, 60
    resample_method : str in ['imresize', 'rasterio']
        method to use for resampling
        either based on scipy.misc.imresize
        or based on rasterio.warp.reproject
    **resample_kwargs : additional keyword arguments
        passed to the resampling function

    Returns
    -------
    nested dict : angles > angles_dirs > ndarray
        angles dictionary
    """
    resample_funcs = {
        'rasterio': _get_resample_angles_rasterio,
        'zoom': _get_resample_angles_zoom,
        'imresize': _get_resample_angles_imresize
    }

    try:
        resample_func = resample_funcs[resample_method]
    except KeyError:
        raise ValueError('resample_method must be one of {}.'.format(resample_funcs))

    root = converters.get_root(metadatafile, metadatastr)
    meta = s2meta.parse_granule_metadata_xml(root)

    kw = {}
    if dst_res_predefined is not None:
        kw['dst_shape'] = meta['image_shape'][dst_res_predefined]
        if resample_method == 'rasterio':
            kw['dst_transform'] = meta['image_transform'][dst_res_predefined]
            kw['meta'] = meta

    kw.update(resample_kwargs)

    angles_data = defaultdict(dict)
    for angle in angles:
        for angle_dir in angle_dirs:
            group = _generate_group_name(angle, angle_dir, bandId=bandId)
            angles_data[angle][angle_dir] = resample_func(root, group, **kw)
    return angles_data
