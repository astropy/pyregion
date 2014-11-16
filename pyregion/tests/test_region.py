import os
from os.path import join
from astropy.io.fits import Header
from .. import open as pyregion_open
import pytest
from numpy.testing import assert_allclose

rootdir = join(os.path.dirname(os.path.abspath(__file__)), 'examples')


@pytest.fixture(scope="module")
def header():
    return Header.fromtextfile(join(rootdir, "sample_fits01.header"))


@pytest.mark.parametrize(("ref_name", "reg_name"), [
    ("test01_img.reg", "test01_fk5_sexagecimal.reg"),
    ("test01_img.reg", "test01_gal.reg"),
    ("test01_img.reg", "test01_ds9_physical.reg"),
    ("test01_img.reg", "test01_fk5_degree.reg"),
    ("test01_img.reg", "test01_mixed.reg"),
    ("test01_img.reg", "test01_ciao.reg"),
    ("test01_img.reg", "test01_ciao_physical.reg"),
    ("test01_img.reg", "test01_fk5.reg"),
])
def test_region(ref_name, reg_name, header):
    ref_region = pyregion_open(join(rootdir, ref_name)).as_imagecoord(header)

    r = pyregion_open(join(rootdir, reg_name)).as_imagecoord(header)
    for ref_reg, reg in zip(ref_region, r):
        if reg.name == "rotbox":
            reg.name = "box"

        assert ref_reg.name == reg.name
        assert_allclose(ref_reg.coord_list, reg.coord_list, atol=0.02)
        assert ref_reg.exclude == reg.exclude


@pytest.mark.parametrize(("reg_name"), [
    ("test_annuli_ciao.reg"),
    ("test_annuli.reg"),
    ("test_annuli_wcs.reg"),
    ("test_context.reg"),
    ("test02.reg"),
    ("test04_img.reg"),
    ("test.reg"),
    ("test_text.reg"),
])
def test_open_regions(reg_name, header):
    # TODO: Better test. Like figure out how these files relate to each other
    r = pyregion_open(join(rootdir, reg_name)).as_imagecoord(header)
