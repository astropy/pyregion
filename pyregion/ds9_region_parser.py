import copy
import warnings
from pyparsing import (Literal, CaselessKeyword, Optional, And, Or,
                       StringEnd, ParseException)
from .region_numbers import CoordOdd, CoordEven, Distance, Angle, Integer
from .parser_helper import (wcs_shape, define_shape_helper, Shape, Global,
                            RegionPusher, define_expr, define_line,
                            CoordCommand,
                            comment_shell_like, define_simple_literals)
from .wcs_helper import (get_kapteyn_projection, sky2sky, UnknownWcs,
                         image_like_coordformats, select_wcs)
from .ds9_attr_parser import Ds9AttrParser, get_attr
from .wcs_converter import (convert_to_imagecoord,
                            convert_physical_to_imagecoord)
from .physical_coordinate import PhysicalCoordinate

ds9_shape_defs = dict(
    circle=wcs_shape(CoordOdd, CoordEven, Distance),
    rotbox=wcs_shape(CoordOdd, CoordEven, Distance, Distance, Angle),
    box=wcs_shape(CoordOdd, CoordEven, Distance, Distance, Angle),
    polygon=wcs_shape(CoordOdd, CoordEven, repeat=(0, 2)),
    ellipse=wcs_shape(CoordOdd, CoordEven, Distance, Distance, Angle, repeat=(2, 4)),
    annulus=wcs_shape(CoordOdd, CoordEven, Distance, repeat=(2, 3)),
    panda=wcs_shape(CoordOdd, CoordEven, Angle, Angle, Integer, Distance, Distance, Integer),
    pie=wcs_shape(CoordOdd, CoordEven,
                  Distance, Distance,
                  Angle, Angle),
    epanda=wcs_shape(CoordOdd, CoordEven,
                     Angle, Angle, Integer,
                     Distance, Distance, Distance,
                     Distance, Integer, Angle),
    bpanda=wcs_shape(CoordOdd, CoordEven,
                     Angle, Angle, Integer,
                     Distance, Distance, Distance,
                     Distance, Integer, Angle),
    point=wcs_shape(CoordOdd, CoordEven),
    line=wcs_shape(CoordOdd, CoordEven, CoordOdd, CoordEven),
    vector=wcs_shape(CoordOdd, CoordEven, Distance, Angle),
    text=wcs_shape(CoordOdd, CoordEven),
)


