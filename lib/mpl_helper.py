import matplotlib.patches as patches

import numpy as np
import math

def rotated_polygon(xy, ox, oy, angle):
    # angle in degree
    theta = angle/180.*math.pi

    st = math.sin(theta)
    ct = math.cos(theta)

    xy = np.asarray(xy, dtype="d")
    x, y = xy[:,0], xy[:,1]
    x1 = x - ox
    y1 = y - oy

    x2 =  ct*x1 + -st*y1
    y2 =  st*x1 +  ct*y1

    xp = x2 + ox
    yp = y2 + oy

    return np.hstack((xp.reshape((-1,1)), yp.reshape((-1,1))))


   # sss3 = [s1[0] for s1 in sss2 if isinstance(s1[0], parser_ds9.Shape)]

def properties_func_default(shape):
    attr_list = shape.attr[0]
    attr_dict = shape.attr[1]

    kwargs = dict(edgecolor=attr_dict.get("color", None),
                  linewidth=int(attr_dict.get("width", 1)),
                  facecolor="none"
                  )

    if "background" in attr_list:
        kwargs["linestyle"] = "dashed"

    if shape.exclude:
        kwargs["hatch"] = "/"

    return kwargs


def _as_mpl_patches(shape_list,
                    properties_func=properties_func_default):

    for shape in shape_list:
        kwargs = properties_func(shape)

        if shape.name == "polygon":
            xy = np.array(shape.coord_list)
            xy.shape = -1,2

            yield patches.Polygon(xy, closed=True, **kwargs)

        elif shape.name == "rotbox" or shape.name == "box":
            xc, yc, w, h, rot = shape.coord_list
            _box = np.array([[-w/2., -h/2.],
                             [-w/2., h/2.],
                             [w/2., h/2.],
                             [w/2., -h/2.]])
            box = _box + [xc, yc]
            rotbox = rotated_polygon(box, xc, yc, rot)
            yield patches.Polygon(rotbox, closed=True, **kwargs)

        elif shape.name == "ellipse":
            xc, yc  = shape.coord_list[:2]
            angle = shape.coord_list[-1]

            maj_list, min_list = shape.coord_list[2:-1:2], shape.coord_list[3:-1:2]
            for maj, min in zip(maj_list, min_list):
                ell = patches.Ellipse((xc, yc), 2*maj, 2*min, angle=angle,
                                      **kwargs)
                yield ell

        elif shape.name == "annulus":
            xc, yc  = shape.coord_list[:2]
            r_list = shape.coord_list[2:]

            for r in r_list:
                ell = patches.Ellipse((xc, yc), 2*r, 2*r,
                                      **kwargs)
                yield ell

        elif shape.name == "circle":
            xc, yc, major = shape.coord_list
            ell = patches.Ellipse((xc, yc), 2*major, 2*major, angle=0,
                                  **kwargs)
            yield ell

        else:
            print "Unknown shape"

def as_mpl_patches(shape_list,
                   properties_func=properties_func_default):
    return list(_as_mpl_patches(shape_list,
                                properties_func=properties_func_default))


if 0:
    import parser_ds9
    regname = "az_region.reg"
    shape_list = region_read_as_imagecoord(regname, wcs)
    p = as_mpl_patches(shape_list)

    clf()
    ax = gca()
    [ax.add_patch(p1) for p1 in p]
    xlim(0,1500)
    ylim(0,1500)

    draw()

