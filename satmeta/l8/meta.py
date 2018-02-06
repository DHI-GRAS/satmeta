from satmeta.l8.metafile import read_metafile
from satmeta.l8.parser import parse_metadata


def find_parse_metadata(path):
    """Find and parse a metadata file in a folder, TAR or MTD file path"""
    mstr = read_metafile(path)
    return parse_metadata(mstr.splitlines())
