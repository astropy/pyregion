from .version import __version__
from .ds9_region_parser import RegionParser
from .wcs_converter import check_wcs as _check_wcs
from itertools import cycle

_builtin_open = open

class ShapeList(list):
    """ A list of shape objects """
    def __init__(self, shape_list, comment_list=None):
        """

        Parameters
        ----------
        shape_list : a list of 'pyregion.parse_helper.Shape' objects
        comment_list : list, None
         list of comment strings for each argument


        """
        if comment_list is not None:
            if len(comment_list) != len(shape_list):
                err = "Ambiguous number of comments {} for number of shapes {}"
                raise ValueError(err.format(len(comment_list),
                                            len(shape_list)))
        self._comment_list = comment_list
        list.__init__(self, shape_list)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return ShapeList(list.__getitem__(self, key))
        else:
            return list.__getitem__(self, key)

    def __getslice__(self, i, j):
        return self[max(0, i):max(0, j):]

    def check_imagecoord(self):
        if [s for s in self if s.coord_format != "image"]:
            return False
        else:
            return True

    def as_imagecoord(self, header, rot_wrt_axis=1):
        """
        Return a new ShapeList where the coordinate of the each shape
        is converted to the image coordinate using the given header
        information
        """

        comment_list = self._comment_list
        if comment_list is None:
            comment_list = cycle([None])

        r = RegionParser.sky_to_image(zip(self, comment_list),
                                      header, rot_wrt_axis=rot_wrt_axis)
        shape_list, comment_list = zip(*list(r))
        return ShapeList(shape_list, comment_list=comment_list)

    def get_mpl_patches_texts(self, properties_func=None,
                              text_offset=5.0,
                              origin=1):
        """
        Often, the regions files implicitly assume the lower-left
        corner of the image as a coordinate (1,1). However, the python
        convetion is that the array index starts from 0. By default
        (origin = 1), coordinates of the returned mpl artists have
        coordinate shifted by (1, 1). If you do not want this shift,
        use origin=0.
        """
        from .mpl_helper import as_mpl_artists
        patches, txts = as_mpl_artists(self, properties_func,
                                       text_offset,
                                       origin=origin)

        return patches, txts

    def get_filter(self, header=None, origin=1, rot_wrt_axis=1):
        """
        Often, the regions files implicitly assume the lower-left
        corner of the image as a coordinate (1,1). However, the python
        convetion is that the array index starts from 0. By default
        (origin = 1), coordinates of the returned mpl artists have
        coordinate shifted by (1, 1). If you do not want this shift,
        use origin=0.
        """

        from .region_to_filter import as_region_filter

        if header is None:
            if not self.check_imagecoord():
                raise RuntimeError("the region has non-image coordinate. header is required.")
            reg_in_imagecoord = self
        else:
            reg_in_imagecoord = self.as_imagecoord(header, rot_wrt_axis=rot_wrt_axis)

        region_filter = as_region_filter(reg_in_imagecoord, origin=1)

        return region_filter


    def get_mask(self, hdu=None, header=None, shape=None, rot_wrt_axis=1):
        """
        creates a 2-d mask.

        get_mask(hdu=f[0])
        get_mask(shape=(10,10))
        get_mask(header=f[0].header, shape=(10,10))
        """

        if hdu and header is None:
            header = hdu.header
        if hdu and shape is None:
            shape = hdu.data.shape

        region_filter = self.get_filter(header=header, rot_wrt_axis=rot_wrt_axis)
        mask = region_filter.mask(shape)

        return mask


    def write(self, outfile):
        """ Writes the current shape list out as a region file """
        if len(self) < 1:
            print("WARNING: The region list is empty. The region file "\
                  "'{:s}' will be empty.".format(outfile))
            try:
                outf = open(outfile,'w')
                outf.close()
                return
            except IOError as e:
                cmsg = "Unable to create region file '{:s}'.".format(outfile)
                if e.args:
                    e.args = (e.args[0] + '\n' + cmsg,) + e.args[1:]
                else:
                    e.args=(cmsg,)
                raise e

        prev_cs = self[0].coord_format

        outf = None
        try:
            outf = _builtin_open(outfile,'w')

            attr0 = self[0].attr[1]
            defaultline = " ".join( [ "{:s}={:s}".format(a,attr0[a]) \
                                      for a in attr0 if a != 'text' ] )

            # first line is globals
            print >>outf, "global", defaultline
            # second line must be a coordinate format
            print >>outf, prev_cs

            for shape in self:
                shape_attr = '' if prev_cs == shape.coord_format \
                    else shape.coord_format+"; "
                shape_excl = '-' if shape.exclude else ''
                text_coordlist = [ "{:f}".format(f) for f in shape.coord_list ]
                shape_coords = "(" + ",".join(text_coordlist) + ")"
                shape_comment = " # " + shape.comment if shape.comment else ''

                shape_str = shape_attr + shape_excl + shape.name + \
                            shape_coords + shape_comment

                print >>outf, shape_str

        except IOError as e:
            cmsg = "Unable to create region file \'{:s}\'.".format(outfile)
            if e.args:
                e.args = (e.args[0] + '\n' + cmsg,) + e.args[1:]
            else:
                e.args=(cmsg,)
            raise e
        finally:
            if outf: outf.close()


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

def open(fname):
    region_string = _builtin_open(fname).read()
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


def read_region_as_imagecoord(s, header, rot_wrt_axis=1):
    rp = RegionParser()
    ss = rp.parse(s)
    sss1 = rp.convert_attr(ss)
    sss2 = _check_wcs(sss1)
    sss3 = rp.sky_to_image(sss2, header, rot_wrt_axis=rot_wrt_axis)

    return rp.filter_shape(sss3)


def get_mask(region, hdu, origin=1):
    """
    f = pyfits.read("test.fits")
    reg = read_region_as_imagecoord(s, f[0].header)
    mask = get_mask(reg, f[0])
    """
    from pyregion.region_to_filter import as_region_filter

    data = hdu.data
    region_filter = as_region_filter(region, origin=origin)
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
