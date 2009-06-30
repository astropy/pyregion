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

patch_list, text_list = as_mpl_artists(r)
for p in patch_list:
    ax.add_patch(p)
for t in text_list:
    ax.add_artist(t)

plt.show()

