import pytest

from .data.s1 import test_data

pexpect = pytest.importorskip('geopandas')

try:
    import geopandas as gpd
    _no_geopandas = False
except ImportError:
    _no_geopandas = True

try:
    import joblib
    _no_joblib = False
except ImportError:
    _no_joblib = True


@pytest.mark.skipif(_no_geopandas, reason='No geopandas')
def test_meta_as_geopandas():
    from satmeta.s1 import to_geopandas
    safes = [test_data['SAFE'], test_data['zip']]
    gdf = to_geopandas.meta_as_geopandas(safes)
    assert isinstance(gdf, gpd.GeoDataFrame)


@pytest.mark.skipif(_no_geopandas, reason='No geopandas')
@pytest.mark.skipif(_no_joblib, reason='No joblib')
def test_meta_as_geopandas_parallel():
    from satmeta.s1 import to_geopandas
    safes = [test_data['SAFE'], test_data['zip']]
    gdf = to_geopandas.meta_as_geopandas_parallel(safes)
    assert isinstance(gdf, gpd.GeoDataFrame)
