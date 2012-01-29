import pytest

import pyregion
import os

basedir = os.path.dirname(pyregion.__file__)

lib_files_with_test = ["ds9_region_parser.py",
                       "region_numbers.py",
                       "ds9_attr_parser.py",
                       "parser_helper.py"]

pytest.main([os.path.join(basedir, f) for f in lib_files_with_test] \
            + ['tests'])
