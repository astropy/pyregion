"""
pyregion: a Python parser for ds9 region files

* Code : https://github.com/astropy/pyregion
* Docs : http://pyregion.readthedocs.io/

See also the in-development ``regions`` package
at https://github.com/astropy/regions
a new astronomy package for regions based on Astropy.
"""

# Affiliated packages may add whatever they like to this file, but
# should keep this content at the top.
# ----------------------------------------------------------------------------
from ._astropy_init import *

# For egg_info test builds to pass, put package imports here.
if not _ASTROPY_SETUP_:
    from .core import *
    from .parser_helper import Shape
