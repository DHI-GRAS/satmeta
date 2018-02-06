import affine


def kw_to_affine(ULX, ULY, COL_STEP, ROW_STEP):
    """Convert meta data keys to affine transform"""
    return affine.Affine(COL_STEP, 0, ULX, 0, -ROW_STEP, ULY)


def res_pos_to_affine(res, pos):
    """Wrapper to kw_to_affine taking to dictionaries"""
    kwargs = dict(res, **pos)
    return kw_to_affine(**kwargs)
