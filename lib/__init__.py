
import parser_ds9 as RP

def parse(region_string):
    rp = RP.RegionParser()
    return rp.parseString(region_string)

if 0:
    s = open("../test/t_10.reg").read()

    rp = RP.RegionParser()
    ss = rp.parse(s)
    ss = list(ss)

