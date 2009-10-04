from ds9_region_parser import RegionParser
from wcs_helper import check_wcs as _check_wcs
from itertools import cycle, izip

class ShapeList(list):
    def __init__(self, *ka, **kw):
        self._comment_list = kw.pop("comment_list", None)
        list.__init__(self, *ka, **kw)
        
    def as_imagecoord(self, header):
        """
        Return a new ShapeList where the coordinate of the each shape
        is converted to the image coordinate using the given header
        information
        """
        
        comment_list = self._comment_list
        if comment_list is None:
            comment_list = cycle([None])

        r = RegionParser.sky_to_image(izip(self, comment_list),
                                      header)
        shape_list, comment_list = zip(*list(r))
        return ShapeList(shape_list, comment_list=comment_list)
        

    def get_mpl_patches_texts(self):
        from mpl_helper import as_mpl_artists
        patches, txts = as_mpl_artists(self)

        return patches, txts
    
    def get_filter(self, hdu=None, header=None, shape=None):
        from region_to_filter import as_region_filter

        if hdu:
            shape = hdu.data.shape
            header = hdu.header

        if header is not None:
            reg_in_imagecoord = self.as_imagecoord(header)
        else:
            reg_in_imagecoord = self
            
        region_filter = as_region_filter(reg_in_imagecoord)

        return region_filter


    def get_mask(self, hdu=None, header=None, shape=None):
            
        region_filter = self.get_filter(hdu=hdu, header=header, shape=shape)
        mask = region_filter.mask(shape)

        return mask

    

def parse(region_string):
    """
    Parse the input string of a ds9 region definition.
    Returns a list of Shape instances.
    """
    rp = RegionParser()
    ss = rp.parse(region_string)
    sss1 = rp.convert_attr(ss)
    sss2 = _check_wcs(sss1)

    shape_list, comment_list = rp.filter_shape2(sss2)
    return ShapeList(shape_list, comment_list=comment_list)

__open_builtin = open

def open(fname):
    region_string = __open_builtin(fname).read()
    return parse(region_string)


# def parse_deprecated(region_string):
#     rp = RegionParser()
#     return rp.parseString(region_string)


def read_region(s):
    rp = RegionParser()
    ss = rp.parse(s)
    sss1 = rp.convert_attr(ss)
    sss2 = _check_wcs(sss1)

    return rp.filter_shape(sss2)


def read_region_as_imagecoord(s, header):
    rp = RegionParser()
    ss = rp.parse(s)
    sss1 = rp.convert_attr(ss)
    sss2 = _check_wcs(sss1)
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


if __name__ == '__main__':
    #reg = pyregion.open("../mos_fov.reg")
    import pyregion
    proposed_fov = 'fk5;circle(290.96388,14.019167,843.31194")'
    reg = pyregion.parse(proposed_fov)
    reg_imagecoord = reg.as_imagecoord(header)
    patches, txts = reg.get_mpl_patches_texts()
    m = reg.get_mask(hdu=f[0])

