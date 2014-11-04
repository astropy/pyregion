import numpy as np
from astropy.wcs import WCS
from .. import parse
from .. import wcs_helper


def test_estimate_cdelt():
    l, b = 0, 0

    # This is the ra,dec of l,b=0,0
    ra, dec = 266.404497776, -28.9364329295

    # This is 'almost' the ra,dec of l,b=0,0 - works
    # ra,dec=266.40,-28.93

    wcs = WCS(naxis=2)

    wcs.wcs.crpix = [5.5, 5.5]
    wcs.wcs.cdelt = [0.1, -0.1]
    wcs.wcs.crval = [l, b]
    wcs.wcs.ctype = ["GLON-ZEA".encode("ascii"), "GLAT-ZEA".encode("ascii")]

    proj = wcs_helper.get_kapteyn_projection(wcs)
    cdelt = wcs_helper.estimate_cdelt(proj, 5.5, 5.5)

    assert np.allclose([cdelt], [0.1])

    region_string = "fk5; circle({0}, {1}, 0.5000)".format(ra, dec)
    reg = parse(region_string).as_imagecoord(wcs)

    assert np.allclose([reg[0].coord_list[-1]], [0.5 / 0.1])
