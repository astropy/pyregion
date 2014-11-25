import os
import numpy as np
from os.path import join
from astropy.io.fits import Header
from .. import open as pyregion_open

rootdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def demo_header():
    return Header.fromtextfile(join(rootdir, "sample_fits01.header"))


def test_region():
    ref_name = "test01_img.reg"
    header = demo_header()

    ref_region = pyregion_open(join(rootdir, ref_name)).as_imagecoord(header)
    mask = ref_region.get_mask(shape=(100, 100))

    assert isinstance(mask, np.ndarray) and mask.shape == (100, 100)

    # TODO: assert the contect of the mask, too
