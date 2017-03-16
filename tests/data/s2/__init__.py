import os

testdatadir = os.path.abspath(os.path.dirname(__file__))

SAFE = os.path.join(testdatadir, 'new_format', 'S2A_MSIL1C_20170103T104432_N0204_R008_T33VUC_20170103T104428.SAFE')

GRANULE = os.path.join(SAFE, 'GRANULE', 'L1C_T33VUC_A008013_20170103T104428')

test_data = {
        'SAFE': SAFE,
        'xml': os.path.join(SAFE, 'MTD_MSIL1C.xml'),
        'granule_xml': os.path.join(GRANULE, 'MTD_TL.xml')}
