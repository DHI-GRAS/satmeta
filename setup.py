from setuptools import setup, find_packages

setup(
    name='satmeta',
    version='0.8.2',
    description='Satellite Meta Data Extraction',
    author='Jonas Solvsteen',
    author_email='josl@dhi-gras.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'python-dateutil',
        'lxml', 'shapely'])
