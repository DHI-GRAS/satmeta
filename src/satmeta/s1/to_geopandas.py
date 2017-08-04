import logging

import geopandas as gpd
import pandas as pd
import shapely.ops

from satmeta.exceptions import MetaDataError
from . import meta as s1meta

logger = logging.getLogger(__name__)


def get_meta_as_geoseries(infile):
    """Get metadata as GeoSeries

    Parameters
    ----------
    infile : str
        path to S1 data file

    Returns
    -------
    gs : GeoSeries
        metadata from s1.meta
        with additional field 'filepath' (=infile)
    """
    meta = s1meta.find_parse_metadata(infile)
    meta['filepath'] = infile
    return gpd.GeoSeries(meta)


def _get_meta_as_geoseries_failsafe(infile):
    try:
        return get_meta_as_geoseries(infile)
    except MetaDataError as me:
        return me
    except PermissionError as pe:
        return pe


def _merge_geoseries(gss):
    return gpd.GeoDataFrame(gss).set_geometry('footprint', crs={'init': 'EPSG:4326'})


def meta_as_geopandas_parallel(infiles):
    """Get metadata as GeoDataFrame in parallel

    Parameters
    ----------
    infiles : list of str
        paths to S1 data files

    Returns
    -------
    gdf : GeoDataFrame
        metadata for all files
        with additional field 'filepath'

    Note
    ----
    Additional requirement: joblib
    """
    import multiprocessing
    import joblib
    num_cores = multiprocessing.cpu_count()
    njobs = min((num_cores, 4))
    gss = joblib.Parallel(n_jobs=njobs)(
            joblib.delayed(_get_meta_as_geoseries_failsafe)(infile) for infile in infiles)
    gss_good = []
    for infile, gs in zip(infiles, gss):
        if isinstance(gs, Exception):
            logger.warn(
                    'Reading metadata from \'%s\' failed with error \'%s\'.',
                    infile, gs)
            continue
        gss_good.append(gs)
    return _merge_geoseries(gss_good)


def meta_as_geopandas(infiles):
    """Get metadata as GeoDataFrame

    Parameters
    ----------
    infiles : list of str
        paths to S1 data files

    Returns
    -------
    gdf : GeoDataFrame
        metadata for all files
        with additional field 'filepath'
    """
    gss = []
    for infile in infiles:
        try:
            gs = get_meta_as_geoseries(infile)
            gss.append(gs)
        except MetaDataError:
            logger.warn(
                    'Reading metadata from \'%s\' failed with error \'%s\'.',
                    infile, gs)
    return _merge_geoseries(gss)


def _get_footprint_union(gdf):
    return shapely.ops.unary_union(gdf['footprint'].values).convex_hull


def group_infiles(gdf):
    """Group input files GeoDataFrame to get stitchable file sets

    Groups by:
      1. date (assuming that all files from one date are from the same overpass)
      2. relative orbit
      3. pass direction
      4. spacecraft (S1A, S1B)

    Parameters
    ----------
    gdf : GeoDataFrame
        as produced with meta_as_geopandas[_parallel]

    Yields
    ------
    meta : dict
        metadata dictionary for group
    infiles : list of str
        input files
    """
    gdf['date'] = pd.DatetimeIndex(gdf.sensing_start).date
    for date, gdf_date in gdf.groupby('date'):
        for relative_orbit_number, gdf_rob in gdf_date.groupby('relative_orbit_number'):
            for passdir, gdf_passdir in gdf_rob.groupby('passdir'):
                for spacecraft, gdf_spacecraft in gdf_passdir.groupby('spacecraft'):
                    fp = _get_footprint_union(gdf_spacecraft)
                    meta = dict(
                        date=date, relative_orbit_number=relative_orbit_number, passdir=passdir,
                        spacecraft=spacecraft, footprint_union=fp)
                    yield meta, gdf_spacecraft['filepath'].values.tolist()


def filter_gdf(
        gdf, rel_orbit_numbers=None, footprint_overlaps=None,
        start_date=None, end_date=None):
    """Filter S1 metadata GeoDataFrame

    Parameters
    ----------
    gdf : GeoDataFrame
        S1 metadata
    rel_orbit_numbers : list of int
        relative orbit numbers
    footprint_overlaps : shapely.geometry.Polygon
        AOI polygon
    start_date, end_date : datetime.datetime or datestr
        date interval
    """
    if start_date is not None:
        mask = gdf['sensing_start'] >= start_date
        gdf = gdf[mask]
    if end_date is not None:
        mask = gdf['sensing_end'] >= end_date
        gdf = gdf[mask]
    if rel_orbit_numbers is not None:
        mask = gdf.apply((lambda d: d['relative_orbit_number'] in rel_orbit_numbers), axis=1)
        gdf = gdf[mask]
    if footprint_overlaps is not None:
        mask = gdf.overlaps(footprint_overlaps)
        gdf = gdf[mask]
    return gdf
