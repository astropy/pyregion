import numpy as np

from .kapteyn_celestial import skymatrix, longlat2xyz, dotrans, xyz2longlat
from . import kapteyn_celestial

pywcs = None

try:
    from astropy import wcs as pywcs
except ImportError:
    try:
        import pywcs
    except ImportError:
        pass

import sys
if sys.version < '3':
    def as_str(x):
        return x
else:
    def as_str(x):
        if hasattr(x, "decode"):
            return x.decode()
        else:
            return x

FK4 = (kapteyn_celestial.equatorial, kapteyn_celestial.fk4)
FK5 = (kapteyn_celestial.equatorial, kapteyn_celestial.fk5)
GAL = kapteyn_celestial.galactic
ECL = kapteyn_celestial.ecliptic
ICRS = (kapteyn_celestial.equatorial, kapteyn_celestial.fk5) # FIXME

coord_system = dict(fk4=FK4,
                    fk5=FK5,
                    gal=GAL,
                    galactic=GAL,
                    ecl=ECL,
                    icrs=ICRS)

select_wcs = coord_system.get

UnknownWcs = "unknown wcs"

image_like_coordformats = ["image", "physical","detector","logical"]


def is_equal_coord_sys(src, dest):
    return (src.lower() == dest.lower())


def is_string_like(obj):
    'Return True if *obj* looks like a string'
    import sys
    if sys.version_info >= (3,0):
        if isinstance(obj, str): return True
    else:
        if isinstance(obj, (str, unicode)): return True
    try: obj + ''
    except: return False
    return True


class sky2sky(object):
    def __init__(self, src, dest):

        if is_string_like(src):
            src = coord_system[src.lower()]

        if is_string_like(dest):
            dest = coord_system[dest.lower()]

        self.src = src
        self.dest = dest
        self._skymatrix = skymatrix(src, dest)
        #self.tran = wcs.Transformation(src, dest)

    def inverted(self):
        return sky2sky(self.dest, self.src)

    def _dotran(self, lonlat):
        xyz = longlat2xyz(lonlat)
        xyz2 = dotrans(self._skymatrix, xyz)
        lonlats2 = xyz2longlat(xyz2)
        return lonlats2

    def __call__(self, lon, lat):
        lon, lat = np.asarray(lon), np.asarray(lat)
        lonlat = np.concatenate([lon[:,np.newaxis],
                                 lat[:,np.newaxis]],1)
        ll_dest = np.asarray(self._dotran(lonlat))
        return ll_dest[:,0], ll_dest[:,1]

import re
_pattern_ra = re.compile(r"^RA")
_pattern_dec = re.compile(r"^DEC")
_pattern_glon = re.compile(r"^GLON")
_pattern_glat = re.compile(r"^GLAT")
_pattern_vel = re.compile(r"^VEL")

def coord_system_guess(ctype1_name, ctype2_name, equinox):
    if ctype1_name.upper().startswith("RA") and \
       ctype2_name.upper().startswith("DEC"):
        if equinox == 2000.0:
            return "fk5"
        elif equinox == 1950.0:
            return "fk4"
        elif equinox is None or np.isnan(equinox):
            return "fk5"
        else:
            return None
    if ctype1_name.upper().startswith("GLON") and \
       ctype2_name.upper().startswith("GLAT"):
        return "gal"
    elif ctype1_name.upper().startswith("ELON") and \
       ctype2_name.upper().startswith("ELAT"):
        return "ecl"



    return None


def fix_header(header):
    "return a new fixed header"

    if hasattr(header, "cards"):
        old_cards = header.cards
    else:
        old_cards = header.ascardlist()

    new_cards = []

    from operator import attrgetter
    if old_cards and hasattr(old_cards[0], "keyword"):
        get_key = attrgetter("keyword")
    else:
        get_key = attrgetter("key")

    for c in old_cards:
        key = get_key(c)

        # ignore comments and history
        if key in ["COMMENT", "HISTORY"]:
            continue

        # use "deg"
        if key.startswith("CUNIT") and c.value.lower().startswith("deg"):
            c = type(c)(key, "deg")

        new_cards.append(c)

    h = type(header)(new_cards)
    return h


