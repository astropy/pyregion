import os
from os.path import join

from astropy.io.fits import Header

import numpy as np

from .. import open as pyregion_open
from .. import get_mask

rootdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'examples')

def demo_header():
    return Header.fromtextfile(join(rootdir, "sample_fits01.header"))

def test_region():

    ref_region_name = "test01_img.reg"

    region_list = ["test01_fk5_sexagecimal.reg",
                   "test01_gal.reg",
                   "test01_ds9_physical.reg",
                   "test01_fk5_degree.reg",
                   "test01_mixed.reg",
                   "test01_ciao.reg",
                   "test01_ciao_physical.reg",
                   ]

    header = demo_header()

    ref_region = pyregion_open(join(rootdir,ref_region_name)).as_imagecoord(header)
    ref_region.get_mask(shape=(100,100))
    # for reg_name in region_list:
    #     r = pyregion_open(join(rootdir,reg_name)).as_imagecoord(header)
    #     get_mask(r)

