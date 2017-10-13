import numpy as np
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales


def _estimate_angle(angle, reg_coordinate_frame, header):
    """Transform an angle into a different frame

    Parameters
    ----------
    angle : float, int
        The number of degrees, measured from the Y axis in origin's frame

    reg_coordinate_frame : str
        Coordinate frame in which ``angle`` is defined

    header : `~astropy.io.fits.Header` instance
        Header describing the image

    Returns
    -------
    angle : float
        The angle, measured from the Y axis in the WCS defined by ``header'`
    """
    y_axis_rot = _calculate_rotation_angle(reg_coordinate_frame, header)
    return angle - y_axis_rot


def _calculate_rotation_angle(reg_coordinate_frame, header):
    """Calculates the rotation angle from the region to the header's frame

    This attempts to be compatible with the implementation used by SAOImage
    DS9. In particular, this measures the rotation of the north axis as
    measured at the center of the image, and therefore requires a
    `~astropy.io.fits.Header` object with defined 'NAXIS1' and 'NAXIS2'
    keywords.

    Parameters
    ----------
    reg_coordinate_frame : str
        Coordinate frame used by the region file

    header : `~astropy.io.fits.Header` instance
        Header describing the image

    Returns
    -------
    y_axis_rot : float
        Degrees by which the north axis in the region's frame is rotated when
        transformed to pixel coordinates
    """
    new_wcs = WCS(header)
    region_frame = SkyCoord(
        '0d 0d',
        frame=reg_coordinate_frame,
        obstime='J2000')
    region_frame = SkyCoord(
        '0d 0d',
        frame=reg_coordinate_frame,
        obstime='J2000',
        equinox=region_frame.equinox)

    origin = SkyCoord.from_pixel(
        header['NAXIS1'] / 2,
        header['NAXIS2'] / 2,
        wcs=new_wcs,
        origin=1).transform_to(region_frame)

    offset = proj_plane_pixel_scales(new_wcs)[1]

    origin_x, origin_y = origin.to_pixel(new_wcs, origin=1)
    origin_lon = origin.data.lon.degree
    origin_lat = origin.data.lat.degree

    offset_point = SkyCoord(
        origin_lon, origin_lat + offset, unit='degree',
        frame=origin.frame.name, obstime='J2000')
    offset_x, offset_y = offset_point.to_pixel(new_wcs, origin=1)

    north_rot = np.arctan2(
        offset_y - origin_y,
        offset_x - origin_x) / np.pi * 180.

    cdelt = new_wcs.wcs.get_cdelt()
    if (cdelt > 0).all() or (cdelt < 0).all():
        return north_rot - 90
    else:
        return -(north_rot - 90)
