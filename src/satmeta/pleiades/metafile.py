import os
import glob


def find_metafile_in_folder(path):
    pattern = os.path.join(path, 'IMG_*', 'DIM_*.XML')
    try:
        return glob.glob(pattern)[0]
    except IndexError:
        raise ValueError(
            'No Pleiades metadata file found with pattern \'{}\'.'
            .format(pattern))
