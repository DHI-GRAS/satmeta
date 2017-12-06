import os

testdatadir = os.path.abspath(os.path.dirname(__file__))

SAFE_new = os.path.join(testdatadir, 'new_format', 'S2A_MSIL1C_20170103T104432_N0204_R008_T33VUC_20170103T104428.SAFE')
ZIP_new = os.path.join(testdatadir, 'new_format', 'S2A_MSIL1C_20170103T104432_N0204_R008_T33VUC_20170103T104428.zip')

SAFE_old = os.path.join(testdatadir, 'old_format', 'short.SAFE')
ZIP_old = os.path.join(testdatadir, 'old_format', 'S2A_OPER_PRD_MSIL1C_PDMC_20161206T101413_R022_V20161205T101402_20161205T101402.zip')

GRANULE_new = os.path.join(SAFE_new, 'GRANULE', 'L1C_T33VUC_A008013_20170103T104428')
GRANULE_old = os.path.join(SAFE_old, 'GRANULE', 'S2A_OPER_MSI_L1C_TL_SGS__20161205T171834_A007598_T33UVB_N02.04')

l2a_dir = os.path.join(testdatadir, 'L2A')

test_data = {
    'new': {
        'SAFE': SAFE_new,
        'zip': ZIP_new,
        'xml': os.path.join(SAFE_new, 'MTD_MSIL1C.xml'),
        'granule_xml': os.path.join(GRANULE_new, 'MTD_TL.xml')},
    'old': {
        'SAFE': SAFE_old,
        'zip': ZIP_old,
        'xml': os.path.join(SAFE_old, 'S2A_OPER_MTD_SAFL1C_PDMC_20161206T101413_R022_V20161205T101402_20161205T101402.xml'),
        'granule_xml': os.path.join(GRANULE_old, 'S2A_OPER_MTD_L1C_TL_SGS__20161205T171834_A007598_T33UVB.xml')},
    'L2A': {
        'xml': os.path.join(l2a_dir, 'MTD_MSIL2A.xml'),
        'granule_xml': os.path.join(l2a_dir, 'MTD_TL.xml')}}


test_tile_ID = {
        'new': '33VUC',
        'old': '33UVB',
        'L2A': '32VNJ'}
