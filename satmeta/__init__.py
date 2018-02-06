from satmeta import s1
from satmeta import s2
from satmeta import l8

# keys present in all metadata dictionaries
COMMON_KEYS = [
    'sensing_time', 'title', 'spacecraft']

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
