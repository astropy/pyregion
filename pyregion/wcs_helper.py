import re
import numpy as np
from astropy.extern import six
from astropy.wcs import WCS
from astropy.io.fits import Header
from .extern.kapteyn_celestial import skymatrix, longlat2xyz, dotrans, xyz2longlat
from .extern import kapteyn_celestial

_pattern_ra = re.compile(r"^RA")
_pattern_dec = re.compile(r"^DEC")
_pattern_glon = re.compile(r"^GLON")
_pattern_glat = re.compile(r"^GLAT")
_pattern_vel = re.compile(r"^VEL")

FK4 = (kapteyn_celestial.equatorial, kapteyn_celestial.fk4)
FK5 = (kapteyn_celestial.equatorial, kapteyn_celestial.fk5)
GAL = kapteyn_celestial.galactic
ECL = kapteyn_celestial.ecliptic
ICRS = (kapteyn_celestial.equatorial, kapteyn_celestial.fk5)  # FIXME

coord_system = dict(fk4=FK4,
                    fk5=FK5,
                    gal=GAL,
                    galactic=GAL,
                    ecl=ECL,
                    icrs=ICRS)

select_wcs = coord_system.get

UnknownWcs = "unknown wcs"

image_like_coordformats = ["image", "physical", "detector", "logical"]


class sky2sky(object):
    def __init__(self, src, dest):
        if isinstance(src, six.string_types):
            src = coord_system[src.lower()]

        if isinstance(dest, six.string_types):
            dest = coord_system[dest.lower()]

        self.src = src
        self.dest = dest
        self._skymatrix = skymatrix(src, dest)
        # self.tran = wcs.Transformation(src, dest)

    def inverted(self):
        return sky2sky(self.dest, self.src)

    def _dotran(self, lonlat):
        xyz = longlat2xyz(lonlat)
        xyz2 = dotrans(self._skymatrix, xyz)
        lonlats2 = xyz2longlat(xyz2)
        return lonlats2

    def __call__(self, lon, lat):
        lon, lat = np.asarray(lon), np.asarray(lat)
        lonlat = np.concatenate([lon[:, np.newaxis],
                                 lat[:, np.newaxis]], 1)
        ll_dest = np.asarray(self._dotran(lonlat))
        return ll_dest[:, 0], ll_dest[:, 1]


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


def fix_lon(lon, lon_ref):
    lon_ = lon - lon_ref
    lon2 = lon_ - 360 * np.floor_divide(lon_, 360.)
    if lon_ == 360:
        lon2 = 360
    return lon2 + lon_ref


