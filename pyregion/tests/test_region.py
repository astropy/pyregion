import os
from os.path import join
from astropy.io.fits import Header
from astropy.wcs import WCS
from .. import open as pyregion_open
import pytest
import numpy as np
from numpy.testing import assert_allclose

rootdir = join(os.path.dirname(os.path.abspath(__file__)), 'data')


@pytest.fixture(scope="module")
def header():
    return Header.fromtextfile(join(rootdir, "sample_fits01.header"))


@pytest.mark.parametrize(("ref_name", "reg_name", "header_name"), [
    ("test01_img.reg", "test01_fk5_sexagecimal.reg", "sample_fits01.header"),
    ("test01_img.reg", "test01_gal.reg", "sample_fits01.header"),
    ("test01_img.reg", "test01_ds9_physical.reg", "sample_fits01.header"),
    ("test01_img.reg", "test01_fk5_degree.reg", "sample_fits01.header"),
    ("test01_img.reg", "test01_mixed.reg", "sample_fits01.header"),
    ("test01_img.reg", "test01_ciao.reg", "sample_fits01.header"),
    ("test01_img.reg", "test01_ciao_physical.reg", "sample_fits01.header"),
    ("test01_img.reg", "test01_fk5.reg", "sample_fits01.header"),
    ("test01_img.reg", "test01_fk4.reg", "sample_fits01.header"),
    ("test01_img.reg", "test01_icrs.reg", "sample_fits01.header"),
    ("test02_1_img.reg", "test02_1_fk5.reg", "sample_fits02.header"),
    ("test_annuli.reg", "test_annuli_wcs.reg", "sample_fits01.header"),
    pytest.mark.xfail(("test03_img.reg", "test03_fk5.reg", "sample_fits03.header")),
    pytest.mark.xfail(("test03_img.reg", "test03_icrs.reg", "sample_fits03.header")),
    ("test03_img.reg", "test03_ciao_physical.reg", "sample_fits03.header"),
])
def test_region(ref_name, reg_name, header_name):
    header = Header.fromtextfile(join(rootdir, header_name))
    ref_region = pyregion_open(join(rootdir, ref_name)).as_imagecoord(header)

    r = pyregion_open(join(rootdir, reg_name)).as_imagecoord(header)

    assert len(r) == len(ref_region)

    for ref_reg, reg in zip(ref_region, r):
        if reg.name == "rotbox":
            reg.name = "box"

        assert ref_reg.name == reg.name

        # Normalize everything like angles
        ref_list = np.asarray(ref_reg.coord_list)
        reg_list = np.asarray(reg.coord_list)
        assert_allclose((ref_list + 180) % 360 - 180, (reg_list + 180) % 360 - 180,
                        atol=0.6)

        assert ref_reg.exclude == reg.exclude


@pytest.mark.parametrize(("reg_name"), [
    ("test_annuli_ciao.reg"), # subset of test03_img.reg
    ("test_context.reg"),
    ("test02.reg"),
    ("test04_img.reg"),
    ("test_text.reg"),
    ("test01.reg"),
])
def test_open_regions(reg_name, header):
    # TODO: Better test. Like figure out how these files relate to each other
    pyregion_open(join(rootdir, reg_name)).as_imagecoord(header)


@pytest.mark.parametrize(("ref_name", "reg_name"), [
    ("test01_img.reg", "test01_gal.reg"),
    ("test01_img.reg", "test01_fk5_degree.reg"),
    ("test01_img.reg", "test01_fk5.reg"),
])
def test_open_imagecoord_from_wcs(ref_name, reg_name, header):
    ref_region = pyregion_open(join(rootdir, ref_name)).as_imagecoord(header)

    r = pyregion_open(join(rootdir, reg_name)).as_imagecoord(WCS(header))
    for ref_reg, reg in zip(ref_region, r):
        if reg.name == "rotbox":
            reg.name = "box"

        assert ref_reg.name == reg.name
        ref_list = np.asarray(ref_reg.coord_list)
        reg_list = np.asarray(reg.coord_list)
        assert_allclose((ref_list + 180) % 360 - 180, (reg_list + 180) % 360 - 180,
                        atol=0.1)
        assert ref_reg.exclude == reg.exclude
