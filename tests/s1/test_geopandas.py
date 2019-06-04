import datetime

import pytest

try:
    import satmeta.s1.to_geopandas as s1geopandas
except ImportError:
    pytestmark = pytest.mark.skip(reason='geopandas not installed')

gpd = pytest.importorskip('geopandas')


def test_meta_as_geopandas(safe_unzipped, safe_zip):
    infiles = [safe_unzipped, safe_zip]
    gdf = s1geopandas.meta_as_geopandas(infiles)
    assert isinstance(gdf, gpd.GeoDataFrame)


def test_meta_as_geopandas_multiprocessing(safe_unzipped, safe_zip):
    infiles = [safe_unzipped, safe_zip]
    gdf = s1geopandas.meta_as_geopandas(infiles, multiprocessing_above=0)
    assert isinstance(gdf, gpd.GeoDataFrame)


def test_stitchable_infiles(safe_unzipped, safe_zip):
    infiles = [safe_unzipped, safe_zip]
    gdf = s1geopandas.meta_as_geopandas(infiles)
    grouped = s1geopandas.stitchable_infiles(gdf)
    for meta, infiles_group in grouped:
        assert isinstance(meta, dict)
        assert 'date' in meta
        assert 'relative_orbit_number' in meta
        assert 'spacecraft' in meta
        break


def test_group_by_relorbit_and_date(safe_unzipped, safe_zip):
    infiles = [safe_unzipped, safe_zip]
    gdf = s1geopandas.meta_as_geopandas(infiles)
    grouped = s1geopandas.group_by_relorbit_and_date(gdf)
    for meta, infiles_group in grouped:
        assert isinstance(meta, dict)
        assert isinstance(infiles_group, type(gdf))
        break


def test_filter_gdf(safe_unzipped, safe_zip):
    infiles = [safe_unzipped, safe_zip]
    gdf = s1geopandas.meta_as_geopandas(infiles)
    gdf_filtered = s1geopandas.filter_gdf(
        gdf,
        rel_orbit_numbers=gdf['relative_orbit_number'].values,
        footprint_overlaps=gdf['footprint'].values[0],
        start_date=datetime.datetime(2019, 1, 1),
        end_date=datetime.datetime(2025, 12, 31))
    assert len(gdf) == len(gdf_filtered)
