from pyparsing import Literal, CaselessKeyword, CaselessLiteral, \
     Word, Optional, OneOrMore, Group, Combine, ZeroOrMore, nums, \
     Forward, StringEnd, restOfLine, alphas, alphanums, CharsNotIn, \
     MatchFirst, And, Or

from region_numbers import CoordOdd, CoordEven, Distance, Angle, Integer
from region_numbers import SimpleNumber, SimpleInteger

from region_attr import attr_parser
import copy
import numpy as np

import warnings

from kapteyn_helper import get_kapteyn_projection, sky2sky
import kapteyn.wcs as wcs

UnknownWcs = "unknown wcs"

image_like_coordformats = ["image", "pysical","detector","logical"]



def estimate_cdelt(wcs_proj, sky_to_sky, x0, y0):
    s2s = sky_to_sky.inverted()

    #x0, y0 = wcs_proj.topixel((lon0, lat0))
    ll = wcs_proj.toworld((x0, y0))
    lon0, lat0 = s2s(ll)

    ll = wcs_proj.toworld((x0+1, y0))
    lon1, lat1 = s2s(ll)
    dlon = (lon1-lon0)*np.cos(lat0/180.*np.pi)
    dlat = (lat1-lat0)
    cd1 = (dlon**2 + dlat**2)**.5

    ll = wcs_proj.toworld((x0+1, y0))
    lon2, lat2 = s2s(ll)
    dlon = (lon2-lon0)*np.cos(lat0/180.*np.pi)
    dlat = (lat2-lat0)
    cd2 = (dlon**2 + dlat**2)**.5

    return (cd1*cd2)**.5

def estimate_angle(wcs_proj, sky_to_sky, x0, y0):
    return 0.

_select_wcs = dict(galactic=wcs.galactic,
                   fk4=wcs.fk5,
                   fk5=wcs.fk5,
                   icrs=wcs.icrs).get


def _convert(cl, fl, wcs_proj, sky_to_sky, xy0):
    fl0 = fl
    new_cl = []

    while cl:
        if len(fl) == 0:
            fl = fl0

        if fl[0] == CoordOdd and fl[1] == CoordEven:

            ll = sky_to_sky(tuple(cl[:2]))
            xy0 = wcs_proj.topixel(ll)
            new_cl.extend(xy0)
            cl = cl[2:]
            fl = fl[2:]
        elif fl[0] == Distance:
            degree_per_pixel = estimate_cdelt(wcs_proj, sky_to_sky,
                                              *xy0)
            new_cl.append(cl[0]/degree_per_pixel)
            cl = cl[1:]
            fl = fl[1:]
        elif fl[0] == Angle:
            rot = estimate_angle(wcs_proj, sky_to_sky, *xy0)
            new_cl.append(cl[0]+rot)
            cl = cl[1:]
            fl = fl[1:]
        else:
            new_cl.append(cl[0])
            cl = cl[1:]
            fl = fl[1:]
            #raise Exception("Unknown format: %s" % fl[0])

    return new_cl, xy0


def sky_to_image(l, wcs):

    wcs_proj = get_kapteyn_projection(wcs)

    for l1, c1 in l:
        if isinstance(l1, Shape) and l1.coord_format not in image_like_coordformats:
            tgt = wcs_proj.radesys
            if l1.coord_format == UnknownWcs:
                src = tgt
            else:
                src = _select_wcs(l1.coord_format)

            sky_to_sky = sky2sky(src, tgt)

            cl = l1.coord_list
            fl = ds9_shape_defs[l1.name].args_list

            if ds9_shape_defs[l1.name].args_repeat:
                n1, n2 = ds9_shape_defs[l1.name].args_repeat
            else:
                n1 = 0
                n2 = len(cl)
            #new_cl = []

            xy0 = None

            cl1, fl1 = cl[:n1], fl[:n1]
            cl10, xy0 = _convert(cl1, fl1, wcs_proj, sky_to_sky, xy0)

            nn2 = len(cl)-(len(fl) - n2)
            cl2, fl2 = cl[n1:nn2], fl[n1:n2]
            cl20, xy0 = _convert(cl2, fl2, wcs_proj, sky_to_sky, xy0)

            cl3, fl3 = cl[nn2:], fl[n2:]
            cl30, xy0 = _convert(cl3, fl3, wcs_proj, sky_to_sky, xy0)

            new_cl = cl10 + cl20 + cl30