def fix_lon(lon, lon_ref):
    lon_ = lon - lon_ref
    lon2 = lon_ - 360*np.floor_divide(lon_, 360.)
    if lon_ == 360:
        lon2 = 360
    return lon2 + lon_ref


class ProjectionBase(object):
    """
    A wrapper for kapteyn.projection or pywcs
    """

    def __init__(self):
        self._lon_ref = None

        for i, ct in enumerate(self.ctypes):
            ct = ct.upper()
            if _pattern_ra.match(ct) or _pattern_glon.match(ct):
                self._lon_axis = i
                break
        else:
            self._lon_axis = None

    def get_lon(self):
        pass


    def set_lon_ref(self, ref):
        self._lon_ref = ref

    def _fix_lon(self, lon, lon_ref=None):
        """
        transform lon into values in range [self._lon_ref, self._lon_ref+360]
        """
        if lon_ref is None:
            lon_ref = self._lon_ref

        if lon_ref is not None:
            lon_ = lon - lon_ref
            lon2 = lon_ - 360*np.floor_divide(lon_, 360.)
            lon2[lon_==360] = 360
            return lon2 + lon_ref
        else:
            return lon

    def fix_lon(self, lon_lat):
        """
        """
        if self._lon_axis is not None:
            lon_lat[self._lon_axis] = self._fix_lon(lon_lat[self._lon_axis])

    # def _get_ctypes(self):
    #     pass

    # def _get_equinox(self):
    #     pass

    # def _get_naxis(self):
    #     pass


    def topixel(self):
        """ 1, 1 base """
        pass

    def toworld(self):
        """ 1, 1 base """
        pass

    def sub(self, axes):
        pass

    def _get_radesys(self):
        ctype1, ctype2 = self.ctypes
        equinox = self.equinox
        radecsys = coord_system_guess(ctype1, ctype2, equinox)
        if radecsys is None:
            raise RuntimeError("Cannot determine the coordinate system with (CTYPE1=%s, CTYPE2=%s, EQUINOX=%s)." % (ctype1, ctype2, equinox))
        return radecsys

    radesys = property(_get_radesys)


class _ProjectionSubInterface:
    def substitute(self, axis_nums_to_keep, ref_pixel):
        for i in axis_nums_to_keep:
            if i >= self.naxis:
                raise ValueError("Incorrect axis number")

        if axis_nums_to_keep == range(self.naxis):
            return self

        proj_sub = ProjectionPywcsSub(self, axis_nums_to_keep, ref_pixel)
        return proj_sub

    def sub(self, axes):
        axis_nums_to_keep = [i-1 for i in axes]
        return self.substitute(axis_nums_to_keep, [0] * self.naxis)


