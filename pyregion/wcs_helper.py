import numpy as np
from astropy.coordinates import SkyCoord


def _estimate_angle(angle, origin, new_wcs, offset=1e-9):
    """Transform an angle into a different frame

    This should be replaced with a better solution, perferably in astropy.
    See discussion in https://github.com/astropy/astropy/issues/3093

    This is influenced by https://github.com/astropy/pyregion/pull/34 ,
    where Mihai Cara argues that measuring angles as East of North is wrong.
    http://cxc.harvard.edu/ciao/ahelp/dmregions.html#Angles backs this up,
    and so all angles are measured as if rot_wrt_axis=2 in PR #34.
    This is only significant for images with non-orthagonal axes.

    Parameters
    ----------
    angle : float, int
        The number of degrees, measured from the Y axis in origin's frame

    origin : `~astropy.coordinates.SkyCoord`
        Coordinate from which the angle is measured

    new_wcs : `~astropy.wcs.WCS` instance
        The WCS to use for conversation of the angle

    offset : float
        This method creates a temporary coordinate to compute the angle in
        the new frame. This offset gives the angular seperation in degrees
        between these points

    Returns
    -------
    angle : float
        The angle, measured from the Y axis in the new WCS

    """

    x0, y0 = origin.to_pixel(new_wcs, origin=1)
    lon0 = origin.data.lon.degree
    lat0 = origin.data.lat.degree

    offset_point = SkyCoord(lon0, lat0+offset, unit='degree',
                            frame=origin.frame.name)
    x2, y2 = offset_point.to_pixel(new_wcs, origin=1)

    y_axis_rot = np.arctan2(y2-y0, x2-x0) / np.pi*180.

    return (y_axis_rot + angle - 90.) % 360.
