from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import numpy as np
import pytest

from ..ds9_region_parser import ds9_shape_defs
from ..region_numbers import CoordOdd, CoordEven, Distance, Angle, Integer
from .. import parse
from .. import wcs_helper
from .. import wcs_converter


def test__estimate_cdelt():
    gal_center = SkyCoord('0d 0d', frame='galactic').transform_to('fk5')

    ra, dec = gal_center.ra.degree, gal_center.dec.degree

    wcs = WCS(naxis=2)

    wcs.wcs.crpix = [5.5, 5.5]
    wcs.wcs.cdelt = [0.1, -0.1]
    wcs.wcs.crval = [0, 0]
    wcs.wcs.ctype = ["GLON-ZEA".encode("ascii"), "GLAT-ZEA".encode("ascii")]

    cdelt = wcs_helper._estimate_cdelt(wcs, 5.5, 5.5)

    assert np.allclose(cdelt, 0.1)

    region_string = "fk5; circle({0}, {1}, 0.5000)".format(ra, dec)
    reg = parse(region_string).as_imagecoord(wcs)

    assert np.allclose(reg[0].coord_list[-1], 0.5 / 0.1)


def test_cdelt_poles():
    wcs = WCS(naxis=2)
    wcs.wcs.crpix = [5.5, 5.5]
    wcs.wcs.cdelt = [0.1, -0.1]
    wcs.wcs.crval = [0, 0]
    wcs.wcs.ctype = ["GLON-ZEA".encode("ascii"), "GLAT-ZEA".encode("ascii")]

    ngp = wcs.all_world2pix(0, 90, 1)
    sgp = wcs.all_world2pix(0, -90, 1)

    with pytest.raises(ValueError):
        wcs_helper._estimate_cdelt(wcs, *ngp)

    with pytest.raises(ValueError):
        wcs_helper._estimate_cdelt(wcs, *sgp)


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