class ProjectionPywcsNd(_ProjectionSubInterface, ProjectionBase):
    """
    A wrapper for pywcs
    """
    def __init__(self, header):
        """
        header could be pyfits.Header instance of pywcs.WCS instance.
        """

        # We can't check the header type using isinstance since we don't know
        # if it comes from PyFITS or Astropy, so instead we check if it has
        # the 'ascard' attribute that both header classes define.

        if hasattr(header, 'ascard'):

            header = fix_header(header)

            # Since we don't know if PyFITS or PyWCS are from Astropy, and the
            # WCS object in PyWCS and Astropy both accept a string
            # representation of the header, we use this instead (both
            # internally use `repr(header.ascard)` which returns str,
            # and is compatible with Python 3

            header = repr(header.ascard).encode('latin1')

            self._pywcs = pywcs.WCS(header=header)

        elif hasattr(header, "wcs"):
            self._pywcs = header
        else:

            raise ValueError("header must be an instance of pyfits.Header or astropy.io.fits.Header")

        ProjectionBase.__init__(self)

    def _get_ctypes(self):
        return tuple(as_str(s) for s in self._pywcs.wcs.ctype)

    ctypes = property(_get_ctypes)

    def _get_equinox(self):
        return self._pywcs.wcs.equinox

    equinox = property(_get_equinox)

    def _get_naxis(self):
        return self._pywcs.wcs.naxis

    naxis = property(_get_naxis)


    def topixel(self, xy):
        """ 1, 1 base """

        lon_lat = np.array(xy)

        self.fix_lon(lon_lat)

        xy1 = lon_lat.transpose()

        # somehow, wcs_world2pix does not work for some cases
        xy21 = [self._pywcs.wcs_world2pix([xy11], 1)[0] for xy11 in xy1]
        #xy21 = self._pywcs.wcs_world2pix(xy1, 1)

        xy2 = np.array(xy21).transpose()
        return xy2

    def toworld(self, xy):
        """ 1, 1 base """
        xy2 = self._pywcs.wcs_pix2world(np.asarray(xy).T, 1)

        lon_lat = xy2.T
        # fixme
        self.fix_lon(lon_lat)

        return lon_lat

    #def sub(self, axes):
    #    wcs = self._pywcs.sub(axes=axes)
    #    return ProjectionPywcs(wcs)



class ProjectionPywcsSub(_ProjectionSubInterface, ProjectionBase):
    """
    A wrapper for pywcs
    """
    def __init__(self, proj, axis_nums_to_keep, ref_pixel):
        """
        ProjectionPywcsSub(proj, [0, 1], (0, 0, 0))
        """
        self.proj = proj

        self._nsub = len(axis_nums_to_keep)
        self._axis_nums_to_keep = axis_nums_to_keep[:]

        self._ref_pixel = ref_pixel

        _ref_pixel0 = np.array(ref_pixel).reshape((len(ref_pixel),1))
        _ref_world0 = np.asarray(proj.toworld(_ref_pixel0))
        self._ref_world = _ref_world0.reshape((len(ref_pixel),))

        ProjectionBase.__init__(self)


    def _get_ctypes(self):
        return [self.proj.ctypes[i] for i in self._axis_nums_to_keep]

    ctypes = property(_get_ctypes)

    def _get_equinox(self):
        return self.proj.equinox

    equinox = property(_get_equinox)

    def _get_naxis(self):
        #return self.proj.naxis - self._nsub
        return self._nsub

    naxis = property(_get_naxis)

    def topixel(self, xy):
        """ 1, 1 base """
        template = xy[0]
        iter_xy = iter(xy)

        xyz = [None]*self.proj.naxis
        for i in self._axis_nums_to_keep:
            xyz[i] = next(iter_xy)
        for i in range(self.proj.naxis):
            if i not in self._axis_nums_to_keep:
                s = np.empty_like(template)
                s.fill(self._ref_world[i])
                xyz[i] = s

        #xyz2 = self._pywcs.wcs_world2pix(np.asarray(xyz).T, 1)
        xyz2 = self.proj.topixel(np.array(xyz))

        #xyz2r = [d for (i, d) in enumerate(xyz2) if i in self._axis_nums_to_keep]
        xyz2r = [xyz2[i] for i in self._axis_nums_to_keep]

        return xyz2r


    def toworld(self, xy):
        """ 1, 1 base """
        template = xy[0]
        iter_xy = iter(xy)


        xyz = [None]*self.proj.naxis
        for i in self._axis_nums_to_keep:
            xyz[i] = next(iter_xy)
        for i in range(self.proj.naxis):
            if i not in self._axis_nums_to_keep:
                s = np.empty_like(template)
                s.fill(self._ref_pixel[i])
                xyz[i] = s

        xyz2 = self.proj.toworld(np.asarray(xyz))
        xyz2r = [xyz2[i] for i in self._axis_nums_to_keep]

        # fixme
        #xyz2r[0] = self._fix_lon(xyz2r[0])

        return xyz2r


