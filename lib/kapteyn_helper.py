from kapteyn import wcs
import numpy as np
from matplotlib.cbook import is_string_like

FK4 = (wcs.equatorial, wcs.fk4, 'B1950.0')
FK5 = (wcs.equatorial, wcs.fk5, 'J2000.0')
GAL = wcs.galactic

coord_system = dict(fk4=FK4,
                    fk5=FK5,
                    gal=GAL)

def is_equal_coord_sys(src, dest):
    return (src.lower() == dest.lower())

class sky2sky(object):
    def __init__(self, src, dest):

        if is_string_like(src):
            src = coord_system[src.lower()]

        if is_string_like(dest):
            dest = coord_system[dest.lower()]

        self.src = src
        self.dest = dest
        self.tran = wcs.Transformation(src, dest)

    def inverted(self):
        return sky2sky(self.dest, self.src)

    def __call__(self, lon, lat=None):
        if lat is None:
            ll_src = lon
            ll_dest = self.tran(ll_src)
            return ll_dest
        else:
            lon, lat = np.asarray(lon), np.asarray(lat)
            ll_src = np.concatenate([lon[:,np.newaxis],
                                     lat[:,np.newaxis]],1)
            ll_dest = self.tran(ll_src)
            return ll_dest[:,0], ll_dest[:,1]


def coord_system_guess(ctype1_name, ctype2_name, equinox):
    if ctype1_name.upper().startswith("RA") and \
       ctype2_name.upper().startswith("DEC"):
        if equinox == 2000.0:
            return "fk5"
        elif equinox == 1950.0:
            return "fk4"
        elif equinox is None:
            return "fk5"
        else:
            return None
    if ctype1_name.upper().startswith("GLON") and \
       ctype2_name.upper().startswith("GLAT"):
        return "gal"
    return None

import kapteyn.wcs
import pyfits

def get_kapteyn_projection(header):
    if isinstance(header, kapteyn.wcs.Projection):
        projection = header
    elif hasattr(header, "wcs") and hasattr(header.wcs, "to_header"):
        # pywcs
        naxis = header.naxis
        header = header.wcs.to_header()
        cards = pyfits.CardList()
        for i in range(0, len(header), 80):
            card_string = header[i:i+80]
            card = pyfits.Card()
            card.fromstring(card_string)
            cards.append(card)
        h = pyfits.Header(cards)
        h.update("NAXIS", naxis)
        projection = kapteyn.wcs.Projection(h)
    else:
        projection = kapteyn.wcs.Projection(header)

    projection = projection.sub(axes=[1,2])
    return projection



if __name__ == "__main___":
    fk5_to_fk4 = sky2sky(FK5, FK4)
    print fk5_to_fk4((47.37, 6.32))
    print fk5_to_fk4([47.37, 47.37], [6.32, 6.32])
    print sky2sky("fk5", "FK4")([47.37, 47.37], [6.32, 6.32])


