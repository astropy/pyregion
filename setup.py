#!/usr/bin/env python
# Licensed under a 3-clause BSD style license - see LICENSE.rst

from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy


include_dirs = [numpy.get_include()]
# define_macros = [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]
extensions = [
    Extension(name="pyregion._region_filter",
              sources=["pyregion/_region_filter.pyx"],
              include_dirs=include_dirs,
            #   define_macros=define_macros,
              ),
    ]
ext_modules = cythonize(extensions, language_level=3, include_path=["pyregion"])

setup(ext_modules=ext_modules)