class ProjectionPywcs(ProjectionBase):
    """
    A wrapper for pywcs
    """
    def __init__(self, header):
        if hasattr(header, "ascard"):
            self._pywcs = pywcs.WCS(header=header)
        else:
            self._pywcs = header
        ProjectionBase.__init__(self)

    def _get_ctypes(self):
        return tuple(as_str(s) for s in self._pywcs.wcs.ctype)

    ctypes = property(_get_ctypes)

    def _get_equinox(self):
        return self._pywcs.wcs.equinox

    equinox = property(_get_equinox)

    def topixel(self, xy):
        """ 1, 1 base """
        xy2 = self._pywcs.wcs_world2pix(np.asarray(xy).T, 1)
        return xy2.T[:2]

    def toworld(self, xy):
        """ 1, 1 base """
        xy2 = self._pywcs.wcs_pix2world(np.asarray(xy).T, 1)
        return xy2.T[:2]

    def sub(self, axes):
        wcs = self._pywcs.sub(axes=axes)
        return ProjectionPywcs(wcs)


class ProjectionSimple(ProjectionBase):
    """
    A wrapper for pywcs
    """
    def __init__(self, header):
        ProjectionBase.__init__(self)
        self._pywcs = pywcs.WCS(header=header)
        self._simple_init(header)

    def _get_ctypes(self):
        return tuple(as_str(s) for s in self._pywcs.wcs.ctype)

    ctypes = property(_get_ctypes)

    def _get_equinox(self):
        return self._pywcs.wcs.equinox

    equinox = property(_get_equinox)

    def _get_naxis(self):
        return self._pywcs.wcs.naxis

    naxis = property(_get_naxis)

    def _simple_init(self, header):
        self.crpix1 = header["CRPIX1"]
        self.crval1 = header["CRVAL1"]
        self.cdelt1 = header["CDELT1"]

        self.crpix2 = header["CRPIX2"]
        self.crval2 = header["CRVAL2"]
        self.cdelt2 = header["CDELT2"]

        self.cos_phi = np.cos(self.crval2/180.*np.pi)

    def _simple_to_pixel(self, lon, lat):
        lon, lat = np.asarray(lon), np.asarray(lat)

        lon = self._fix_lon(lon)

        x = (lon - self.crval1)/self.cdelt1*self.cos_phi + self.crpix1
        y = (lat - self.crval2)/self.cdelt2 + self.crpix2

        return x, y

    def _simple_to_world(self, x, y):
        x, y = np.asarray(x), np.asarray(y)
        lon = (x - self.crpix1)*self.cdelt1/self.cos_phi + self.crval1
        lat = (y - self.crpix2)*self.cdelt2 + self.crval2

        lon = self._fix_lon(lon)

        return lon, lat

    def topixel(self, xy):
        """ 1, 1 base """
        lon, lat = xy[0], xy[1]
        x, y = self._simple_to_pixel(lon, lat)
        return np.array([x, y])


    def toworld(self, xy):
        """ 1, 1 base """
        x, y = xy[0], xy[1]
        lon, lat = self._simple_to_world(x, y)
        return np.array([lon, lat])

    def substitute(self, axis_nums, values):
        return self

    def sub(self, axis_nums):
        return self

    # def sub(self, axes):
    #     wcs = self._pywcs.sub(axes=axes)
    #     return ProjectionPywcs(wcs)


ProjectionDefault = ProjectionPywcsNd

def get_kapteyn_projection(header):
    if isinstance(header, ProjectionBase):
        projection = header
    else:
        projection = ProjectionPywcsNd(header)

    #projection = projection.sub(axes=[1,2])
    return projection


