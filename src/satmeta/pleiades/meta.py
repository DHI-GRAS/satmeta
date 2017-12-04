import os

from satmeta.pleiades.metafile import find_metafile_in_folder
from satmeta.pleiades.parser import parse_metadata


def find_parse_metadata(path):
    """Find and parse a metadata file in a folder, TAR or MTD file path"""
    if os.path.isdir(path):
        xmlfile = find_metafile_in_folder(path)
    else:
        xmlfile = path
    return parse_metadata(xmlfile)
