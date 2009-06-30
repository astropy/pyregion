import sys

try:
    import pyfits
except ImportError:
    print "This example requires the pyfits module installed"
    sys.exit(0)

import matplotlib.pyplot as plt
import matplotlib.cm as cm

from pyregion import read_region_as_imagecoord
from pyregion.mpl_helper import as_mpl_artists

# read in the image
xray_name="pspc_skyview.fits"
f_xray = pyfits.open(xray_name)

try:
    import pywcsgrid2
    ax=pywcsgrid2.subplot(111, header=f_xray[0].header)
except ImportError:
    ax=plt.subplot(111)

ax.imshow(f_xray[0].data, cmap=cm.gray, vmin=0., vmax=0.00038, origin="lower")


reg_name = "test.reg"
r = read_region_as_imagecoord(open(reg_name).read(), header=f_xray[0].header)

from pyregion.mpl_helper import properties_func_default

# Use custom function for patch attribute
def fixed_color(shape, saved_attrs):
    
    attr_list, attr_dict = saved_attrs
    attr_dict["color"] = "red"
    kwargs = properties_func_default(shape, (attr_list, attr_dict))

    # This is just for a demonstration.  Setting alpha value does not
    # affect the alpha of the edge color, which I think a mpl bug.
    kwargs["alpha"]=0.5

    return kwargs

# select region shape with tag=="Group 1"
r1 = [rr for rr in r if rr.attr[1].get("tag") == "Group 1"]
patch_list1, artist_list1 = as_mpl_artists(r1, fixed_color)

r2 = [rr for rr in r if rr.attr[1].get("tag") != "Group 1"]
patch_list2, artist_list2 = as_mpl_artists(r2)

for p in patch_list1 + patch_list2:
    ax.add_patch(p)
for t in artist_list1 + artist_list2:
    ax.add_artist(t)

plt.show()

