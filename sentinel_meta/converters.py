import logging

import shapely.geometry
import dateutil.parser

logger = logging.getLogger(__name__)


def get_single(root, tagname, attrname=None):
    results = root.findall('.//{}'.format(tagname), namespaces=root.nsmap)
    if len(results) != 1:
        raise ValueError('Expected to find a single instance of tag \'{}\'. Found {}.'.format(tagname, len(results)))
    if attrname is not None:
        return results[0].attrib[attrname]
    else:
        return results[0].text


def get_instance(root, tagname, attrname=None, index=0):
    result = root.findall('.//{}'.format(tagname), namespaces=root.nsmap)[index]
    if attrname is not None:
        return result.attrib[attrname]
    else:
        return result.text


def get_all(root, tagname, attrname=None):
    results = root.findall('.//{}'.format(tagname), namespaces=root.nsmap)
    if attrname is not None:
        return [e.attrib[attrname] for e in results]
    else:
        return [e.text for e in results]


def get_single_date(root, tagname):
    datestr = get_single(root, tagname)
    return dateutil.parser.parse(datestr)


def _parse_coordinates_str(cs):
    """Parse coordinates string"""
    return [tuple(map(float, s.split(','))) for s in cs.split()]


def _coords_to_polygon(coords):
    return shapely.geometry.shape(dict(type='Polygon', coordinates=[coords]))


def get_single_polygon(root, tagname):
    coordinates_str = get_single(root, tagname)
    coords = _parse_coordinates_str(coordinates_str)
    return shapely.geometry.shape(dict(type='Polygon', coordinates=[coords]))
