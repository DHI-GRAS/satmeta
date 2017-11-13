import posixpath
from collections import defaultdict

import numpy as np

from satmeta.s2 import meta as s2meta
from satmeta.s2 import utils as s2utils
from satmeta import utils
from satmeta import converters

_angles_tags = {
        'Viewing_Incidence': (
            'Viewing_Incidence_Angles_Grids[@bandId="{bandId}"]'),
        'Sun': 'Sun_Angles_Grid'}

_all_angles = ['Viewing_Incidence', 'Sun']
_all_dirs = ['Zenith', 'Azimuth']


def _get_res(root, group):
    """Get resolution from XML root and data group"""
    res = {}
    for s in ['COL_STEP', 'ROW_STEP']:
        tagname = posixpath.join(group, s)
        res[s] = converters.get_instance(
                root, tagname, index=0, to_type=int)
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


def _get_resample_angles_rasterio(
        root, group, dst_res=None, dst_transform=None,
        dst_crs=None, dst_shape=None, meta=None, resampling=None):
    """Parse angles and resample to dst_res

    Parameters
    ----------
    root : lxml root
        root of granule metadata XML doc
    group : str
        path to angles tag
    dst_res : int, optional
        target resolution
        NB: overrides dst_shape, dst_transform, and dst_crs
    dst_transform : Affine, optional
        transform to resample to
    dst_crs : dict or CRS, optional
        destination CRS
    dst_shape : tuple, optional
        destinatinon shape
    meta : dict, optional
        granule metadata
    resampling : int, optional
        resampling method
        see rasterio.warp.Resampling
        default: Resampling.bilinear
    """
    import rasterio.crs
    import rasterio.warp

    if meta is None:
        meta = s2meta.parse_granule_metadata_xml(root)
    angles_raw, src_transform, src_crs = _get_angles_with_gref(
            root, group, meta=meta)

    if resampling is None:
        resampling = rasterio.warp.Resampling.bilinear

    # convert to rasterio CRS
    src_crs = rasterio.crs.CRS(src_crs)
    if dst_crs is not None:
        dst_crs = rasterio.crs.CRS(dst_crs)

    if dst_res is not None:
        if any([v is not None for v in [dst_transform, dst_shape, dst_crs]]):
            raise ValueError(
                'You provided `dst_res`, which is meant to '
                'override `dst_transform`, `dst_crs`, and `dst_shape`.')
        try:
            dst_transform = meta['image_transform'][dst_res]
            dst_shape = meta['image_shape'][dst_res]
            dst_crs = src_crs
        except KeyError:
            raise ValueError(
                    'You must either specify `dst_crs` and '
                    '`dst_transform` or choose a predefined resolution ({}).'
                    .format(s2meta._all_res))

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

    if dst_transform is None:
        dst_transform = src_transform
    if dst_shape is None:
        dst_shape = angles_raw.shape

    angles_filled = np.ma.masked_invalid(angles_raw).filled(999)

    return utils.resample(
            angles_filled,
            src_transform=src_transform,
            src_crs=src_crs,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            dst_shape=dst_shape,
            resampling=resampling)


def _get_resample_angles_imresize(
        root, group, dst_res=None, dst_shape=None, meta=None):
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
    from scipy.misc import imresize

    if meta is None:
        meta = s2meta.parse_granule_metadata_xml(root)
    angles_raw = _get_angles_any_type(root, group)

    if dst_res is not None:
        dst_shape = meta['image_shape'][dst_res]
    elif dst_shape is None:
        raise ValueError(
                'You must either specify `dst_shape` '
                'or choose a predefined resolution ({}).'
                ''.format(s2meta._all_res))
    return imresize(angles_raw, dst_shape, interp='bilinear', mode='F')


def _generate_group_name(angle, angle_dir, bandId):
    tag = _angles_tags[angle].format(bandId=bandId)
    return posixpath.join(tag, angle_dir)


def parse_angles(
        metadatafile=None, metadatastr=None,
        angles=_all_angles,
        angle_dirs=_all_dirs,
        bandId=0):
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
        angles=_all_angles,
        angle_dirs=_all_dirs,
        bandId=0,
        dst_res=None,
        resample_method='imresize',
        **resample_kwargs):
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
    bandId : int
        use this band to retrieve
        viewing angles
        default: 0
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
    if resample_method == 'imresize':
        _resample_func = _get_resample_angles_imresize
    elif resample_method == 'rasterio':
        _resample_func = _get_resample_angles_rasterio
    else:
        raise ValueError('resample_method must be `imresize` or `rasterio`.')

    root = converters.get_root(metadatafile, metadatastr)
    meta = s2meta.parse_granule_metadata_xml(root)

    angles_data = defaultdict(dict)
    for angle in angles:
        for angle_dir in angle_dirs:
            group = _generate_group_name(angle, angle_dir, bandId=bandId)
            angles_data[angle][angle_dir] = _resample_func(
                    root, group, meta=meta, dst_res=dst_res, **resample_kwargs)
    return angles_data
