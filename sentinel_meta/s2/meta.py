import functools

from .. import converters


def get_sizes(root):
    sizes = {}
    for res in [10, 20, 60]:
        sizes[res] = {}
        for dim in ['NROWS', 'NCOLS']:
            sizetag = './/Size[@resolution=\'{}\']/{}'.format(res, dim)
            sizes[res][dim] = int(root.findall(sizetag)[0].text)
    return sizes


def get_geopositions(root):
    geopos = {}
    for res in [10, 20, 60]:
        geopos[res] = {}
        for corner in ['ULX', 'ULY']:
            sizetag = './/Geoposition[@resolution=\'{}\']/{}'.format(res, corner)
            geopos[res][corner] = int(root.findall(sizetag)[0].text)
    return geopos


def parse_granule_metadata(metadatafile=None, metadatastr=None):
    root = converters.get_root(metadatafile, metadatastr)
    _get_single = functools.partial(converters.get_single, root)
    metadata = {
            'sun_senith': _get_single('Mean_Sun_Angle/ZENITH_ANGLE', to_type=float),
            'sun_azimuth': _get_single('Mean_Sun_Angle/AZIMUTH_ANGLE', to_type=float),
            'sensor_senith': converters.get_all(root, 'Mean_Viewing_Incidence_Angle_List/Mean_Viewing_Incidence_Angle/ZENITH_ANGLE', to_type=float),
            'sensor_azimuth': converters.get_all(root, 'Mean_Viewing_Incidence_Angle_List/Mean_Viewing_Incidence_Angle/AZIMUTH_ANGLE', to_type=float),
            'projection': _get_single('HORIZONTAL_CS_CODE'),
            'cloudCoverPercent': _get_single('CLOUDY_PIXEL_PERCENTAGE', to_type=float),
            'image_size': get_sizes(root),
            'image_geoposition': get_geopositions(root)}
    return metadata


def parse_metadata(metadatafile=None, metadatastr=None):
    root = converters.get_root(metadatafile, metadatastr)
    _get_single = functools.partial(converters.get_single, root)
    metadata = {
            'productName': _get_single('PRODUCT_URI'),
            'startTime': converters.get_single_date(root, 'PRODUCT_START_TIME'),
            'processing_level': _get_single('PROCESSING_LEVEL'),
            'spacecraft': _get_single('SPACECRAFT_NAME'),
            'orbit_direction': _get_single('SENSING_ORBIT_DIRECTION'),
            'quantification_value': _get_single('QUANTIFICATION_VALUE', to_type=int),
            'reflectance_conversion': _get_single('Reflectance_Conversion/U', to_type=float),
            'irradiance_values': converters.get_all(root, 'Reflectance_Conversion/Solar_Irradiance_List/SOLAR_IRRADIANCE', to_type=float)}
    return metadata
