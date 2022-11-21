from math import pi
from pyregion.region_numbers import (usn, simple_integer, sexadecimal60, Sixty,
                              hms_number, dms_number, angular_distance,
                              CoordOdd, HMS)


def test_usn():
    for f in ["32.4", "0.23", "0.3e-7", "1.234e+7"]:
        assert usn.parseString(f)[0] == f


def test_integer():
    for f in ["32", "+3"]:
        assert simple_integer.parseString(f)[0].text == f


def test_sexadecimal():
    s = sexadecimal60.parseString

    assert s("32:24:32.2")[0].v == Sixty(1, 32, 24, 32.2).v
    assert s("-32:24:32.2")[0].v == Sixty(-1, 32, 24, 32.2).v
    assert s("+32:24:32.2")[0].v == Sixty(1, 32, 24, 32.2).v


def test_hms():
    s = hms_number.parseString

    assert s("32h24m32.2s")[0].v == Sixty(1, 32, 24, 32.2).v
    assert s("0h24m32.2s")[0].v == Sixty(1, 0, 24, 32.2).v
    assert s("32h")[0].v == Sixty(1, 32, 0, 0).v


def test_dms():
    s = dms_number.parseString

    assert s("32d24m32.2s")[0].v == Sixty(1, 32, 24, 32.2).v
    assert s("-32d24m32.2s")[0].v == Sixty(-1, 32, 24, 32.2).v
    assert s("32d")[0].v == Sixty(1, 32, 0, 0).v


def test_ang_distance():
    s = angular_distance.parseString

    assert s("32.3'")[0].v == Sixty(1, 0, 32.3, 0.).v
    assert s("32\'24\"")[0].v == Sixty(1, 0, 32, 24).v
    assert s("0.3d")[0].v == Sixty(1, 0.3, 0, 0).v
    assert s("1r")[0].v == Sixty(1, 1./pi*180., 0, 0).v


def test_coord_odd():
    s = CoordOdd.parser.parseString

    assert s("32h24m32.2s")[0].v == Sixty(1, 32, 24, 32.2).v
    assert s("32:24:32.2s")[0].v == Sixty(1, 32, 24, 32.2).v
    assert s("32.24")[0].v == 32.24

    s1 = s("32:24:32.2s")[0]
    assert isinstance(s1, HMS)
