BAND_NAMES = [1, 2, 3, 4, 5, 6, 7, 8, '8A', 9, 10, 11, 12]


def band_ids_to_band_names(band_ids):
    return [BAND_NAMES[i] for i in band_ids]


def band_names_to_band_ids(band_names):
    band_ids = []
    for band_name in band_names:
        try:
            band_id = BAND_NAMES.index(band_name)
        except ValueError:
            band_id = BAND_NAMES.index(int(band_name))
        band_ids.append(band_id)
    return band_ids
