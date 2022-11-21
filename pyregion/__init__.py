"""
pyregion: a Python parser for ds9 region files

* Code : https://github.com/astropy/pyregion
* Docs : http://pyregion.readthedocs.io/

See also the in-development ``regions`` package
at https://github.com/astropy/regions
a new astronomy package for regions based on Astropy.
"""

from .core import *
from .core import open
from .parser_helper import Shape
from .version import __version__