#             while cl:
#                 if len(fl) == 0:
#                     fl = ds9_shape_defs[l1.name].args_list

#                 if fl[0] == CoordOdd and fl[1] == CoordEven:

#                     ll = sky_to_sky(tuple(cl[:2]))
#                     xy0 = wcs_proj.topixel(ll)
#                     new_cl.extend(xy0)
#                     cl = cl[2:]
#                     fl = fl[2:]
#                 elif fl[0] == Distance:
#                     degree_per_pixel = estimate_cdelt(wcs_proj, sky_to_sky,
#                                                       *xy0)
#                     new_cl.append(cl[0]/degree_per_pixel)
#                     cl = cl[1:]
#                     fl = fl[1:]
#                 elif fl[0] == Angle:
#                     rot = estimate_angle(wcs_proj, sky_to_sky, *xy0)
#                     new_cl.append(cl[0]+rot)
#                     cl = cl[1:]
#                     fl = fl[1:]
#                 else:
#                     raise Exception("Unknown format: %s" % fl[0])

            l1n = copy.copy(l1)

            l1n.coord_list = new_cl
            l1n.coord_format = "image"
            yield l1n, c1

        else:
            yield l1, c1



def deprecated_sky_to_image(l, wcs):

    proj = get_kapteyn_projection(wcs)

    # set degree_per_pixel which will be used to transform angular distance
    if wcs.has_cdi_ja():
        warnings.warn("wcs with CDI_J not fully supported.")
        degree_per_pixel = ((wcs.cd**2).sum()/2.)**.5

        #raise Exception("Not implemented yet")
    else:
        degree_per_pixel = ((wcs.cdelt**2).sum()/2.)**.5

    for l1, c1 in l:
        if isinstance(l1, Shape) and l1.coord_format == source_coord_format:
            cl = l1.coord_list
            fl = ds9_shape_defs[l1.name].args_list
            new_cl = []

            while cl:
                if len(fl) == 0:
                    fl = ds9_shape_defs[l1.name].args_list

                if fl[0] == CoordOdd and fl[1] == CoordEven:

                    new_cl.extend(wcs.world2pixel(np.array([cl[:2]]))[0])
                    cl = cl[2:]
                    fl = fl[2:]
                elif fl[0] == Distance:
                    new_cl.append(cl[0]/degree_per_pixel)
                    cl = cl[1:]
                    fl = fl[1:]
                elif fl[0] == Angle:
                    new_cl.append(cl[0])
                    cl = cl[1:]
                    fl = fl[1:]
                else:
                    raise Exception("Unknown format: %s" % fl[0])

            l1n = copy.copy(l1)

            l1n.coord_list = new_cl
            l1n.coord_format = "image"
            yield l1n, c1

        else:
            yield l1, c1



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
    default_coord = "image"

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

            if is_wcs and default_coord in image_like_coordformats:
                # ciao formats
                coord_format = "unknown wcs"
            else:
                coord_format = default_coord

            l1n = copy.copy(l1)

            l1n.coord_list = coord_list
            l1n.coord_format = coord_format

            yield l1n, c1
        else:
            yield l1, c1



