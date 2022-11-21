from pyregion.ds9_attr_parser import get_ds9_attr_parser, get_attr, Ds9AttrParser


def test_attr():
    p = get_ds9_attr_parser()
    assert p.parseString("color=green")[0] == ("color", "green")
    assert p.parseString("font=\"123 123\"")[0] == ("font", '"123 123"')
    assert p.parseString("color")[0] == ("color",)
    assert p.parseString("tag={group 1}")[0] == ("tag", "group 1")
    assert p.parseString('color=#6a8')[0] == ("color", "#6a8")


def test_get_attr():
    attr_list = [('tag', 'group1'), ('tag', 'group2'),
                 ('tag', 'group3'), ('color', 'green')]
    global_attrs = [], {}

    attr = get_attr(attr_list, global_attrs)
    assert attr[0] == []
    assert attr[1] == {'color': 'green',
                       'tag': set(['group1', 'group3', 'group2'])}


def test_shape_in_comment():
    parser = Ds9AttrParser()

    r = parser.parse_check_shape("segment(0, 2)")
    assert r[0].name == "segment"
    assert r[1] == []

    r = parser.parse_check_shape("projection(0, 2, 3, 2, 4)")
    assert r[0].name == "projection"
    assert r[1] == []
