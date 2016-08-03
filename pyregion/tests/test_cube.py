import os
from os.path import join
from astropy.io.fits import Header
from astropy.wcs import WCS
from .. import parse

rootdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'examples')


def demo_header():
    return Header.fromtextfile(join(rootdir, "sample_fits03.header"))

# 
def test_cube():

    header = demo_header()

    region_string = 'circle(12:04:15.065,+18:26:51.00,173.029")'
    parse(region_string).as_imagecoord(header)

    wcs = WCS(header)
    parse(region_string).as_imagecoord(wcs)
