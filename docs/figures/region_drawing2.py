import matplotlib.pyplot as plt
import matplotlib.cm as cm
from astropy.io import fits
import pyregion

# read in the image
xray_name = "pspc_skyview.fits"
f_xray = fits.open(xray_name)

try:
    from astropy.wcs import WCS
    from astropy.visualization.wcsaxes import WCSAxes

    wcs = WCS(f_xray[0].header)
    fig = plt.figure()
    ax = WCSAxes(fig, [0.1, 0.1, 0.8, 0.8], wcs=wcs)
    fig.add_axes(ax)
except ImportError:
    ax = plt.subplot(111)

ax.imshow(f_xray[0].data, cmap=cm.gray, vmin=0., vmax=0.00038, origin="lower")

reg_name = "test.reg"
r = pyregion.open(reg_name).as_imagecoord(header=f_xray[0].header)

from pyregion.mpl_helper import properties_func_default


# Use custom function for patch attribute
def fixed_color(shape, saved_attrs):
    attr_list, attr_dict = saved_attrs
    attr_dict["color"] = "red"
    kwargs = properties_func_default(shape, (attr_list, attr_dict))

    return kwargs


# select region shape with tag=="Group 1"
r1 = pyregion.ShapeList([rr for rr in r if rr.attr[1].get("tag") == "Group 1"])
patch_list1, artist_list1 = r1.get_mpl_patches_texts(fixed_color)

r2 = pyregion.ShapeList([rr for rr in r if rr.attr[1].get("tag") != "Group 1"])
patch_list2, artist_list2 = r2.get_mpl_patches_texts()

for p in patch_list1 + patch_list2:
    ax.add_patch(p)
for t in artist_list1 + artist_list2:
    ax.add_artist(t)

plt.show()
