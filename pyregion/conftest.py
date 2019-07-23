# this contains imports plugins that configure py.test for astropy tests.
# by importing them here in conftest.py they are discoverable by py.test
# no matter how it is invoked within the source tree.

from astropy.version import version as astropy_version
if astropy_version < '3.0':
    # With older versions of Astropy, we actually need to import the pytest
    # plugins themselves in order to make them discoverable by pytest.
    from astropy.tests.pytest_plugins import *
else:
    # As of Astropy 3.0, the pytest plugins provided by Astropy are
    # automatically made available when Astropy is installed. This means it's
    # not necessary to import them here, but we still need to import global
    # variables that are used for configuration.
    from astropy.tests.plugins.display import PYTEST_HEADER_MODULES, TESTED_VERSIONS

from astropy.tests.helper import enable_deprecations_as_exceptions

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
