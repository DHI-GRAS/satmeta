import os

testdatadir = os.path.abspath(os.path.dirname(__file__))

SAFE_with_manifest = os.path.join(testdatadir, 'SAFE_with_manifest')

test_data = {
        'SAFE': os.path.join(SAFE_with_manifest, 'S1A_IW_GRDH_1SDV_20160114T053940_20160114T054005_009486_00DC3C_4695.SAFE'),
        'zip': os.path.join(SAFE_with_manifest, 'S1A_IW_GRDH_1SDV_20160114T053940_20160114T054005_009486_00DC3C_4695.zip'),
        'manifest': os.path.join(SAFE_with_manifest, 'S1A_IW_GRDH_1SDV_20160114T053940_20160114T054005_009486_00DC3C_4695.SAFE', 'manifest.safe')}