def _get_attr(attr_list, global_attrs):
    local_attr = [], {}
    for kv in attr_list:
        if len(kv) == 1:
            local_attr[0].append(kv[0])
        elif len(kv) == 2:
            local_attr[1][kv[0]] = kv[1]
        elif len(kv) > 2:
            local_attr[1][kv[0]] = kv[1:]

    attr0 = copy.copy(global_attrs[0])
    attr1 = copy.copy(global_attrs[1])

    if local_attr[0]:
        attr0.extend(local_attr[0])

    if local_attr[1]:
        attr1.update(local_attr[1])

    return attr0, attr1


def convert_attr(l):
    global_attr = [], {}

    parser = AttrParser()

    for l1, c1 in l:
        if isinstance(l1, Global):
            for kv in parser.parse_default(l1.text):
                if len(kv) == 1:
                    global_attr[0].append(kv[0])
                elif len(kv) == 2:
                    global_attr[1][kv[0]] = kv[1]

        elif isinstance(l1, Shape):
            if c1:
                attr_list = parser.parse_default(c1)
                attr0, attr1 = _get_attr(attr_list, global_attr)
            else:
                attr0, attr1 = global_attr
            l1n = copy.copy(l1)
            l1n.attr = attr0, attr1
            yield l1n, c1

        elif not l1 and c1:
            shape, attr_list = parser.parse_check_shape(c1)
            if shape:
                shape.attr = _get_attr(attr_list, global_attr)
                yield shape, c1
        else:
            yield l1, c1





class Shape(object):

    def __init__(self, shape_name, shape_params):
        self.name = shape_name
        self.params = shape_params

        self.comment = None
        self.exclude = False

    def __repr__(self):
        params_string = ",".join(map(repr, self.params))
        if self.exclude:
            return "Shape : -%s ( %s )" %  (self.name, params_string)
        else:
            return "Shape : %s ( %s )" %  (self.name, params_string)

    def set_exclude(self):
        self.exclude = True

class Property(object):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return "Property : " + repr(self.text)

class CoordCommand(Property):
    def __repr__(self):
        return "CoordCommand : " + repr(self.text)

class Global(Property):
    def __repr__(self):
        return "Global : " + repr(self.text)

class Comment(Property):
    def __repr__(self):
        return "Comment : " + repr(self.text)


class RegionPusher(object):
    def __init__(self):
        self.flush()

    def flush(self):
        self.stack = []
        self.comment = None

    def pushAtom(self, s, l, tok):
        #s = tok[-1]
        self.stack.append(tok[-1])

    def pushComment(self, s, l, tok):
        self.comment  = tok[-1].strip()



def as_comma_separated_list(al):

    l = [al[0]]
    comma = Literal(",").suppress()

    for a1 in al[1:]:
        l.append(comma)
        l.append(a1)

    return And(l)


class wcs_shape(object):
    def __init__(self, *kl, **kw):
        self.args_list = kl
        self.args_repeat = kw.get("repeat", None)

    def get_pyparsing(self):
        return [a.parser for a in self.args_list]



def define_shape(name, shape_args, args_repeat=None):
    lparen = Literal("(").suppress()
    rparen = Literal(")").suppress()
    comma = Literal(",").suppress()

    shape_name = CaselessKeyword(name)


    if args_repeat is None:
        shape_with_parens = And([shape_name, lparen,
                                 as_comma_separated_list(shape_args),
                                 rparen])

        shape_with_spaces = shape_name + And(shape_args)

    else:
        n1, n2 = args_repeat
        sl = []

        ss = shape_args[:n1]
        if ss:
            sl.append(as_comma_separated_list(ss))

        ss = shape_args[n1:n2]
        if ss:
            ar = as_comma_separated_list(ss)
            if sl:
                sl.extend([comma+ ar, ZeroOrMore(comma + ar)])
            else:
                sl.extend([ar, ZeroOrMore(comma + ar)])

        ss = shape_args[n2:]
        if ss:
            if sl:
                sl.extend([comma, as_comma_separated_list(ss)])
            else:
                sl.extend([as_comma_separated_list(ss)])

        sl = [shape_name, lparen] + sl + [rparen]
        #sl.append(rparen)

        shape_with_parens = And(sl)

        shape_with_spaces = shape_name + OneOrMore(And(shape_args))


    return (shape_with_parens | shape_with_spaces)


