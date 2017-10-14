# this contains imports plugins that configure py.test for astropy tests.
# by importing them here in conftest.py they are discoverable by py.test
# no matter how it is invoked within the source tree.

from astropy.tests.pytest_plugins import *

# Uncomment the following line to treat all DeprecationWarnings as exceptions
enable_deprecations_as_exceptions()

PYTEST_HEADER_MODULES.clear()
PYTEST_HEADER_MODULES.update([
    ('numpy', 'numpy'),
    ('cython', 'cython'),
    ('Astropy', 'astropy'),
    ('pyparsing', 'pyparsing'),
    ('matplotlib', 'matplotlib'),
])

# This is to figure out the affiliated package version, rather than
# using Astropy's
try:
    from .version import version
except ImportError:
    version = 'dev'

import os
packagename = os.path.basename(os.path.dirname(__file__))
TESTED_VERSIONS[packagename] = version
