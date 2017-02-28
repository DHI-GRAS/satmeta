import os.path
import logging

import click

from . import parsers

logger = logging.getLogger('sentinel_meta.scripts.filesearch')


@click.group()
def filesearch():
    """Filter sentinel data files by meta data"""
    pass


@filesearch.command()
@click.argument('indir', type=click.Path(dir_okay=True))
@click.option('--orbit_number', '-oo', 'orbit_numbers', multiple=True, type=int, help='Orbit numbers to look for')
@click.option('--SAFE/--no-SAFE', 'find_SAFE', default=True, help='Whether to look for SAFE files in INDIR (default: True)')
@click.option('--zip/--no-zip', 'find_zip', default=True, help='Whether to look for zip files in INDIR (default: True)')
@click.option('--start-date', '-s', type=parsers.Datetime(format='%Y%m%d'), help='Start date (YYYYMMDD)')
@click.option('--end-date', '-s', type=parsers.Datetime(format='%Y%m%d'), help='End date (YYYYMMDD)')
@click.option('--fullpath/--no-fullpath', default=True, help='Print full path to files (default: True)')
def search_s1(indir, find_SAFE, find_zip, fullpath=True, **filterkw):
    from ..s1 import filesearch as s1fs
    formats = []
    if find_SAFE:
        formats.append('SAFE')
    if find_zip:
        formats.append('zip')
    logger.debug('Formats are {}'.format(formats))
    infiles = s1fs.find_input_files(indir, formats=formats)
    infiles_filtered = s1fs.filter_input_files(infiles, **filterkw)
    click.echo('Total number of files: {}'.format(len(infiles_filtered)))
    for infile in infiles_filtered:
        if fullpath:
            click.echo(infile)
        else:
            click.echo(os.path.basename(infile))
    click.echo('Total number of files: {}'.format(len(infiles_filtered)))
