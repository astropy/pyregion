from math import pi
from pyparsing import Literal, Optional, Combine, Or, Word, nums


def _unsigned_simple_number():
    # fnumber : 102.43, 12304.3e10,
    #           .32???
    point = Literal(".")
    e = Literal("e") | Literal("E")  # CaselessLiteral( "E" )
    fnumber = Combine(Word(nums) +
                      Optional(point + Optional(Word(nums))) +
                      Optional(e + Word("+-" + nums, nums)))

    return fnumber  # .setParseAction(lambda s,l,t: (float(t[0]), t[0]))


usn = _unsigned_simple_number()


def get_default(v):
    def _f(s, l, tok):
        if tok:
            return tok
        return v

    return _f


optional_sign = Optional(Literal("+") | Literal("-")).setParseAction(get_default(""))


class SimpleNumber(object):
    def __repr__(self):
        return "Number(%s)" % (self.text,)

    def __str__(self):
        return self.__repr__()

    def __init__(self, text):
        self.text = text
        self.v = float(text)


def _simple_number():
    s = Combine(optional_sign + usn)
    s.setParseAction(lambda s, l, tok: SimpleNumber(tok[0]))

    return s


simple_number = _simple_number()


class SimpleInteger(object):
    def __repr__(self):
        return "Number(%s)" % (self.text,)

    def __str__(self):
        return self.__repr__()

    def __init__(self, text):
        self.text = text
        self.v = int(text)


def _unsigned_integer():
    s = Combine(Optional("+") + Word(nums))
    s.setParseAction(lambda s, l, tok: SimpleInteger(tok[0]))

    return s


simple_integer = _unsigned_integer()


class Sixty(object):
    def __init__(self, sn, d, m, s):
        self.v = sn * (d + (m + s / 60.) / 60.)
        self.degree = self.v


class HMS(object):
    def __repr__(self):
        return "HMS(%s)" % (self.text,)

    def __init__(self, kl):
        self.text = "".join(kl)

        if kl[0] == "-":
            sn = -1
        else:
            sn = +1

        kkl = kl[1::2]
        if len(kkl) == 3:
            d, m, s = float(kl[1]), float(kl[3]), float(kl[5])
        elif len(kkl) == 2:
            d, m, s = float(kl[1]), float(kl[3]), 0.
        else:
            d, m, s = float(kl[1]), 0., 0.

        self.v = sn * (d + (m + s / 60.) / 60.)
        self.degree = self.v * 15


class DMS(object):
    def __repr__(self):
        return "DMS(%s)" % (self.text,)

    def __init__(self, kl):
        self.text = "".join(kl)

        if kl[0] == "-":
            sn = -1
        else:
            sn = +1

        kkl = kl[1::2]
        if len(kkl) == 3:
            d, m, s = float(kl[1]), float(kl[3]), float(kl[5])
        elif len(kkl) == 2:
            d, m, s = float(kl[1]), float(kl[3]), 0.
        else:
            d, m, s = float(kl[1]), 0., 0.

        self.v = sn * (d + (m + s / 60.) / 60.)
        self.degree = self.v


class AngularDistance(object):
    def __repr__(self):
        return "Ang(%s)" % (self.text,)

    def __init__(self, kl):
        self.text = "".join(kl)

        d, m, s = 0, 0, 0
        if kl[1] == "d": # format of "3.5d"
            d = float(kl[0])
        elif kl[1] == "r": # format of "3.5r"
            d = float(kl[0]) / pi * 180.
        else: # 3'5" or 3'
            if kl[1] == "'":
                m = float(kl[0])
                if len(kl) == 4:
                    s = float(kl[2])
            else:  # should be a format of 5"
                s = float(kl[0])

        self.v = d + (m + s / 60.) / 60.
        self.degree = self.v


def _sexadecimal():
    colon = Literal(":")

    s = optional_sign + usn + colon + usn + \
        Optional(colon + usn)

    return s


sexadecimal60 = _sexadecimal().setParseAction(lambda s, l, tok: DMS(tok))
sexadecimal24 = _sexadecimal().setParseAction(lambda s, l, tok: HMS(tok))


def _hms_number():
    _h = (usn + Literal("h")).leaveWhitespace()
    _m = (usn + Literal("m")).leaveWhitespace()
    _s = (usn + Literal("s")).leaveWhitespace()

    hms = optional_sign + _h + Optional(_m + Optional(_s))

    hms = hms.setParseAction(lambda s, l, tok: HMS(tok))

    return hms


def _dms_number():
    _d = (usn + Literal("d")).leaveWhitespace()
    _m = (usn + Literal("m")).leaveWhitespace()
    _s = (usn + Literal("s")).leaveWhitespace()

    dms = optional_sign + _d + Optional(_m + Optional(_s))

    dms = dms.setParseAction(lambda s, l, tok: DMS(tok))

    return dms


hms_number = _hms_number()
dms_number = _dms_number()


def _angular_distance():
    _m = (usn + Literal("\'").leaveWhitespace())
    _s = (usn + Literal("\"").leaveWhitespace())
    _dr = (usn + Or([Literal("d"),
                     Literal("r")]).leaveWhitespace())

    ms = Or([_m + Optional(_s), _s, _dr])

    ms = ms.setParseAction(lambda s, l, tok: AngularDistance(tok))

    return ms


angular_distance = _angular_distance()


class Arg(object):
    def __init__(self, type, parser):
        self.type = type
        self.parser = parser


class CoordOdd:
    parser = (hms_number | sexadecimal24 | simple_number)
    type = HMS


class CoordEven:
    parser = (dms_number | sexadecimal60 | simple_number)
    type = DMS


class Distance:
    parser = (angular_distance | simple_number)
    type = AngularDistance


class Angle:
    parser = (simple_number)
    type = simple_number


class Integer:
    parser = simple_integer
    type = simple_number
