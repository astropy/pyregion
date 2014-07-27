from setuptools import setup, Extension

# check if cython or pyrex is available.
pyrex_impls = 'Cython.Distutils.build_ext', 'Pyrex.Distutils.build_ext'
for pyrex_impl in pyrex_impls:
    try:
        # from (pyrex_impl) import build_ext
        build_ext = __import__(pyrex_impl, fromlist=['build_ext']).build_ext
        break
    except:
        pass
have_pyrex = 'build_ext' in globals()

if have_pyrex:
    cmdclass = {'build_ext': build_ext}
    PYREX_SOURCE = "src/_region_filter.pyx"
else:
    cmdclass = {}
    PYREX_SOURCE = "src/_region_filter.c"

import sys
import warnings

# If you don't want to build filtering module (which requires a C
# compiler), set it to False
WITH_FILTER = True

for line in open('lib/version.py').readlines():
    if (line.startswith('__version__')):
        exec(line.strip())

def main():
    if sys.version_info[0] >= 3:
        install_requires = ['pyparsing>=2.0.0']
    elif sys.version_info[:2] >= (2, 6):
        # For Python 2.6 and 2.7, any version *except* 2.0.0 will work
        install_requires = ['pyparsing!=2.0.0']
    else:
        # For Python < 2.6, a version before 2.0.0 is required
        install_requires = ['pyparsing<2.0.0']

    ka = dict(name = "pyregion",
              version = __version__,
              description = "python parser for ds9 region files",
              author = "Jae-Joon Lee",
              author_email = "lee.j.joon@gmail.com",
              url="http://leejjoon.github.com/pyregion/",
              download_url="http://github.com/leejjoon/pyregion/downloads",
              license = "MIT",
              platforms = ["Linux","MacOS X"],
              packages = ['pyregion'],
              package_dir={'pyregion':'lib'},
              install_requires = install_requires,
              use_2to3 = False,
              )
    ka["classifiers"]=['Development Status :: 5 - Production/Stable',
                       'Intended Audience :: Science/Research',
                       'License :: OSI Approved :: MIT License',
                       'Operating System :: MacOS :: MacOS X',
                       'Operating System :: POSIX :: Linux',
                       'Programming Language :: Cython',
                       'Programming Language :: Python',
                       'Programming Language :: Python :: 3',
                       'Topic :: Scientific/Engineering :: Astronomy',
                       ]

    if WITH_FILTER:
        try:
            import numpy
        except ImportError:
            warnings.warn("numpy must be installed to build the filtering module.")
            sys.exit(1)

        try:
            numpy_include = numpy.get_include()
        except AttributeError:
            numpy_include = numpy.get_numpy_include()

        if cmdclass:
            ka["cmdclass"] = cmdclass

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
