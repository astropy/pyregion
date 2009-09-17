
#import parser_ds9 as RP

from ds9_region_parser import RegionParser
from wcs_helper import check_wcs

def parse(region_string):
    rp = RegionParser()
    return rp.parseString(region_string)


def read_region(s):
    rp = RegionParser()
    ss = rp.parse(s)
    sss1 = rp.convert_attr(ss)
    sss2 = check_wcs(sss1)

    return rp.filter_shape(sss2)


def read_region_as_imagecoord(s, header):
    rp = RegionParser()
    ss = rp.parse(s)
    sss1 = rp.convert_attr(ss)
    sss2 = check_wcs(sss1)
    sss3 = rp.sky_to_image(sss2, header)

    return rp.filter_shape(sss3)



def get_mask(region, hdu):
    """
    f = pyfits.read("test.fits")
    reg = read_region_as_imagecoord(s, f[0].header)
    mask = get_mask(reg, f[0])
    """

    from pyregion.region_to_filter import as_region_filter

    data = hdu.data
    header = hdu.header
    
    region_filter = as_region_filter(region)

    mask = region_filter.mask(data)

    return mask


