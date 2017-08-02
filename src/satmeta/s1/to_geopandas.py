import logging

import geopandas as gpd
import pandas as pd
import shapely.ops

from satmeta.exceptions import MetaDataError
from . import meta as s1meta

logger = logging.getLogger(__name__)


def get_meta_as_geoseries(infile):
    meta = s1meta.find_parse_metadata(infile)
    meta['filepath'] = infile
    return gpd.GeoSeries(meta)


def get_meta_as_geoseries_failsafe(infile):
    try:
        return get_meta_as_geoseries(infile)
    except MetaDataError as me:
        return me


def merge_geoseries(gss):
    return gpd.GeoDataFrame(gss).set_geometry('footprint', crs={'init': 'EPSG:4326'})


def meta_as_geopandas_parallel(infiles):
    import multiprocessing
    import joblib
    num_cores = multiprocessing.cpu_count()
    njobs = min((num_cores, 4))
    gss = joblib.Parallel(n_jobs=njobs)(
            joblib.delayed(get_meta_as_geoseries_failsafe)(infile) for infile in infiles)
    gss_good = []
    for infile, gs in zip(infiles, gss):
        if isinstance(gs, Exception):
            logger.warn(
                    'Reading metadata from \'%s\' failed with error \'%s\'.',
                    infile, gs)
            continue
        gss_good.append(gs)
    return merge_geoseries(gss_good)


def meta_as_geopandas(infiles):
    gss = []
    for infile in infiles:
        try:
            gs = get_meta_as_geoseries(infile)
            gss.append(gs)
        except MetaDataError:
            logger.warn(
                    'Reading metadata from \'%s\' failed with error \'%s\'.',
                    infile, gs)
    return merge_geoseries(gss)


def get_footprint_union(gdf):
    return shapely.ops.unary_union(gdf['footPrint'].values).convex_hull


def group_infiles(gdf):
    """Group input files GeoDataFrame to get stitchable file sets

    Groups by:
        date (assuming that all files from one date are from the same overpass)
          relative orbit
            pass direction
              platform (S1A, S1B)

    Parameters
    ----------
    gdf : GeoDataFrame
        as produced with meta_as_geopandas[_parallel]
    """
    gdf['date'] = pd.DatetimeIndex(gdf.sensing_start).date
    for date, gdf_date in gdf.groupby('date'):
        for rob, gdf_rob in gdf_date.groupby('relative_orbit_number'):
            for passdir, gdf_passdir in gdf_rob.groupby('pass'):
                for platform, gdf_platform in gdf_passdir.groupby('platform'):
                    fp = get_footprint_union(gdf_platform)
                    meta = dict(
                        date=date, rob=rob, passdir=passdir,
                        platform=platform, footprint_union=fp)
                    yield meta, gdf_platform['filepath'].values.tolist()