def test_define_shape():
    args = [s.parser for s in [CoordOdd, CoordEven, Distance]]
    circle_parser = define_shape("circle", args, args_repeat=None)

    p = circle_parser.parseString("circle(1:2:3, 2:4:5, 3.)")
    assert p[0] == "circle"
    assert isinstance(p[1], CoordOdd.type)
    assert isinstance(p[2], CoordEven.type)

    args = [s.parser for s in [CoordEven]]
    circle_parser = define_shape("circle", args, args_repeat=None)

    p = circle_parser.parseString("circle(1:2:3)")
    p = circle_parser.parseString("circle(1d2m3s)")
    assert p[0] == "circle"
    assert isinstance(p[1], CoordEven.type)

    args = [s.parser for s in [CoordOdd, CoordEven, Distance, Distance]]
    ell_parser = define_shape("ell", args, args_repeat=(2,4))

    p = ell_parser.parseString("ell(1:2:2, 2:2:2, 3, 4, 5, 6)")
    assert p[0] == "ell"
    assert isinstance(p[1], CoordOdd.type)
    assert isinstance(p[2], CoordEven.type)

    args = [s.parser for s in [CoordOdd, CoordEven]]
    polygon_parser = define_shape("polygon", args, args_repeat=(0,2))
    p = polygon_parser.parseString("polygon(3:2:4.22, 3:3:4., 3:2:3, 3.2)")
    assert p[0] == "polygon"
    assert isinstance(p[-2], CoordOdd.type)
    assert isinstance(p[2], CoordEven.type)
    #assert isinstance(p[-1], float)


def define_shape_helper(shape_defs):
    l = []

    for n, args in shape_defs.items():
        s = define_shape(n,
                         args.get_pyparsing(),
                         args_repeat = args.args_repeat)

        l.append(s)

    return Or(l)


ds9_shape_defs = dict(circle=wcs_shape(CoordOdd, CoordEven, Distance),
                      rotbox=wcs_shape(CoordOdd, CoordEven, Distance, Distance, Angle),
                      box=wcs_shape(CoordOdd, CoordEven, Distance, Distance, Angle),
                      polygon=wcs_shape(CoordOdd, CoordEven,
                                        repeat=(0,2)),
                      ellipse=wcs_shape(CoordOdd, CoordEven,
                                        Distance, Distance,
                                        Angle, repeat=(2,4)),
                      annulus=wcs_shape(CoordOdd, CoordEven,
                                        Distance, repeat=(2,3)),
                      panda=wcs_shape(CoordOdd, CoordEven,
                                      Angle, Angle, Integer,
                                      Distance, Distance, Integer),
                      epanda=wcs_shape(CoordOdd, CoordEven,
                                       Angle, Angle, Integer,
                                       Distance, Distance, Distance, Distance, Integer,
                                       Angle),
                      bpanda=wcs_shape(CoordOdd, CoordEven,
                                       Angle, Angle, Integer,
                                       Distance, Distance, Distance, Distance, Integer,
                                       Angle),
                      point=wcs_shape(CoordOdd, CoordEven),
                      )



def define_expr(regionShape, negate_func):

    minus = Literal("-").suppress()
    regionExclude = (minus + regionShape).setParseAction(negate_func)
    regionExpr = (regionShape | regionExclude)

    return regionExpr


def define_line(atom,
                separator,
                comment):

    atomSeparator = separator.suppress()

    atomList = atom + ZeroOrMore(atomSeparator + atom)

    line = (atomList + Optional(comment)) | \
           comment

    return line




def comment_shell_like(comment_begin, parseAction=None):

    c = comment_begin + restOfLine
    if parseAction:
        c = c.setParseAction(parseAction)

    return c


