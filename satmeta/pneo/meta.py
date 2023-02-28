import os

from satmeta.pneo.metafile import find_metafile_in_folder
from satmeta.pneo.parser import parse_metadata


def find_parse_metadata(path):
    """Find and parse a metadata file in a folder, TAR or MTD file path"""
    if os.path.isdir(path):
        xmlfile = find_metafile_in_folder(path)
    else:
        xmlfile = path
    return parse_metadata(xmlfile)