class RegionParser(RegionPusher):
    def __init__(self):

        RegionPusher.__init__(self)

        self.shape_definition = ds9_shape_defs
        regionShape = define_shape_helper(self.shape_definition)
        regionShape = regionShape.setParseAction(lambda s, l, tok: Shape(tok[0], tok[1:]))

        regionExpr = define_expr(regionShape,
                                 negate_func=lambda s, l, tok: tok[-1].set_exclude(),
                                 )

        coord_command_keys = ['PHYSICAL', 'IMAGE', 'FK4', 'B1950', 'FK5',
                              'J2000', 'GALACTIC', 'ECLIPTIC', 'ICRS',
                              'LINEAR', 'AMPLIFIER', 'DETECTOR']

        coordCommand = define_simple_literals(coord_command_keys,
                                              parseAction=lambda s, l, tok: CoordCommand(tok[-1]))

        regionGlobal = comment_shell_like(CaselessKeyword("global"),
                                          lambda s, l, tok: Global(tok[-1]))

        regionAtom = (regionExpr | coordCommand | regionGlobal)

        regionAtom = regionAtom.setParseAction(self.pushAtom)

        regionComment = comment_shell_like(Literal("#"),
                                           parseAction=self.pushComment)

        line_simple = define_line(atom=regionAtom,
                                  separator=Literal(";"),
                                  comment=regionComment
                                  )

        line_w_composite = And([regionAtom,
                                CaselessKeyword("||").setParseAction(self.set_continued)
                                ]) \
                           + Optional(regionComment)

        line = Or([line_simple, line_w_composite])

        self.parser = Optional(line) + StringEnd()

    def parseLine(self, l):
        self.parser.parseString(l)
        s, c, continued = self.stack, self.comment, self.continued
        self.flush()

        return s, c, continued

    def parse(self, s):

        for l in s.split("\n"):
            try:
                s, c, continued = self.parseLine(l)
            except ParseException:
                warnings.warn("Failed to parse : " + l)
                self.flush()
                continue

            if len(s) > 1:
                for s1 in s[:-1]:
                    yield s1, None

                s[-1].comment = c
                s[-1].continued = continued
                yield s[-1], c
            elif len(s) == 1:
                s[-1].comment = c
                s[-1].continued = continued
                yield s[-1], c
            elif c:
                yield None, c

            self.flush()

    def convert_attr(self, l):
        global_attr = [], {}

        parser = Ds9AttrParser()

        for l1, c1 in l:
            if isinstance(l1, Global):
                for kv in parser.parse_default(l1.text):
                    if len(kv) == 1:
                        global_attr[0].append(kv[0])
                    elif len(kv) == 2:
                        if kv[0] == 'tag':
                            global_attr[1].setdefault(kv[0], set()).add(kv[1])
                        else:
                            global_attr[1][kv[0]] = kv[1]

            elif isinstance(l1, Shape):
                if c1:
                    attr_list = parser.parse_default(c1)
                    attr0, attr1 = get_attr(attr_list, global_attr)
                else:
                    attr0, attr1 = global_attr
                l1n = copy.copy(l1)
                l1n.attr = attr0, attr1
                yield l1n, c1

            elif not l1 and c1:
                shape, attr_list = parser.parse_check_shape(c1)
                if shape:
                    shape.attr = get_attr(attr_list, global_attr)
                    yield shape, c1
            else:
                yield l1, c1

    @staticmethod
    def sky_to_image(l, header, rot_wrt_axis=1):
        """

        Parameters
        ----------
        l : TODO
            TODO
        header : `~astropy.io.fits.Header`
            FITS header
        rot_wrt_axis : {1, 2}
            Use rotation with respect to axis 1 (X-axis) or axis 2 (Y-axis) and north.

        Returns
        -------
        TODO
        """

        try:  # this is a hack to test if header is fits header of wcs object.
            header["NAXIS"]
        except (KeyError, TypeError, ValueError):
            pc = None
        else:
            pc = PhysicalCoordinate(header)

        wcs_proj = get_kapteyn_projection(header)

        for l1, c1 in l:
            if isinstance(l1, Shape) and \
                    (l1.coord_format not in image_like_coordformats):
                tgt = wcs_proj.radesys
                if l1.coord_format == UnknownWcs:
                    src = tgt
                else:
                    src = select_wcs(l1.coord_format)
                sky_to_sky = sky2sky(src, tgt)

                cl = l1.coord_list
                fl = ds9_shape_defs[l1.name].args_list

                # take care of repeated items
                if ds9_shape_defs[l1.name].args_repeat:
                    n1, n2 = ds9_shape_defs[l1.name].args_repeat
                else:
                    n1 = 0
                    n2 = len(cl)

                xy0 = None

                cl1, fl1 = cl[:n1], fl[:n1]
                cl10, xy0 = convert_to_imagecoord(cl1, fl1, wcs_proj,
                                                  sky_to_sky, xy0,
                                                  rot_wrt_axis=rot_wrt_axis)

                nn2 = len(cl) - (len(fl) - n2)
                cl2, fl2 = cl[n1:nn2], fl[n1:n2]
                cl20, xy0 = convert_to_imagecoord(cl2, fl2, wcs_proj,
                                                  sky_to_sky, xy0,
                                                  rot_wrt_axis=rot_wrt_axis)

                cl3, fl3 = cl[nn2:], fl[n2:]
                cl30, xy0 = convert_to_imagecoord(cl3, fl3, wcs_proj,
                                                  sky_to_sky, xy0,
                                                  rot_wrt_axis=rot_wrt_axis)

                new_cl = cl10 + cl20 + cl30

                l1n = copy.copy(l1)

                l1n.coord_list = new_cl
                l1n.coord_format = "image"
                yield l1n, c1

            elif isinstance(l1, Shape) and (l1.coord_format == "physical"):

                if pc is None:
                    raise RuntimeError("Physical coordinate is not known.")

                cl = l1.coord_list
                fl = ds9_shape_defs[l1.name].args_list

                # take care of repeated items
                if ds9_shape_defs[l1.name].args_repeat:
                    n1, n2 = ds9_shape_defs[l1.name].args_repeat
                else:
                    n1 = 0
                    n2 = len(cl)

                xy0 = None

                cl1, fl1 = cl[:n1], fl[:n1]
                cl10 = convert_physical_to_imagecoord(cl1, fl1, pc)
                # cl10, xy0 = convert_to_imagecoord(cl1, fl1, wcs_proj,
                #                sky_to_sky, xy0, rot_wrt_axis=rot_wrt_axis)

                nn2 = len(cl) - (len(fl) - n2)
                cl2, fl2 = cl[n1:nn2], fl[n1:n2]
                cl20 = convert_physical_to_imagecoord(cl2, fl2, pc)
                # cl20, xy0 = convert_to_imagecoord(cl2, fl2, wcs_proj,
                #                sky_to_sky, xy0, rot_wrt_axis=rot_wrt_axis)

                cl3, fl3 = cl[nn2:], fl[n2:]
                cl30 = convert_physical_to_imagecoord(cl3, fl3, pc)

                new_cl = cl10 + cl20 + cl30

                l1n = copy.copy(l1)

                l1n.coord_list = new_cl
                l1n.coord_format = "image"
                yield l1n, c1

            else:
                yield l1, c1

    def filter_shape(self, sss):
        return [s1[0] for s1 in sss if isinstance(s1[0], Shape)]

    @staticmethod
    def filter_shape2(sss):
        r = [s1 for s1 in sss if isinstance(s1[0], Shape)]
        return zip(*r)
