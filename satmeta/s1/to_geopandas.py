
from . import meta as s1meta

import geopandas as gpd


def get_meta_as_geoseries(infile):
    meta = s1meta.find_parse_metadata(infile)
    meta['filepath'] = infile
    return gpd.GeoSeries(meta)


def merge_geoseries(gss):
    return gpd.GeoDataFrame(gss).set_geometry('footPrint', crs={'init': 'EPSG:4326'})


def meta_as_geopandas_parallel(infiles):
    import multiprocessing
    import joblib
    num_cores = multiprocessing.cpu_count()
    njobs = min((num_cores, 4))
    gss = joblib.Parallel(n_jobs=njobs)(joblib.delayed(get_meta_as_geoseries)(infile) for infile in infiles)
    return merge_geoseries(gss)


def meta_as_geopandas(infiles):
    gss = [get_meta_as_geoseries(infile) for infile in infiles]
    return merge_geoseries(gss)
