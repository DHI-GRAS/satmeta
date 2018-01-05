import logging
import multiprocessing
import concurrent.futures

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


def meta_as_geopandas(infiles, multiprocessing_above=40):
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
    multiprocessing_above : int
        use multiprocessing above this number of input files
        set to None to disable
    """
    if multiprocessing_above is not None and len(infiles) > multiprocessing_above:
        nprocs = multiprocessing.cpu_count()
        with concurrent.futures.ProcessPoolExecutor(nprocs) as executor:
            gss = list(executor.map(_get_meta_as_geoseries_failsafe, infiles))
    else:
        gss = [_get_meta_as_geoseries_failsafe(infile) for infile in infiles]
    gss_good = []
    for infile, gs in zip(infiles, gss):
        if isinstance(gs, Exception):
            logger.warn(
                    'Reading metadata from \'%s\' failed with error \'%s\'.',
                    infile, gs)
            continue
        gss_good.append(gs)
    return _merge_geoseries(gss_good)


def _get_footprint_union(gdf):
    return shapely.ops.unary_union(gdf['footprint'].values).convex_hull


def stitchable_infiles(gdf):
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


def group_by_relorbit_and_date(gdf):
    """Group input files GeoDataFrame by relative orbit and date

    Parameters
    ----------
    gdf : GeoDataFrame
        input metadata

    Yields
    ------
    meta : dict
        metadata for group
    gdf_date : GeoDataFrame
        grouped meta data

    Order
    -----
    Groups will be ordered by date first and relative orbit number second
    i.e. consecutive pairs have same relative orbit but different date
    but might also have different relative orbit when one group ends
    """
    gdf['date'] = pd.DatetimeIndex(gdf.sensing_start).date
    for relative_orbit_number, gdf_rob in gdf.groupby('relative_orbit_number'):
        for date, gdf_date in gdf_rob.groupby('date'):
            meta = dict(
                date=date, relative_orbit_number=relative_orbit_number)
            yield meta, gdf_date


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
    if len(gdf) and start_date is not None:
        mask = gdf['sensing_end'] >= start_date
        gdf = gdf[mask]
    if len(gdf) and end_date is not None:
        mask = gdf['sensing_start'] <= end_date
        gdf = gdf[mask]
    if len(gdf) and rel_orbit_numbers is not None:
        mask = gdf.apply((lambda d: d['relative_orbit_number'] in rel_orbit_numbers), axis=1)
        gdf = gdf[mask]
    if len(gdf) and footprint_overlaps is not None:
        mask = gdf.intersects(footprint_overlaps)
        gdf = gdf[mask]
    return gdf
