import pytest

from .data import test_data

gpd = pytest.importorskip('geopandas')


def test_meta_as_geopandas():
    from satmeta.s1 import to_geopandas
    safes = [test_data['SAFE'], test_data['zip']]
    gdf = to_geopandas.meta_as_geopandas(safes)
    assert isinstance(gdf, gpd.GeoDataFrame)


def test_meta_as_geopandas_parallel():
    from satmeta.s1 import to_geopandas
    safes = [test_data['SAFE'], test_data['zip']]
    gdf = to_geopandas.meta_as_geopandas_parallel(safes)
    assert isinstance(gdf, gpd.GeoDataFrame)
