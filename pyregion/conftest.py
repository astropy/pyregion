# this contains imports plugins that configure py.test for astropy tests.
# by importing them here in conftest.py they are discoverable by py.test
# no matter how it is invoked within the source tree.

import os

from astropy.version import version as astropy_version
if astropy_version < '3.0':
    from astropy.tests.pytest_plugins import *
    del pytest_report_header
else:
    from pytest_astropy_header.display import PYTEST_HEADER_MODULES, TESTED_VERSIONS


def pytest_configure(config):

    config.option.astropy_header = True

    PYTEST_HEADER_MODULES.clear()
    PYTEST_HEADER_MODULES.update([
        ('numpy', 'numpy'),
        ('cython', 'cython'),
        ('Astropy', 'astropy'),
        ('pyparsing', 'pyparsing'),
        ('matplotlib', 'matplotlib'),
    ])

    from .version import version, astropy_helpers_version
    packagename = os.path.basename(os.path.dirname(__file__))
    TESTED_VERSIONS[packagename] = version
    TESTED_VERSIONS['astropy_helpers'] = astropy_helpers_version
