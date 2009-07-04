#from distutils.core import setup
#from distutils.extension import Extension
from setuptools import setup
from setuptools.extension import Extension

import sys

try:
    import numpy
except ImportError:
    print "numpy must be installed to build."
    print "ABORTING."
    sys.exit(1)

try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()


def main():
    setup(name = "pyregion",
          version = "0.1a",
          description = "python parser for ds9 region files",
          author = "Jae-Joon Lee",
          author_email = "lee.j.joon@gmail.com",
          url="http://leejjoon.github.com/pyregion/",
          #maintainer_email = "lee.j.joon@gmail.com",
          license = "MIT",
          platforms = ["Linux","Mac OS X"], # "Solaris"?
          packages = ['pyregion'],
          package_dir={'pyregion':'lib'},

          ext_modules=[ Extension("pyregion._region_filter",
                                  ["src/_region_filter.pyx"],
                                  include_dirs=['./src',
                                                numpy_include,
                                                ],
                                  libraries=[],
                                  )
                        ],

          #test_suite = 'nose.collector',
          )


if __name__ == "__main__":
    main()
