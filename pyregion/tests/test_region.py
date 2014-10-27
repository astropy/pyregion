from os.path import join

try:
    from astropy.io import fits as pyfits
except ImportError:
    import pyfits

import numpy as np

from ..wcs_helper import fix_lon
from .. import open as pyregion_open

# At some point, pyfits.Card.fromstring has changed from unbound
# method to bounded method.

if pyfits.Card.fromstring.__self__: # 
    def pyfits_card_fromstring(l):
        return pyfits.Card.fromstring(l)
else:
    def pyfits_card_fromstring(l):
        c = pyfits.Card()
        return c.fromstring(l)

rootdir = "examples"

def demo_header():
    cards = pyfits.CardList()
    for l in open(join(rootdir, "sample_fits01.header")):
        card = pyfits_card_fromstring(l.strip())
        cards.append(card)
    h = pyfits.Header(cards)
    return h

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

    for reg_name in region_list:
        r = pyregion_open(join(rootdir,reg_name)).as_imagecoord(header)
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
        
