import copy

from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from .wcs_helper import _estimate_angle, _get_combined_cdelt
from .region_numbers import CoordOdd, Distance, Angle
from .parser_helper import Shape, CoordCommand
from .region_numbers import SimpleNumber, SimpleInteger
import numpy as np


def _generate_arg_types(coordlist_length, shape_name):
    """Find coordinate types based on shape name and coordlist length

    This function returns a list of coordinate types based on which
    coordinates can be repeated for a given type of shap

    Parameters
    ----------
    coordlist_length : int
        The number of coordinates or arguments used to define the shape.

    shape_name : str
        One of the names in `pyregion.ds9_shape_defs`.

    Returns
    -------
    arg_types : list
        A list of objects from `pyregion.region_numbers` with a length equal to
        coordlist_length.

    """
    from .ds9_region_parser import ds9_shape_defs

    initial_arg_types = ds9_shape_defs[shape_name].args_list
    arg_repeats = ds9_shape_defs[shape_name].args_repeat

    if arg_repeats is None:
        return initial_arg_types
    else:
        # repeat args between n1 and n2
        n1, n2 = arg_repeats
        arg_types = list(initial_arg_types[:n1])
        num_of_repeats = coordlist_length - (len(initial_arg_types) - n2)
        arg_types.extend((num_of_repeats-n1) //
                         (n2 - n1) * initial_arg_types[n1:n2])
        arg_types.extend(initial_arg_types[n2:])
        return arg_types


def convert_to_imagecoord(shape, header):
    """Convert the coordlist of `shape` to image coordinates

    Parameters
    ----------
    shape : `pyregion.parser_helper.Shape`
        The `Shape` to convert coordinates

    header : `~astropy.io.fits.Header` or `~astropy.wcs.WCS`
        Specifies what WCS transformations to use.

    Returns
    -------
    new_coordlist : list
        A list of image coordinates defining the shape.

    """
    arg_types = _generate_arg_types(len(shape.coord_list), shape.name)

    new_coordlist = []
    last_coordinate = None
    old_coordinate = None
    coord_list_iter = iter(zip(shape.coord_list, arg_types))
    if isinstance(header, WCS):
        new_wcs = header
    else:
        new_wcs = WCS(header)

    for coordinate, coordinate_type in coord_list_iter:
        if coordinate_type == CoordOdd:
            even_coordinate = next(coord_list_iter)[0]

            old_coordinate = SkyCoord(coordinate, even_coordinate,
                                      frame=shape.coord_format, unit='degree',
                                      obstime='J2000')
            last_coordinate = old_coordinate.to_pixel(new_wcs, origin=1)
            last_coordinate = [np.asscalar(x) for x in last_coordinate]

            new_coordlist.extend(last_coordinate)

        elif coordinate_type == Distance:
            degree_per_pixel = _get_combined_cdelt(new_wcs)
            new_coordlist.append(coordinate / degree_per_pixel)

        elif coordinate_type == Angle:
            new_angle = _estimate_angle(coordinate, old_coordinate, new_wcs)
            new_coordlist.append(new_angle)

        else:
            new_coordlist.append(coordinate)

    return new_coordlist


def convert_physical_to_imagecoord(shape, header):
    arg_types = _generate_arg_types(len(shape.coord_list), shape.name)

    new_coordlist = []
    coord_list_iter = iter(zip(shape.coord_list, arg_types))

    from .physical_coordinate import PhysicalCoordinate
    pc = PhysicalCoordinate(header)

    for coordinate, coordinate_type in coord_list_iter:
        if coordinate_type == CoordOdd:
            even_coordinate = next(coord_list_iter)[0]

            xy0 = pc.to_image(coordinate, even_coordinate)
            new_coordlist.extend(xy0)
        elif coordinate_type == Distance:
            new_coordlist.append(pc.to_image_distance(coordinate))
        else:
            new_coordlist.append(coordinate)

    return new_coordlist


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

            if is_wcs and (default_coord == "physical"):  # ciao format
                coord_format = "fk5"
            else:
                coord_format = default_coord

            l1n = copy.copy(l1)

            l1n.coord_list = coord_list
            l1n.coord_format = coord_format

            yield l1n, c1
        else:
            yield l1, c1
