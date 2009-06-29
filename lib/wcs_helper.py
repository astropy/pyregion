import copy

import numpy as np

from region_numbers import CoordOdd, CoordEven, Distance, Angle, Integer

from parser_helper import define_shape_helper, wcs_shape, Shape, Global,\
     CoordCommand

from region_numbers import SimpleNumber, SimpleInteger

from kapteyn_helper import get_kapteyn_projection, sky2sky
import kapteyn.wcs as wcs

UnknownWcs = "unknown wcs"

image_like_coordformats = ["image", "pysical","detector","logical"]


def estimate_cdelt(wcs_proj, x0, y0): #, sky_to_sky):
    #s2s = sky_to_sky.inverted()

    #x0, y0 = wcs_proj.topixel((lon0, lat0))
    #ll = wcs_proj.toworld((x0, y0))
    #lon0, lat0 = s2s(ll)

    #ll = wcs_proj.toworld((x0+1, y0))
    #lon1, lat1 = s2s(ll)
    lon0, lat0 = wcs_proj.toworld((x0, y0))
    lon1, lat1 = wcs_proj.toworld((x0+1, y0))

    dlon = (lon1-lon0)*np.cos(lat0/180.*np.pi)
    dlat = (lat1-lat0)
    cd1 = (dlon**2 + dlat**2)**.5

    #ll = wcs_proj.toworld((x0+1, y0))
    #lon2, lat2 = s2s(ll)
    lon2, lat2 = wcs_proj.toworld((x0+1, y0))
    dlon = (lon2-lon0)*np.cos(lat0/180.*np.pi)
    dlat = (lat2-lat0)
    cd2 = (dlon**2 + dlat**2)**.5

    return (cd1*cd2)**.5


def estimate_angle(wcs_proj, x0, y0, sky_to_sky=None):

    cdelt = estimate_cdelt(wcs_proj, x0, y0)

    #x0, y0 = wcs_proj.topixel((lon0, lat0))
    ll = wcs_proj.toworld((x0, y0))
    lon0, lat0 = sky_to_sky.inverted()(ll)

    ll = sky_to_sky((lon0 + cdelt*np.cos(lat0/180.*np.pi), lat0))
    x1, y1 = wcs_proj.topixel(ll)
    a1 = np.arctan2(y1-y0, x1-x0)/np.pi*180.

    ll = sky_to_sky((lon0, lat0+cdelt))
    x2, y2 = wcs_proj.topixel(ll)
    a2 = np.arctan2(y2-y0, x2-x0)/np.pi*180.

    return a1, a2



select_wcs = dict(galactic=wcs.galactic,
                  fk4=wcs.fk5,
                  fk5=wcs.fk5,
                  icrs=wcs.icrs).get


def convert_to_imagecoord(cl, fl, wcs_proj, sky_to_sky, xy0):
    fl0 = fl
    new_cl = []

    while cl:
        if len(fl) == 0:
            fl = fl0

        if fl[0] == CoordOdd and fl[1] == CoordEven:

            ll = sky_to_sky(tuple(cl[:2]))
            xy0 = wcs_proj.topixel(ll)
            new_cl.extend(xy0)
            cl = cl[2:]
            fl = fl[2:]
        elif fl[0] == Distance:
            degree_per_pixel = estimate_cdelt(wcs_proj, sky_to_sky,
                                              *xy0)
            new_cl.append(cl[0]/degree_per_pixel)
            cl = cl[1:]
            fl = fl[1:]
        elif fl[0] == Angle:
            rot = estimate_angle(wcs_proj, sky_to_sky, *xy0)
            new_cl.append(cl[0]+rot)
            cl = cl[1:]
            fl = fl[1:]
        else:
            new_cl.append(cl[0])
            cl = cl[1:]
            fl = fl[1:]

    return new_cl, xy0




def check_wcs_and_convert(args, all_dms=False):

    is_wcs = False

    value_list = []
    for a in args:
        if isinstance(a, SimpleNumber) or isinstance(a, SimpleInteger) \
               or all_dms:
            value_list.append(a.v)
        else:
            value_list.append(a.degree)
            is_wcs = True

    return is_wcs, value_list


def check_wcs(l):
    default_coord = "image"

    for l1, c1 in l:
        if isinstance(l1, CoordCommand):
            default_coord = l1.text.lower()
            continue
        if isinstance(l1, Shape):
            if default_coord == "galactic":
                is_wcs, coord_list = check_wcs_and_convert(l1.params,
                                                           all_dms=True)
            else:
                is_wcs, coord_list = check_wcs_and_convert(l1.params)

            if is_wcs and default_coord in image_like_coordformats:
                # ciao formats
                coord_format = "unknown wcs"
            else:
                coord_format = default_coord

            l1n = copy.copy(l1)

            l1n.coord_list = coord_list
            l1n.coord_format = coord_format

            yield l1n, c1
        else:
            yield l1, c1

