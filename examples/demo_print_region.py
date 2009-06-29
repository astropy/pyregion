from pyregion import read_region, read_region_as_imagecoord

import math

import pyfits

def test_header():
    cards = pyfits.CardList()
    for l in open("test.header"):
        card = pyfits.Card()
        card.fromstring(l.strip())
        cards.append(card)
    h = pyfits.Header(cards)
    return h

def print_region(r):
    for i, l in enumerate(r):
        print "[region %d]" % (i+1)
        print
        print "%s; %s(%s)" % (l.coord_format,
                              l.name,
                              ", ".join([str(s) for s in l.coord_list]))

        print l.attr[0]
        print ", ".join(["%s=%s" % (k, v.strip()) for k, v in l.attr[1].items()])
        print

if __name__ == "__main__":
    print "** coordinate in FK5 **"
    print
    region_name = "test01_print.reg"
    #region_name = "test_text.reg"
    #region_name = "test01.reg"
    r = read_region(open(region_name).read())
    print_region(r)

    print
    print
    print "** coordinate in image **"
    print
    header = test_header()
    r = read_region_as_imagecoord(open(region_name).read(), header)
    print_region(r)

