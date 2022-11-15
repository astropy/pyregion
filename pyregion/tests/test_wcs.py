import pytest
import os.path
from numpy.testing import assert_allclose
from astropy.io.fits import Header
from pyregion.ds9_region_parser import ds9_shape_defs
from pyregion.region_numbers import CoordOdd, CoordEven
from pyregion import wcs_converter
from pyregion.wcs_helper import _calculate_rotation_angle


rootdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def test__generate_arg_types_min_list():
    for name, shape in ds9_shape_defs.items():
        args_list = shape.args_list
        min_list = wcs_converter._generate_arg_types(len(args_list), name)
        for expected_arg, tested_arg in zip(args_list, min_list):
            assert expected_arg == tested_arg


@pytest.mark.parametrize(("name", "length", "result"), [
    ("polygon", 6, 3 * [CoordOdd, CoordEven]),
])
def test__generate_arg_types_with_repeats(name, length, result):
    test_list = wcs_converter._generate_arg_types(length, name)

    for expected_arg, tested_arg in zip(result, test_list):
        assert expected_arg == tested_arg


@pytest.mark.parametrize(("region_frame", "header_name", "rot_angle"), [
    ('fk5', 'sample_fits01.header', 0.00505712),
    ('galactic', 'sample_fits01.header', -19.2328),
    ('fk4', 'sample_fits01.header', -0.0810223),
    ('fk5', 'sample_fits03.header', -2.16043),
])
def test_calculate_rotation_angle(region_frame, header_name, rot_angle):
    header = Header.fromtextfile(os.path.join(rootdir, header_name))
    assert_allclose(
        _calculate_rotation_angle(region_frame, header), rot_angle,
        atol=0.001
    )
