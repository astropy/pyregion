#from distutils.core import setup
#from distutils.extension import Extension
from setuptools import setup
from setuptools.extension import Extension

import sys
from os.path import join

try:
    import numpy
except ImportError:
    print "numpy must be installed to build pywcs."
    print "ABORTING."
    sys.exit(1)

try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()


# REGIONLIB = "region" # Path to cxc region library
# REGIONLIBFILES = [ # List of reguib kubrary files to compile
#     "region_attribute.c",
#     "region_create.c",
#     "region_extent.c",
#     "region_inside.c",
# #    "region_read.c",
# #    "region_test.c",
# #    "region_type.c",
#     "region_util.c",
# #    "region_write.c",
#     "reglexer.c",
#     "regparser.c",
#     "regparser.tab.c",
#     ]

# REGIONLIBFILES = [join(REGIONLIB, x) for x in REGIONLIBFILES]

 

def main():
    #dolocal()
    setup(name = "pyregion",
          version = "0.1b1",
          description = "python wrapper around some region library",
          author = "Jae-Joon Lee",
          maintainer_email = "lee.j.joon@gmail.com",
          license = "???",
          platforms = ["Linux","Mac OS X"], # "Solaris"?
          packages = ['pyregion'],
          package_dir={'pyregion':'lib'},
          #package_data={'pysao': ["ds9_xpa_help.pickle"]},
          
          ext_modules=[ Extension("pyregion._region",
                                  ["_region.pyx"], #+REGIONLIBFILES,
                                  include_dirs=['./region',
                                                numpy_include,
                                                #'/sw/lib/python2.4/site-packages/numpy/core/include'],
                                                ],
#                                  library_dirs=['./region'],
                                  libraries=[],
                                  )
                        ],
          #cmdclass = {'build_ext': build_ext},
          #test_suite = "test.saods9_test",
          test_suite = 'nose.collector',
          )

if __name__ == "__main__":
    main()
