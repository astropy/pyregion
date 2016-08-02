"""Example how to read and print regions.
"""
from astropy.io.fits import Header
import pyregion


def print_shape_list(shape_list):
    for idx, shape in enumerate(shape_list, start=1):
        print("[region %d]" % idx)
        print()
        print("%s; %s(%s)" % (shape.coord_format,
                              shape.name,
                              ", ".join([str(s) for s in shape.coord_list])))

        print(shape.attr[0])
        print(", ".join(["%s=%s" % (k, v.strip()) for k, v in list(shape.attr[1].items())]))
        print()


if __name__ == "__main__":
    print("** coordinate in FK5 **")
    print()
    filename = "test01_print.reg"
    # filename = "test_text.reg"
    # filename = "test01.reg"
    shape_list = pyregion.open(filename)
    print_shape_list(shape_list)

    print()
    print()
    print("** coordinate in image **")
    print()
    header = Header.fromtextfile("test.header")
    shape_list2 = shape_list.as_imagecoord(header=header)
    print_shape_list(shape_list2)
