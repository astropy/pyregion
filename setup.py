try:
    from setuptoolsas import setup
    from setuptools.extension import Extension
    PYREX_SOURCE = "src/_region_filter.pyx"
except ImportError:
    from distutils.core import setup, Extension
    PYREX_SOURCE = "src/_region_filter.c"

import sys

# If you don't want to build filtering module (which requires a C
# compiler), set it to False
WITH_FILTER = True



def main():
    ka = dict(name = "pyregion",
              version = "0.1a",
              description = "python parser for ds9 region files",
              author = "Jae-Joon Lee",
              author_email = "lee.j.joon@gmail.com",
              url="http://leejjoon.github.com/pyregion/",
              license = "MIT",
              platforms = ["Linux","Mac OS X"],
              packages = ['pyregion'],
              package_dir={'pyregion':'lib'},
              )

    if WITH_FILTER:
        try:
            import numpy
        except ImportError:
            print "numpy must be installed to build the filtering module."
            print "ABORTING."
            sys.exit(1)

        try:
            numpy_include = numpy.get_include()
        except AttributeError:
            numpy_include = numpy.get_numpy_include()

        ka["ext_modules"] = [ Extension("pyregion._region_filter",
                                        [PYREX_SOURCE],
                                        include_dirs=['./src',
                                                      numpy_include,
                                                      ],
                                        libraries=[],
                                        )
                              ]


    setup(**ka)


if __name__ == "__main__":
    main()
