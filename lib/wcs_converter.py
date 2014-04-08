from .wcs_helper import estimate_cdelt, estimate_angle
from .region_numbers import CoordOdd, CoordEven, Distance, Angle
from .parser_helper import Shape, CoordCommand
from .region_numbers import SimpleNumber, SimpleInteger

import copy


def convert_to_imagecoord(cl, fl, wcs_proj, sky_to_sky, xy0, rot_wrt_axis=1):
    fl0 = fl
    new_cl = []

    while cl:
        if len(fl) == 0:
            fl = fl0

        if fl[0] == CoordOdd and fl[1] == CoordEven:

            ll = sky_to_sky([cl[0]], [cl[1]])
            x0, y0 = wcs_proj.topixel(ll)
            xy0 = [x0[0], y0[0]]
            new_cl.extend(xy0)
            cl = cl[2:]
            fl = fl[2:]
        elif fl[0] == Distance:
            degree_per_pixel = estimate_cdelt(wcs_proj, *xy0)
            new_cl.append(cl[0]/degree_per_pixel)
            cl = cl[1:]
            fl = fl[1:]
        elif fl[0] == Angle:
            rot1, rot2 = estimate_angle(wcs_proj, xy0[0], xy0[1], sky_to_sky)
            if rot_wrt_axis == 1:
                new_cl.append(cl[0]+rot1-180.)
            else:
                new_cl.append(cl[0]+rot2-90.) # use the angle between the Y axis and North

            cl = cl[1:]
            fl = fl[1:]
        else:
            new_cl.append(cl[0])
            cl = cl[1:]
            fl = fl[1:]

    return new_cl, xy0


def convert_physical_to_imagecoord(cl, fl, pc):
    fl0 = fl
    new_cl = []

    while cl:
        if len(fl) == 0:
            fl = fl0

        if fl[0] == CoordOdd and fl[1] == CoordEven:

            xy0 = pc.to_image(cl[0], cl[1])
            new_cl.extend(xy0)
            cl = cl[2:]
            fl = fl[2:]
        elif fl[0] == Distance:
            new_cl.append(pc.to_image_distance(cl[0]))
            cl = cl[1:]
            fl = fl[1:]
        else:
            new_cl.append(cl[0])
            cl = cl[1:]
            fl = fl[1:]

    return new_cl




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
    default_coord = "physical"

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

            if is_wcs and (default_coord == "physical"): # ciao format
                coord_format = "fk5"
            else:
                coord_format = default_coord

            l1n = copy.copy(l1)

            l1n.coord_list = coord_list
            l1n.coord_format = coord_format

            yield l1n, c1
        else:
            yield l1, c1



