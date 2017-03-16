import logging

import shapely.geometry
import dateutil.parser

logger = logging.getLogger(__name__)


def _get_value(element, attrname=None, to_type=None):
    if attrname is not None:
        s = element.attrib[attrname]
    else:
        s = element.text
    if to_type is None:
        return s
    else:
        return to_type(s)


def get_single(root, tagname, attrname=None, to_type=None):
    results = root.findall('.//{}'.format(tagname), namespaces=root.nsmap)
    if len(results) != 1:
        raise ValueError('Expected to find a single instance of tag \'{}\'. Found {}.'.format(tagname, len(results)))
    return _get_value(results[0], attrname=attrname, to_type=to_type)


def get_instance(root, tagname, attrname=None, index=0, to_type=None):
    result = root.findall('.//{}'.format(tagname), namespaces=root.nsmap)[index]
    return _get_value(result, attrname=attrname, to_type=to_type)


def get_all(root, tagname, attrname=None, to_type=None):
    results = root.findall('.//{}'.format(tagname), namespaces=root.nsmap)
    return [_get_value(e, attrname=attrname, to_type=to_type) for e in results]


def get_single_date(root, tagname):
    return get_single(root, tagname, to_type=dateutil.parser.parse)


def _parse_coordinates_str(cs):
    return [tuple(map(float, s.split(','))) for s in cs.split()]


def _coords_to_polygon(coords):
    return shapely.geometry.shape(dict(type='Polygon', coordinates=[coords]))


def parse_coords(coordinates_str):
    """Parse GeoJSON-like coordinates string as a Polygon"""
    coords = _parse_coordinates_str(coordinates_str)
    return _coords_to_polygon(coords)


def get_single_polygon(root, tagname):
    return get_single(root, tagname, to_type=parse_coords)
