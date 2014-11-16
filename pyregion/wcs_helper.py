import numpy as np
from astropy.coordinates import SkyCoord

def _estimate_cdelt(wcs, x0, y0):
    """Give an estimate of the pixel scale

    This should probably be from wcs.pixel_scale_matrix

    Parameters
    ----------
    wcs : `~astropy.wcs.WCS`
        The WCS object to obtain pixel values from

    x0, y0 : floats
        Pixel coordinates to obtain the pixel scale around

    Returns
    -------
    cdelt : float
        An estimate of the pixel scale at (x0, y0)

    """
    # TODO: should ra_dec_order=True here?
    lon0, lat0 = wcs.all_pix2world(x0, y0, 1)

    if np.isclose(lat0, 90) or np.isclose(lat0, -90):
        raise ValueError("estimate_cdelt does not work at poles.")

    lon1, lat1 = wcs.all_pix2world(x0+1, y0, 1)
    dlon = (lon1-lon0)*np.cos(lat0/180.*np.pi)
    dlat = (lat1-lat0)
    cd1 = (dlon**2 + dlat**2)**.5

    lon2, lat2 = wcs.all_pix2world(x0, y0+1, 1)
    dlon = (lon2-lon0)*np.cos(lat0/180.*np.pi)
    dlat = (lat2-lat0)
    cd2 = (dlon**2 + dlat**2)**.5

    return ((cd1 * cd2) ** .5)


def _estimate_angle(angle, origin, new_frame, offset=1e-7):
    """Transform an angle into a different frame

    This should be replaced with a better solution, perferably in astropy.
    See discussion in https://github.com/astropy/astropy/issues/3093

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
