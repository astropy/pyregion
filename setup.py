#!/usr/bin/env python
# Licensed under a 3-clause BSD style license - see LICENSE.rst

from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

include_dirs = [numpy.get_include()]
define_macros = [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]
extensions = [
    Extension(name="pyregions._region_filter",
              sources=["pyregion/_region_filter.pyx"],
              include_dirs=include_dirs,
              define_macros=define_macros,
              )
    ]
# ext_modules = cythonize(extensions, language_level=3)
ext_modules = cythonize(extensions, language_level=3, include_path=["pyregion", numpy.get_include()])



LONG_DESCRIPTION = """
pyregion - a Python parser for ds9 region files

* Code : https://github.com/astropy/pyregion
* Docs : http://pyregion.readthedocs.io/

See also the in-development ``regions`` package
at https://github.com/astropy/regions
a new astronomy package for regions based on Astropy.
"""

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Cython',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Scientific/Engineering :: Astronomy',
]

setup(
    long_description=LONG_DESCRIPTION,
    classifiers=classifiers,
    ext_modules=ext_modules
)
