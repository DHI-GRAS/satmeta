import os
import datetime

import shapely.affinity

import satmeta.s1.meta as s1meta
import satmeta.s1.filesearch as s1filesearch

from . import data
from .data import test_data


def test_find_input_files():
    searchdir = data.SAFE_with_manifest
    infiles = s1filesearch.find_input_files(searchdir, formats=['zip', 'SAFE'])
    assert len(infiles) == 2
    infiles = s1filesearch.find_input_files(searchdir, formats=['zip'])
    assert len(infiles) == 1
    assert os.path.splitext(infiles[0])[1] == '.zip'
    infiles = s1filesearch.find_input_files(searchdir, formats=['SAFE'])
    assert len(infiles) == 1
    assert os.path.splitext(infiles[0])[1] == '.SAFE'


def test_find_input_files_empty(tmpdir):
    searchdir = tmpdir.mkdir('empty_stuff')
    with open(str(searchdir.join('S1B_empty.zip')), 'w'):
        pass
    searchdir.mkdir('S1A_empty.SAFE')
    infiles = s1filesearch.find_input_files(
        str(searchdir), formats=['zip', 'SAFE'], ignore_empty=False)
    assert len(infiles) == 2
    infiles = s1filesearch.find_input_files(
        str(searchdir), formats=['zip', 'SAFE'], ignore_empty=True)
    assert len(infiles) == 0


def test_filter_input_files_dates():
    infiles = [test_data[k] for k in ['SAFE', 'zip']]
    out = s1filesearch.filter_input_files(
        infiles,
        start_date=datetime.datetime(2016, 1, 1),
        end_date=datetime.datetime(2016, 12, 31))
    assert out


def test_filter_input_files_dates_none():
    infiles = [test_data[k] for k in ['SAFE', 'zip']]
    out = s1filesearch.filter_input_files(
        infiles,
        start_date=datetime.datetime(2016, 12, 1),
        end_date=datetime.datetime(2016, 12, 31))
    assert not out


def test_filter_input_files_rob():
    infiles = [test_data[k] for k in ['SAFE', 'zip']]
    rob = s1meta.find_parse_metadata(infiles[0])['relative_orbit_number']
    out = s1filesearch.filter_input_files(
        infiles,
        rel_orbit_numbers=[rob])
    assert out


def test_filter_input_files_rob_none():
    infiles = [test_data[k] for k in ['SAFE', 'zip']]
    rob = s1meta.find_parse_metadata(infiles[0])['relative_orbit_number']
    out = s1filesearch.filter_input_files(
        infiles,
        rel_orbit_numbers=[rob - 100])
    assert not out


def test_filter_input_files_aoi():
    infiles = [test_data[k] for k in ['SAFE', 'zip']]
    fp = s1meta.find_parse_metadata(infiles[0])['footprint']
    out = s1filesearch.filter_input_files(
        infiles,
        aoi=fp)
    assert out


def test_filter_input_files_aoi_no_overlap():
    infiles = [test_data[k] for k in ['SAFE', 'zip']]
    fp = s1meta.find_parse_metadata(infiles[0])['footprint']
    fp = shapely.affinity.translate(fp, xoff=180)
    out = s1filesearch.filter_input_files(
        infiles,
        aoi=fp)
    assert not out
