from ..ds9_region_parser import RegionParser, Global


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
        s = rp.parseLine(s)[0]
        assert len(s) == 1
        assert s[0].name == n


def test_comment():
    s = "circle(3323, 423, 423) # comment"

    rp = RegionParser()
    c = rp.parseLine(s)[1]

    assert c == "comment"

    s = " # comment2"
    c = rp.parseLine(s)[1]

    assert c == "comment2"


def test_global():
    s = 'global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source'

    rp = RegionParser()
    ss = rp.parseLine(s)[0]

    assert isinstance(ss[0], Global)