def define_simple_literals(literal_list, parseAction=None):

    l = MatchFirst([CaselessKeyword(k) for k in literal_list])

    if parseAction:
        l = l.setParseAction(parseAction)

    return l




class RegionParser(RegionPusher):

    def __init__(self):

        RegionPusher.__init__(self)

        self.shape_definition = ds9_shape_defs
        regionShape = define_shape_helper(self.shape_definition)
        regionShape = regionShape.setParseAction(lambda s, l, tok: Shape(tok[0], tok[1:]))

        regionExpr = define_expr(regionShape,
                                 negate_func=lambda s, l, tok: tok[-1].set_exclude(),
                                 )

        coord_command_keys = "PHYSICAL IMAGE FK4 B1950 FK5 J2000 GALACTIC ECLIPTIC ICRS LINEAR AMPLIFIER DETECTOR".split()

        coordCommand = define_simple_literals(coord_command_keys,
                                              parseAction=lambda s, l, tok:CoordCommand(tok[-1]))

        regionGlobal = comment_shell_like(CaselessKeyword("global"),
                                          lambda s, l, tok:Global(tok[-1]))

        regionAtom = (regionExpr | coordCommand | regionGlobal)

        regionAtom = regionAtom.setParseAction(self.pushAtom)

        regionComment = comment_shell_like(Literal("#"),
                                           parseAction=self.pushComment)

        line_simple = define_line(atom=regionAtom,
                                  separator=Literal(";"),
                                  comment=regionComment
                                  )

        line_w_composite = And([regionAtom, CaselessKeyword("||")]) \
                           + Optional(regionComment)

        line = Or([line_simple, line_w_composite])

        self.parser = Optional(line) + StringEnd()
        #self.parser.ignore(regionComment)
        #self.parser.ignore(regionProperty)
        #self.parser.ignore()



    def parseLine(self, l):
        self.parser.parseString(l)
        #assert len(self.stack) == 1
        s, c = self.stack, self.comment

        self.flush()

        return s, c

    def parse(self, s):

        for l in s.split("\n"):
            s, c = self.parseLine(l)

            if len(s) > 1:
                for s1 in s[:-1]:
                    yield s1, None

                yield s[-1], c
            elif len(s) == 1:
                yield s[-1], c
            elif c:
                yield None, c

            self.flush()


#def test():
#if 0:

    #a = rr.parseString("circle(30,40,30) a(3)")
#test()


class AttrParser(object):
    def __init__(self):
        ds9_attr_parser = attr_parser()

        ds9_shape_in_comment_defs = dict(text=wcs_shape(CoordOdd, CoordEven))
        regionShape = define_shape_helper(ds9_shape_in_comment_defs)
        regionShape = regionShape.setParseAction(lambda s, l, tok: Shape(tok[0], tok[1:]))


        self.parser_default = ds9_attr_parser

        line = Optional(And([regionShape, Optional(CaselessKeyword("||").suppress())])) + \
               ds9_attr_parser

        self.parser_with_shape = line


    def parse_default(self, s):
        return self.parser_default.parseString(s)

    def parse_check_shape(self, s):
        l = self.parser_with_shape.parseString(s)
        if isinstance(l[0], Shape):
            return l[0], l[1:]
        else:
            return None, l

def test_regionLine():

    test_string_1 = ["circle(109,253,28.950304) # comment 1",
                     "polygon(257,290,300.78944,271.78944,300.78944,178.21056,258,216,207.21056,178.21056)",
                     "polygon(273.98971,175.01029,274.01029,175.01029,274.01029,174.98971,273.98971,174.98971)",
                     "-rotbox(162,96.5,134,41,43.801537)",
                     "ellipse(172,328,23,41,27.300813)"]

    test_names = ["circle",
                  "polygon",
                  "polygon",
                  "rotbox",
                  "ellipse"]


    rp = RegionParser()

    for s, n in zip(test_string_1, test_names):
        s, c = rp.parseLine(s)
        assert len(s) == 1
        assert s[0].name == n

