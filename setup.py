from setuptools import setup, find_packages

setup(
    name='satmeta',
    version='0.5',
    description='Satellite Meta Data Extraction',
    author='Jonas Solvsteen',
    author_email='josl@dhi-gras.com',
    packages=find_packages(),
    install_requires=[
        'python-dateutil',
        'lxml', 'shapely'])
