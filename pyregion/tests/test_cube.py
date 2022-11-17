import os
from os.path import join

from astropy.io.fits import Header
from numpy.testing import assert_allclose

from pyregion import parse


rootdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def demo_header():
    return Header.fromtextfile(join(rootdir, "sample_fits04.header"))


def test_cube():
    header = demo_header()

    region_string = 'circle(12:04:15.065,+18:26:51.00,173.029")'
    r = parse(region_string).as_imagecoord(header)

    assert_allclose(r[0].coord_list, [117, 132, 34.6], atol=0.01)
