import numpy as np
from astropy.coordinates import SkyCoord


def _estimate_angle(angle, origin, new_frame, offset=1e-7):
    """Transform an angle into a different frame

    This should be replaced with a better solution, perferably in astropy.
    See discussion in https://github.com/astropy/astropy/issues/3093

    According to http://cxc.harvard.edu/ciao/ahelp/dmregions.html#Angles
    this is *definitely* wrong. Angles should be measured counter-clockwise
    from the X axis (not East of North) and this difference screws up
    non-orthagonal axes (see https://github.com/astropy/pyregion/pull/34 )

    Parameters
    ----------
    angle : float, int
        The number of degrees East of North for this angle.

    origin : `~astropy.coordinates.SkyCoord`
        Coordinate from which the angle is measured

    new_frame : `~astropy.coordinates.BaseCoordinateFrame` class or string
        The frame to convert to

    offset : float
        This method creates a temporary coordinate to compute the angle in
        the new frame. This offset gives the angular seperation in degrees
        between these points

    Returns
    -------
    angle : `~astropy.coordinates.Angle`
        The angle, measured East of North in `new_frame`

    """
    angle_deg = angle*np.pi/180

    newlat = offset * np.cos(angle_deg) + origin.data.lat.degree
    newlon = (offset * np.sin(angle_deg) / np.cos(newlat * np.pi/180) +
              origin.data.lon.degree)

    sc = SkyCoord(newlon, newlat, unit='degree', frame=origin.frame.name)

    new_origin = origin.transform_to(new_frame)
    new_sc = sc.transform_to(new_frame)
    return new_origin.position_angle(new_sc)
