import copy
import warnings
from pyparsing import (Literal, CaselessKeyword, CaselessLiteral,
                       Optional, And, Or, Word,
                       StringEnd, ParseException, Combine,
                       alphas)
from .region_numbers import CoordOdd, CoordEven, Distance, Angle, Integer
from .parser_helper import (wcs_shape, define_shape_helper, Shape, Global,
                            RegionPusher, define_expr, define_line,
                            CoordCommand,
                            comment_shell_like, define_simple_literals)
from .ds9_attr_parser import Ds9AttrParser, get_attr
from .wcs_converter import (convert_to_imagecoord,
                            convert_physical_to_imagecoord)

ds9_shape_defs = dict(
    circle=wcs_shape(CoordOdd, CoordEven, Distance),
    rotbox=wcs_shape(CoordOdd, CoordEven, Distance, Distance, Angle,
                     repeat=(2, 4)),
    box=wcs_shape(CoordOdd, CoordEven, Distance, Distance, Angle,
                  repeat=(2, 4)),
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

image_like_coordformats = ["image", "physical", "detector", "logical"]


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

        coordCommandLiterals = define_simple_literals(coord_command_keys)
        coordCommandWCS = Combine(CaselessLiteral("WCS") + Optional(Word(alphas)))

        coordCommand = (coordCommandLiterals | coordCommandWCS)
        coordCommand.setParseAction(lambda s, l, tok: CoordCommand(tok[-1]))

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
    def sky_to_image(shape_list, header):
        """Converts a `ShapeList` into shapes with coordinates in image coordinates

        Parameters
        ----------
        shape_list : `pyregion.ShapeList`
            The ShapeList to convert
        header : `~astropy.io.fits.Header`
            Specifies what WCS transformations to use.

        Yields
        -------
        shape, comment : Shape, str
            Shape with image coordinates and the associated comment

        Note
        ----
        The comments in the original `ShapeList` are unaltered

        """

        for shape, comment in shape_list:
            if isinstance(shape, Shape) and \
                    (shape.coord_format not in image_like_coordformats):

                new_coords = convert_to_imagecoord(shape, header)

                l1n = copy.copy(shape)

                l1n.coord_list = new_coords
                l1n.coord_format = "image"
                yield l1n, comment

            elif isinstance(shape, Shape) and shape.coord_format == "physical":

                if header is None:
                    raise RuntimeError("Physical coordinate is not known.")

                new_coordlist = convert_physical_to_imagecoord(shape, header)

                l1n = copy.copy(shape)

                l1n.coord_list = new_coordlist
                l1n.coord_format = "image"
                yield l1n, comment

            else:
                yield shape, comment

    def filter_shape(self, sss):
        return [s1[0] for s1 in sss if isinstance(s1[0], Shape)]

    @staticmethod
    def filter_shape2(sss):
        r = [s1 for s1 in sss if isinstance(s1[0], Shape)]
        return zip(*r)
