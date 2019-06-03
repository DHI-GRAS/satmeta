from pathlib import Path
import zipfile

import pytest

here = Path(__file__).resolve().parent


@pytest.fixture(scope='session')
def safe_zip():
    path = (
        here / 'data' /
        'S1A_IW_GRDH_1SDV_20190301T052343_20190301T052408_026140_02EABC_E6CF.zip'
    )
    assert path.is_file()
    return path


@pytest.fixture(scope='session')
def safe_unzipped(safe_zip, tmp_path_factory):
    tmpdir = tmp_path_factory.mktemp('s1_safe')
    with zipfile.ZipFile(safe_zip) as zf:
        zf.extractall(tmpdir)
    safedir = tmpdir / 'S1A_IW_GRDH_1SDV_20190301T052343_20190301T052408_026140_02EABC_E6CF.SAFE'
    return safedir


@pytest.fixture(scope='session')
def manifest(safe_unzipped):
    path = safe_unzipped / 'manifest.safe'
    assert path.is_file()
    return path
