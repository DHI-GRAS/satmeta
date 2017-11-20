import datetime

from satmeta.s1 import bookkeeping as s1bookkeeping

from .data import test_data


def test_find_date_groups():
    nreps = 1
    infiles = [test_data['zip']] * nreps
    groups = s1bookkeeping.find_date_groups(infiles)
    keys = list(groups.keys())
    assert len(keys) == 1
    first_key = keys[0]
    assert isinstance(first_key, datetime.date)
    files_group = groups[first_key]
    assert len(files_group) == nreps
