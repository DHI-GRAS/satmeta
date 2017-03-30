from setuptools import setup, find_packages

setup(
    name='sentinel_meta',
    version='0.2',
    description='Sentinel Meta Data Extraction',
    author='Jonas Solvsteen',
    author_email='josl@dhi-gras.com',
    packages=find_packages(),
    entry_points="""
    [console_scripts]
    sentinel_meta=sentinel_meta.scripts.cli:cli
    sentinel_filesearch=sentinel_meta.scripts.filesearch:filesearch
    """,
    install_requires=[
        'python-dateutil',
        'lxml', 'shapely'])
