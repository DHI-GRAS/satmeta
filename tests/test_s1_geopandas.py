import pytest

try:
    import geopandas as gpd
    from satmeta.s1 import to_geopandas
except ImportError:
    pytestmark = pytest.mark.skip(reason='No geopandas')

try:
    import joblib
    _no_joblib = False
except ImportError:
    _no_joblib = True

from .data.s1 import test_data


def test_meta_as_geopandas():
    safes = [test_data['SAFE'], test_data['zip']]
    gdf = to_geopandas.meta_as_geopandas(safes)
    assert isinstance(gdf, gpd.GeoDataFrame)


@pytest.mark.skipif(_no_joblib, reason='No joblib')
def test_meta_as_geopandas_parallel():
    safes = [test_data['SAFE'], test_data['zip']]
    gdf = to_geopandas.meta_as_geopandas_parallel(safes)
    assert isinstance(gdf, gpd.GeoDataFrame)
