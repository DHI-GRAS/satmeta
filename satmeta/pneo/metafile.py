import os
import glob


def find_metafile_in_folder(path):
    pattern = os.path.join(path, 'IMG_*_MS*', 'DIM_*.XML')
    paths = glob.glob(pattern)
    if len(paths) == 1:
        return paths[0]
    else:
        raise ValueError(
            'Expecting to find exactly one (found: {}) Pleiades Neo metadata file with pattern \'{}\'.'
            .format(len(paths), pattern))
