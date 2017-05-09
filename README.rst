pyregion
========

pyregion is a python module to parse ds9 region files.
It also supports ciao region files.

* Code: https://github.com/astropy/pyregion
* Docs: https://pyregion.readthedocs.io
* PyPI: http://pypi.python.org/pypi/pyregion

Installation: ``pip install pyregion``

Lead developer: Jae-Joon Lee ([@leejjoon](http://github.com/leejjoon))

FEATURES
--------

* ds9 and ciao region files.
* (physical, wcs) coordinate conversion to the image coordinate.
* convert regions to matplotlib patches.
* convert regions to spatial filter (i.e., generate mask images)

LICENSE
-------

All files are under MIT License. See LICENSE.

Status
------

.. image:: https://travis-ci.org/astropy/pyregion.svg?branch=master
    :target: https://travis-ci.org/astropy/pyregion

.. image:: https://coveralls.io/repos/astropy/pyregion/badge.svg?branch=master
    :target: https://coveralls.io/r/astropy/pyregion

New regions package
-------------------

See also the in-development ``regions`` package
at https://github.com/astropy/regions
a new astronomy package for regions based on Astropy.
