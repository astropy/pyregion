import sys

try:
    import pyfits
except ImportError:
    print "This example requires the pyfits module installed"
    sys.exit(0)

import matplotlib.pyplot as plt

from pyregion import read_region_as_imagecoord
from pyregion.mpl_helper import as_mpl_artists
from pyregion.region_to_filter import as_region_filter

# read in the image
xray_name="pspc_skyview.fits"
f_xray = pyfits.open(xray_name)

reg_name = "test.reg"
r = read_region_as_imagecoord(open(reg_name).read(), header=f_xray[0].header)
ff = as_region_filter(r)
#print ff
m = ff.mask(f_xray[0].data.shape)

ax = plt.subplot(121)
plt.imshow(m, origin="lower")

patch_list, text_list = as_mpl_artists(r)
for p in patch_list:
    ax.add_patch(p)
for t in text_list:
    ax.add_artist(t)

# another region

reg_name = "test02.reg"
r = read_region_as_imagecoord(open(reg_name).read(), header=f_xray[0].header)
ff = as_region_filter(r)
#print ff
m = ff.mask(f_xray[0].data.shape)

ax = plt.subplot(122)
plt.imshow(m, origin="lower")

patch_list, text_list = as_mpl_artists(r)
for p in patch_list:
    ax.add_patch(p)
for t in text_list:
    ax.add_artist(t)

plt.show()