def estimate_cdelt_trans(transSky2Pix, x0, y0):

    transPix2Sky = transSky2Pix.inverted()

    lon0, lat0 = transPix2Sky.transform_point((x0, y0))

    lon1, lat1 = transPix2Sky.transform_point((x0+1, y0))
    dlon = (lon1-lon0)*np.cos(lat0/180.*np.pi)
    dlat = (lat1-lat0)
    cd1 = (dlon**2 + dlat**2)**.5

    lon2, lat2 = transPix2Sky.transform_point((x0, y0+1))
    dlon = (lon2-lon0)*np.cos(lat0/180.*np.pi)
    dlat = (lat2-lat0)
    cd2 = (dlon**2 + dlat**2)**.5

    return (cd1*cd2)**.5






def estimate_angle_trans(transSky2Pix, x0, y0):
    """
    return a tuple of two angles (in degree) of increasing direction
    of 1st and 2nd coordinates.

    note that x, y = wcs_proj.topixel(sky_to_sky((l1, l2)))

    """

    cdelt = estimate_cdelt_trans(transSky2Pix, x0, y0)

    transPix2Sky = transSky2Pix.inverted()

    lon0, lat0 = transPix2Sky.transform_point((x0, y0))

    x1, y1 = transSky2Pix.transform_point((lon0 + cdelt*np.cos(lat0/180.*np.pi),
                                           lat0))

    x2, y2 = transSky2Pix.transform_point((lon0, lat0+cdelt))

    a1 = np.arctan2(y1-y0, x1-x0)/np.pi*180.
    a2 = np.arctan2(y2-y0, x2-x0)/np.pi*180.

    return a1, a2


def estimate_cdelt(wcs_proj, x0, y0): #, sky_to_sky):
    lon0, lat0 = wcs_proj.toworld(([x0], [y0]))

    if lat0 == 90 or lat0 == -90:
        raise ValueError("estimate_cdelt does not work at poles.")

    lon_ref = lon0 - 180.

    lon1, lat1 = wcs_proj.toworld(([x0+1], [y0]))
    lon1 = fix_lon(lon1, lon_ref)
    dlon = (lon1[0]-lon0[0])*np.cos(lat0[0]/180.*np.pi)
    dlat = (lat1[0]-lat0[0])
    cd1 = (dlon**2 + dlat**2)**.5

    lon2, lat2 = wcs_proj.toworld(([x0], [y0+1]))
    lon2 = fix_lon(lon2, lon_ref)
    dlon = (lon2[0]-lon0[0])*np.cos(lat0[0]/180.*np.pi)
    dlat = (lat2[0]-lat0[0])
    cd2 = (dlon**2 + dlat**2)**.5

    return ((cd1*cd2)**.5)


def estimate_angle(wcs_proj, x0, y0, sky_to_sky=None):
    """
    return a tuple of two angles (in degree) of increasing direction
    of 1st and 2nd coordinates.

    note that x, y = wcs_proj.topixel(sky_to_sky((l1, l2)))

    """

    cdelt = estimate_cdelt(wcs_proj, x0, y0)

    #x0, y0 = wcs_proj.topixel((lon0, lat0))
    ll = wcs_proj.toworld(([x0], [y0]))
    lon0, lat0 = sky_to_sky.inverted()(ll[0], ll[1])

    ll = sky_to_sky(lon0 + cdelt*np.cos(lat0/180.*np.pi), lat0)
    x1, y1 = wcs_proj.topixel(ll)
    a1 = np.arctan2(y1-y0, x1-x0)/np.pi*180.

    ll = sky_to_sky(lon0, lat0+cdelt)
    x2, y2 = wcs_proj.topixel(ll)
    a2 = np.arctan2(y2-y0, x2-x0)/np.pi*180.

    return a1[0], a2[0]



if __name__ == "__main__":
    fk5_to_fk4 = sky2sky(FK5, FK4)
    #print fk5_to_fk4([47.37], [6.32])
    #print fk5_to_fk4([47.37, 47.37], [6.32, 6.32])
    #print sky2sky("fk5", "FK4")([47.37, 47.37], [6.32, 6.32])
