import re
from itertools import product

import shapely.geometry
import dateutil.parser


PREFIX_REMOVE = [
    'LANDSAT_', 'WRS_']

STRING_LINES = [
    'LANDSAT_SCENE_ID', 'LANDSAT_PRODUCT_ID', 'SPACECRAFT_ID',
    'SENSOR_ID', 'NADIR_OFFNADIR']

INT_LINES = [
    'WRS_PATH', 'WRS_ROW',
    'IMAGE_QUALITY_OLI', 'IMAGE_QUALITY_TIRS',
    'UTM_ZONE',
    'REFLECTIVE_LINES', 'REFLECTIVE_SAMPLES',
    'PANCHROMATIC_LINES', 'PANCHROMATIC_SAMPLES']

FLOAT_LINES = [
    'CLOUD_COVER', 'CLOUD_COVER_LAND',
    'ROLL_ANGLE', 'SUN_AZIMUTH', 'SUN_ELEVATION',
    'EARTH_SUN_DISTANCE']

SPECIAL_PATTERNS = {
    'DATE_ACQUIRED': r'DATE_ACQUIRED\s=\s([\d-]*)',
    'SCENE_CENTER_TIME': r'SCENE_CENTER_TIME\s=\s"([\d:\.]*Z)"'}

KEYGEN_PATTERNS = [
    (float, re.compile(r'CORNER_([A-Z_]+)_PRODUCT\s=\s(-?\d+\.?\d*)'))]


def _generate_string_pattern(key):
    return r'{key}\s=\s"(.*)"'.format(key=key)


def _generate_int_pattern(key):
    return r'{key}\s=\s(-?\d+)'.format(key=key)


def _generate_float_pattern(key):
    return r'{key}\s=\s(-?\d+\.?\d*)'.format(key=key)


def _remove_prefix(key):
    for prefix in PREFIX_REMOVE:
        if key.startswith(prefix):
            key = key[len(prefix):]
    return key


def _gather_patterns():
    patterns = {}
    patterns.update(
        {key: _generate_string_pattern(key) for key in STRING_LINES})
    patterns.update(
        {key: _generate_int_pattern(key) for key in INT_LINES})
    patterns.update(
        {key: _generate_float_pattern(key) for key in FLOAT_LINES})
    patterns.update(SPECIAL_PATTERNS)
    patterns = {k: re.compile(v) for k, v in patterns.items()}
    return patterns


def _gather_converters():
    converters = {}
    converters.update(
        {key: int for key in INT_LINES})
    converters.update(
        {key: float for key in FLOAT_LINES})
    return converters


def _plain_parse_metadata(lines):
    metadata = {}
    patterns = _gather_patterns()
    converters = _gather_converters()
    for line in lines:
        for key, pattern in patterns.items():
            match = re.search(pattern, line)
            if match is not None:
                value = match.group(1)
                if key in converters:
                    value = converters[key](value)
                metadata[key] = value
        for converter, pattern in KEYGEN_PATTERNS:
            match = re.search(pattern, line)
            if match is not None:
                key, value = match.groups()
                metadata[key] = converter(value)
    return metadata


def _postprocess_sensing_time(metadata):
    datestr = metadata.pop('date_acquired')
    timestr = metadata.pop('scene_center_time')
    dtstring = datestr + 'T' + timestr
    metadata['sensing_time'] = dateutil.parser.parse(dtstring)


def _postprocess_title(metadata):
    metadata['title'] = metadata['product_id']


def _postprocess_spacecraft(metadata):
    scid = metadata['spacecraft_id']
    metadata['spacecraft'] = ''.join(re.search('(L)ANDSAT_(\d)', scid).groups())


def _get_footprint(metadata, xext, yext):
    corners = [''.join(pair) for pair in product('UL', 'LR')]
    x_corners = [corner + xext for corner in corners]
    y_corners = [corner + yext for corner in corners]
    vertices = []
    for xkey, ykey in zip(x_corners, y_corners):
        x = metadata.pop(xkey)
        y = metadata.pop(ykey)
        vertices.append((x, y))
    vertices.append(vertices[0])
    return shapely.geometry.Polygon(vertices)


def parse_metadata(lines):
    """Parse Landsat 8 metadata from iterable of lines

    Parameters
    ----------
    lines : iterable of lines in MTD file
        can be file-like object
        or list of str

    Returns
    -------
    dict
        metadata
    """
    metadata = _plain_parse_metadata(lines)
    metadata['footprint'] = _get_footprint(metadata, xext='_LON', yext='_LAT')
    metadata['footprint_projected'] = _get_footprint(metadata,
                                                     xext='_PROJECTION_X', yext='_PROJECTION_Y')
    # rename keys to lowercase
    metadata = {_remove_prefix(k).lower(): v for k, v in metadata.items()}
    _postprocess_sensing_time(metadata)
    _postprocess_spacecraft(metadata)
    _postprocess_title(metadata)
    return metadata
