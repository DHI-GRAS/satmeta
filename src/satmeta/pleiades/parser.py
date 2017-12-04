import os

import dateutil.parser
import shapely.geometry

from satmeta import converters


COPY_RENAME = {
    'SOURCE_ID': 'title'}

COPY_RENAME_INT = {
    'NROWS': 'height',
    'NCOLS': 'width',
    'NBANDS': 'count'}


def _get_single_multi(root, names):
    parts = {}
    for name in names:
        parts[name] = converters.get_single(root, name)
    return parts


def _get_angles(root):
    rename_angles = {
        'SUN_AZIMUTH': 'sun_azimuth',
        'SUN_ELEVATION': 'sun_elevation',
        'AZIMUTH_ANGLE': 'sensor_azimuth',
        'INCIDENCE_ANGLE': 'sensor_zenith'}
    center = root.xpath('.//Located_Geometric_Values[LOCATION_TYPE="Center"]')[0]

    def _get_single_float(name):
        return float(converters.get_single(center, name))

    angles = {}
    for name, key in rename_angles.items():
        angles[key] = _get_single_float(name)
    return angles


def _get_spacecraft(root):
    parts = _get_single_multi(root, names=['INSTRUMENT', 'INSTRUMENT_INDEX'])
    return '{INSTRUMENT}{INSTRUMENT_INDEX}'.format(**parts)


def _get_sensing_time(root):
    parts = _get_single_multi(root, names=['IMAGING_DATE', 'IMAGING_TIME'])
    datestr = '{IMAGING_DATE}T{IMAGING_TIME}'.format(**parts)
    return dateutil.parser.parse(datestr)


def _get_footprint(root):
    lons = [float(l.text) for l in root.xpath('.//Dataset_Extent/Vertex/LON')]
    lats = [float(l.text) for l in root.xpath('.//Dataset_Extent/Vertex/LAT')]
    points = list(zip(lons, lats))
    points.append(points[0])
    return shapely.geometry.Polygon(points)


def _parse_metadata_xml(root):
    meta = {}
    meta['angles'] = _get_angles(root)
    meta['spacecraft'] = _get_spacecraft(root)
    meta['sensing_time'] = _get_sensing_time(root)
    meta['footprint'] = _get_footprint(root)
    for name, key in COPY_RENAME.items():
        meta[key] = converters.get_single(root, name)
    for name, key in COPY_RENAME_INT.items():
        meta[key] = int(converters.get_single(root, name))
    return meta


def parse_metadata(xmlfile_or_str):
    if xmlfile_or_str.startswith('<?xml'):
        root = converters.get_root(metadatastr=xmlfile_or_str)
    else:
        root = converters.get_root(metadatafile=xmlfile_or_str)
    return _parse_metadata_xml(root)

