# satmeta

[![Build Status](https://travis-ci.org/DHI-GRAS/satmeta.svg?branch=master)](https://travis-ci.org/DHI-GRAS/satmeta)

Sentinel Meta Data


## Installation

```
python setup.py install
```

### Sentinel 2 Sun and Viewing Incidence angles

The `satmeta.s2.angles` module has functions for parsing Sentinel 2
Sun and Viewing Incidence angles. These come on 5000 m resolution grids.
There are functions to resample these grids to any other resolution,
either using `scipy` and `PIL` (the `scipy.misc.imresize` function) or 
`rasterio.warp.reproject`.

If you want to resample angles, you need to install either of these dependencies.
Currently, `pil` is only available for Python 2 and the `rasterio` method only works
on Python 3.6.

So depending on your system, install the dependencies, preferably with `conda`:

```
conda install scipy pil
```

or

```
conda install rasterio
```
