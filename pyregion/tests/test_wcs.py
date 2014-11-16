from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import numpy as np
import pytest

from ..ds9_region_parser import ds9_shape_defs
from ..region_numbers import CoordOdd, CoordEven, Distance, Angle, Integer
from .. import parse
from .. import wcs_helper
from .. import wcs_converter


def test__generate_arg_types_min_list():
    for name, shape in ds9_shape_defs.items():
        args_list = shape.args_list
        min_list = wcs_converter._generate_arg_types(len(args_list), name)
        for expected_arg, tested_arg in zip(args_list, min_list):
            assert expected_arg == tested_arg


@pytest.mark.parametrize(("name", "length", "result"), [
    ("polygon", 6, 3*[CoordOdd, CoordEven]),
])
def test__generate_arg_types_with_repeats(name, length, result):
    test_list = wcs_converter._generate_arg_types(length, name)

    for expected_arg, tested_arg in zip(result, test_list):
        assert expected_arg == tested_arg