def test_comment():
    s = "circle(3323, 423, 423) # comment"

    rp = RegionParser()
    s, c = rp.parseLine(s)

    assert c == "comment"

    s = " # comment2"
    s, c = rp.parseLine(s)

    assert c == "comment2"


def test_global():
    s = 'global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source'

    rp = RegionParser()
    s, c = rp.parseLine(s)

    print s



def test_all():
    s = """global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source
circle(58,50,33.639205) # comment
circle(18:43:43,50:32:23,33.639205) # color=blue comment
circle(18:43:43,5:32:23,33.639205) # background comment
"""

    rp = RegionParser()
    #for s1 in s.split("\n"):
    #    ss = rp.parseLine(s1)
    ss = rp.parse(s)
    #ssl = list(ss)

    sss = [s1[0] for s1 in convert_attr(ss)]
    assert sss[0].attr[1]["color"] == "green"
    assert sss[1].attr[1]["color"] == "blue"
    assert sss[2].attr[0][-1] == "background"


    s = """global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source
circle(58,50,33.639205) # comment
fk5; circle(58,50,33.639205)
image
circle(18:43:43,50:32:23,33.639205) # color=blue comment
"""

    ss = rp.parse(s)

    sss = [s1[0] for s1 in check_wcs(ss) if isinstance(s1[0], Shape)]
    assert sss[0].coord_format == "image"
    assert sss[1].coord_format == "fk5"
    assert sss[2].coord_format == "fk5"
    #assert sss[1].attr[1]["color"] == "blue"
    #assert sss[2].attr[0][-1] == "background"



def read_region(s):
    " s: string "
    rp = RegionParser()
    ss = rp.parse(s)
    sss1 = convert_attr(ss)
    sss2 = check_wcs(sss1)

    r = [s1[0] for s1 in sss2 if isinstance(s1[0], Shape)]
    return r

def read_region_as_imagecoord(s, header):
    rp = RegionParser()
    ss = rp.parse(s)
    sss1 = convert_attr(ss)
    sss2 = check_wcs(sss1)
    sss3 = sky_to_image(sss2, header)

    r = [s1[0] for s1 in sss3 if isinstance(s1[0], Shape)]
    return r



import numpy as np
import pyfits
import pywcs



def test_read_region():

    s = open("../test01.reg").read()
    ss1 = read_region(s)

    fname="../test01.fits"
    f = pyfits.open(fname)
    ss2 = read_region_as_imagecoord(s, f[0].header)
    print ss2


def test_wcs_old():
    fname="../E300-2100.b1.img.fits"
    f = pyfits.open(fname)

    d, h = f[0].data, f[0].header
    d.shape = d.shape[-2:]

    w = pywcs.WCS(h)

    s = open("../test/t_01.reg").read()

    rp = RegionParser()
    ss = rp.parse(s)
    ss = list(ss)
    sss2 = [s1[0] for s1 in sky_to_image(check_wcs(ss), w, source_coord_format="fk5")]
    print sss2[-1].coord_list
    #print sss2

def test_ttt():
    s = open("../examples/test_annuli.reg").read()
    ss1 = read_region(s)

    fname="../examples/test01.fits"
    f = pyfits.open(fname)
    ss2 = read_region_as_imagecoord(s, f[0].header)


if __name__ == "__main__":
    #s2 = "panda(4112,4135,0,360,4,37.006913,74.013826,1)\n"

    #s2 = "panda(4112,4135,0,90,1,37.006913,74.013826,1) ||\n"
    #s = open("../examples/test_annuli.reg").read()
    s = open("../examples/test_text.reg").read()
    rp = RegionParser()
    #ss = list(rp.parse(s))
    ss1 = read_region(s)



    #print list(ss1)
    #att = AttrParser()
    #print att.parse_default("abc=3 def=2")

