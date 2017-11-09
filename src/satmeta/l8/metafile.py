import os
import glob
import shutil
import tarfile


def _find_metafile_in_names(names):
    mtls = [name for name in names if '_MTL' in name]
    if not len(mtls) == 1:
        raise ValueError('Found more than one MTL candidate: {}', mtls)
    return mtls[0]


def find_metafile_folder(indir):
    pattern = os.path.join(indir, '*_MTL.txt')
    try:
        return glob.glob(pattern)[0]
    except IndexError:
        raise ValueError('Unable to find MTL file in folder \'{}\'.'.format(indir))


def extract_metafile_folder(indir, outfile):
    source = find_metafile_folder(indir)
    shutil.copy(source, outfile)


def read_metafile_folder(indir):
    mtlfile = find_metafile_folder(indir)
    with open(mtlfile) as fin:
        return fin.read()


def read_metafile_TAR(infile):
    with tarfile.open(infile) as tar:
        names = tar.getnames()
        mtl_member = _find_metafile_in_names(names)
        mstr = tar.extractfile(mtl_member).read()
        return mstr.decode('utf-8')


def extract_metafile_TAR(infile, outfile):
    mstr = read_metafile_TAR(infile)
    with open(outfile, 'w') as fout:
        fout.write(mstr)


def extract_metafile(input_path, outfile):
    if os.path.isdir(input_path):
        extract_metafile_folder(input_path. outfile)
    else:
        extract_metafile_TAR(input_path, outfile)


def read_metafile(path):
    if os.path.isfile(path):
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.tar', '.gz', '.tgz']:
            return read_metafile_TAR(path)
        else:
            # assume plain text
            mstr = open(path).read()
            if 'LANDSAT' in mstr:
                return mstr
            else:
                raise ValueError(
                    'File \'{}\' is not a plain-text MTD file'.format(path))
    elif os.path.isdir(path):
        return read_metafile_folder(path)
    raise ValueError('Input path \'{}\' is neither a valid (TXT/TAR) file or folder.')
