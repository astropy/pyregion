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

ax.imshow(f_xray[0].data,
          cmap=cm.gray, vmin=0., vmax=0.00038, origin="lower")

reg_name = "test.reg"
r = pyregion.open(reg_name).as_imagecoord(f_xray[0].header)

patch_list, text_list = r.get_mpl_patches_texts()
for p in patch_list:
    ax.add_patch(p)
for t in text_list:
    ax.add_artist(t)

plt.show()
