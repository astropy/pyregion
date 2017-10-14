import copy

from pyparsing import (Literal, CaselessKeyword, Word, Optional, Combine,
                       ZeroOrMore, nums, alphas, And, Or, quotedString,
                       QuotedString, White)

from .region_numbers import CoordOdd, CoordEven, Distance, Angle

from .parser_helper import wcs_shape, define_shape_helper, Shape


def get_ds9_attr_parser():
    lhs = Word(alphas)
    paren = QuotedString("(", endQuoteChar=")")
    rhs = Or([Word(alphas + nums),
              Combine(Literal("#") + Word(alphas + nums)),  # color with '#'
              Combine(Word(alphas) + White() + Word(nums)),  # for point
              quotedString,
              QuotedString("{", endQuoteChar="}"),
              paren + ZeroOrMore(paren),
              Word(nums + " "),
              Word(nums + ".")
              ])
    expr = lhs + Optional(Literal("=").suppress() + rhs)
    expr.setParseAction(lambda s, l, tok: tuple(tok))

    return ZeroOrMore(expr)


ds9_shape_in_comment_defs = dict(
    text=wcs_shape(CoordOdd, CoordEven),
    vector=wcs_shape(CoordOdd, CoordEven,
                     Distance, Angle),
    composite=wcs_shape(CoordOdd, CoordEven, Angle),
    ruler=wcs_shape(CoordOdd, CoordEven, CoordOdd, CoordEven),
    compass=wcs_shape(CoordOdd, CoordEven, Distance),
    projection=wcs_shape(CoordOdd, CoordEven, CoordOdd, CoordEven, Distance),
    segment=wcs_shape(CoordOdd, CoordEven,
                      repeat=(0, 2))
)


class Ds9AttrParser(object):
    def set_continued(self, s, l, tok):
        self.continued = True

    def __init__(self):
        self.continued = False

        ds9_attr_parser = get_ds9_attr_parser()

        regionShape = define_shape_helper(ds9_shape_in_comment_defs)
        regionShape = regionShape.setParseAction(lambda s, l, tok: Shape(tok[0], tok[1:]))

        self.parser_default = ds9_attr_parser

        cont = CaselessKeyword("||").setParseAction(self.set_continued).suppress()
        line = Optional(And([regionShape, Optional(cont)])) + ds9_attr_parser

        self.parser_with_shape = line

    def parse_default(self, s):
        return self.parser_default.parseString(s)

    def parse_check_shape(self, s):
        l = self.parser_with_shape.parseString(s)
        if l and isinstance(l[0], Shape):
            if self.continued:
                l[0].continued = True
            return l[0], l[1:]
        else:
            return None, l


def get_attr(attr_list, global_attrs):
    """
    Parameters
    ----------
    attr_list : list
        A list of (keyword, value) tuple pairs
    global_attrs : tuple(list, dict)
        Global attributes which update the local attributes
    """
    local_attr = [], {}
    for kv in attr_list:
        keyword = kv[0]
        if len(kv) == 1:
            local_attr[0].append(keyword)
            continue
        elif len(kv) == 2:
            value = kv[1]
        elif len(kv) > 2:
            value = kv[1:]

        if keyword == 'tag':
            local_attr[1].setdefault(keyword, set()).add(value)
        else:
            local_attr[1][keyword] = value

    attr0 = copy.copy(global_attrs[0])
    attr1 = copy.copy(global_attrs[1])

    if local_attr[0]:
        attr0.extend(local_attr[0])

    if local_attr[1]:
        attr1.update(local_attr[1])

    return attr0, attr1
