import os
import numpy as np
from os.path import join
from astropy.io.fits import Header
from ..wcs_helper import fix_lon
from .. import open as pyregion_open

rootdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'examples')


def demo_header():
    return Header.fromtextfile(join(rootdir, "sample_fits01.header"))


def test_region():
    ref_name = "test01_img.reg"

    region_list = ["test01_fk5_sexagecimal.reg",
                   "test01_gal.reg",
                   "test01_ds9_physical.reg",
                   "test01_fk5_degree.reg",
                   "test01_mixed.reg",
                   "test01_ciao.reg",
                   "test01_ciao_physical.reg",
                   ]

    header = demo_header()

    ref_region = pyregion_open(join(rootdir, ref_name)).as_imagecoord(header)

    for reg_name in region_list:
        r = pyregion_open(join(rootdir, reg_name)).as_imagecoord(header)
        for reg0, reg in zip(ref_region, r):
            if reg.name == "rotbox":
                reg.name = "box"

            assert reg0.name == reg.name
            if reg0.name in ["ellipse", "box"]:
                assert np.allclose(reg0.coord_list[:-1], reg.coord_list[:-1],
                                   atol=0.01)
                a0 = reg0.coord_list[-1]
                a1 = fix_lon(reg.coord_list[-1], 0)
                assert np.allclose([a0], [a1], atol=0.02)
            else:
                assert np.allclose(reg0.coord_list, reg.coord_list,
                                   atol=0.01)
            assert reg0.exclude == reg.exclude
