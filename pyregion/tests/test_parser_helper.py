from pyregion.parser_helper import define_shape
from pyregion.region_numbers import CoordOdd, CoordEven, Distance


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
    ell_parser = define_shape("ell", args, args_repeat=(2, 4))

    p = ell_parser.parseString("ell(1:2:2, 2:2:2, 3, 4, 5, 6)")
    assert p[0] == "ell"
    assert isinstance(p[1], CoordOdd.type)
    assert isinstance(p[2], CoordEven.type)

    args = [s.parser for s in [CoordOdd, CoordEven]]
    polygon_parser = define_shape("polygon", args, args_repeat=(0, 2))
    p = polygon_parser.parseString("polygon(3:2:4.22, 3:3:4., 3:2:3, 3.2)")
    assert p[0] == "polygon"
    assert isinstance(p[-2], CoordOdd.type)
    assert isinstance(p[2], CoordEven.type)
