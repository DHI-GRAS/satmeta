from collections import defaultdict
from collections import OrderedDict

from . import meta as s1meta

def find_date_groups(infiles):
    """Group files by date (ignoring time)"""
    date_groups = defaultdict(list)
    for fname in sorted(infiles):
        date = s1meta.dates_from_fname(fname)[0].date()
        date_groups[date].append(fname)
    return OrderedDict(sorted(date_groups.items()))