class ProjectionBase(object):
    """
    A wrapper for kapteyn.projection or WCS
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
            lon2 = lon_ - 360 * np.floor_divide(lon_, 360.)
            lon2[lon_ == 360] = 360
            return lon2 + lon_ref
        else:
            return lon

    def fix_lon(self, lon_lat):
        """
        """
        if self._lon_axis is not None:
            lon_lat[self._lon_axis] = self._fix_lon(lon_lat[self._lon_axis])

    def _get_radesys(self):
        ctype1, ctype2 = self.ctypes
        equinox = self.equinox
        radecsys = coord_system_guess(ctype1, ctype2, equinox)
        if radecsys is None:
            raise RuntimeError("Cannot determine the coordinate system with "
                               "(CTYPE1={0}, CTYPE2={1}, EQUINOX={2})."
                               .format(ctype1, ctype2, equinox))
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


class ProjectionPywcsNd(_ProjectionSubInterface, ProjectionBase):
    """
    A wrapper for WCS
    """

    def __init__(self, header):
        """
        header could be astropy.io.fits.Header or astropy.wcs.WCS instance
        """

        if isinstance(header, Header):
            self._pywcs = WCS(header=header)
        elif isinstance(header, WCS):
            self._pywcs = header
        else:
            raise ValueError("header must be an instance of "
                             "astropy.io.fits.Header or a WCS object")

        ProjectionBase.__init__(self)

    def _get_ctypes(self):
        return tuple(self._pywcs.wcs.ctype)

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
        # xy21 = self._pywcs.wcs_world2pix(xy1, 1)

        xy2 = np.array(xy21).transpose()
        return xy2

    def toworld(self, xy):
        """ 1, 1 base """
        xy2 = self._pywcs.wcs_pix2world(np.asarray(xy).T, 1)

        lon_lat = xy2.T
        # fixme
        self.fix_lon(lon_lat)

        return lon_lat


class ProjectionPywcsSub(_ProjectionSubInterface, ProjectionBase):
    """
    A wrapper for WCS
    """

    def __init__(self, proj, axis_nums_to_keep, ref_pixel):
        """
        ProjectionPywcsSub(proj, [0, 1], (0, 0, 0))
        """
        self.proj = proj

        self._nsub = len(axis_nums_to_keep)
        self._axis_nums_to_keep = axis_nums_to_keep[:]

        self._ref_pixel = ref_pixel

        _ref_pixel0 = np.array(ref_pixel).reshape((len(ref_pixel), 1))
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
        return self._nsub

    naxis = property(_get_naxis)

    def topixel(self, xy):
        """ 1, 1 base """
        template = xy[0]
        iter_xy = iter(xy)

        xyz = [None] * self.proj.naxis
        for i in self._axis_nums_to_keep:
            xyz[i] = next(iter_xy)
        for i in range(self.proj.naxis):
            if i not in self._axis_nums_to_keep:
                s = np.empty_like(template)
                s.fill(self._ref_world[i])
                xyz[i] = s

        # xyz2 = self._pywcs.wcs_world2pix(np.asarray(xyz).T, 1)
        xyz2 = self.proj.topixel(np.array(xyz))

        # xyz2r = [d for (i, d) in enumerate(xyz2) if i in self._axis_nums_to_keep]
        xyz2r = [xyz2[i] for i in self._axis_nums_to_keep]

        return xyz2r

    def toworld(self, xy):
        """ 1, 1 base """
        template = xy[0]
        iter_xy = iter(xy)

        xyz = [None] * self.proj.naxis
        for i in self._axis_nums_to_keep:
            xyz[i] = next(iter_xy)
        for i in range(self.proj.naxis):
            if i not in self._axis_nums_to_keep:
                s = np.empty_like(template)
                s.fill(self._ref_pixel[i])
                xyz[i] = s

        xyz2 = self.proj.toworld(np.asarray(xyz))
        xyz2r = [xyz2[i] for i in self._axis_nums_to_keep]

        return xyz2r


def get_kapteyn_projection(header):
    if isinstance(header, ProjectionBase):
        projection = header
    else:
        projection = ProjectionPywcsNd(header)

    return projection


def estimate_cdelt(wcs_proj, x0, y0):
    lon0, lat0 = wcs_proj.toworld(([x0], [y0]))

    if lat0 == 90 or lat0 == -90:
        raise ValueError("estimate_cdelt does not work at poles.")

    lon_ref = lon0 - 180.

    lon1, lat1 = wcs_proj.toworld(([x0 + 1], [y0]))
    lon1 = fix_lon(lon1, lon_ref)
    dlon = (lon1[0] - lon0[0]) * np.cos(lat0[0] / 180. * np.pi)
    dlat = (lat1[0] - lat0[0])
    cd1 = (dlon ** 2 + dlat ** 2) ** .5

    lon2, lat2 = wcs_proj.toworld(([x0], [y0 + 1]))
    lon2 = fix_lon(lon2, lon_ref)
    dlon = (lon2[0] - lon0[0]) * np.cos(lat0[0] / 180. * np.pi)
    dlat = (lat2[0] - lat0[0])
    cd2 = (dlon ** 2 + dlat ** 2) ** .5

    return ((cd1 * cd2) ** .5)


def estimate_angle(wcs_proj, x0, y0, sky_to_sky=None):
    """
    return a tuple of two angles (in degree) of increasing direction
    of 1st and 2nd coordinates.

    note that x, y = wcs_proj.topixel(sky_to_sky((l1, l2)))

    """

    cdelt = estimate_cdelt(wcs_proj, x0, y0)

    # x0, y0 = wcs_proj.topixel((lon0, lat0))
    ll = wcs_proj.toworld(([x0], [y0]))
    lon0, lat0 = sky_to_sky.inverted()(ll[0], ll[1])

    ll = sky_to_sky(lon0 + cdelt * np.cos(lat0 / 180. * np.pi), lat0)
    x1, y1 = wcs_proj.topixel(ll)
    a1 = np.arctan2(y1 - y0, x1 - x0) / np.pi * 180.

    ll = sky_to_sky(lon0, lat0 + cdelt)
    x2, y2 = wcs_proj.topixel(ll)
    a2 = np.arctan2(y2 - y0, x2 - x0) / np.pi * 180.

    return a1[0], a2[0]
