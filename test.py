import pytest

lib_files_with_test = ["lib/ds9_region_parser.py",
                       "lib/region_numbers.py",
                       "lib/ds9_attr_parser.py",
                       "lib/parser_helper.py"]

pytest.main(lib_files_with_test + ['tests'])
