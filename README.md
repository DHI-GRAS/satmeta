# satmeta

[![Build Status](https://travis-ci.org/DHI-GRAS/satmeta.svg?branch=master)](https://travis-ci.org/DHI-GRAS/satmeta)
[![codecov](https://codecov.io/gh/DHI-GRAS/satmeta/branch/master/graph/badge.svg)](https://codecov.io/gh/DHI-GRAS/satmeta)

Extract meta data from satellite data products


## Features

1. Parse meta data files into Python types
1. Extract and parse meta data from packed (zipped) or unpacked data products
1. Currently supporting Sentinel 1 and Sentinel 2 (MSIL1C)
1. Read metadata into Geopandas' `GeoDataFrames` for quick filtering and grouping


## Installation

```
python setup.py install
```

Minimum requirements are `pyton-dateutil lxml shapely affine`.

To use Geopandas, you obviously need `geopandas`, too. 
For parallel extraction of metadata from many files, you need to have `joblib`.


### Additional requirements for S2 Sun and viewing incidence angles (2D)

The `satmeta.s2.angles_2d` module has functions for parsing Sentinel 2
Sun and Viewing Incidence angles in 2D. These come on 5000 m resolution grids.

There are functions to resample these grids to any other resolution,
either using `scipy` and `PIL` (from the `scipy.misc.imresize` function) or 
`rasterio.warp.reproject`.

If you want to resample angles, you need to install either of these dependencies,
preferably with `conda`:

```
conda install scipy pillow
```

or

```
conda install rasterio -c conda-forge/label/dev
```
