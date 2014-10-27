import os

import matplotlib.pyplot as plt
import matplotlib.cm as cm

import pyregion
try:
    from astropy.io import fits as pyfits
except ImportError:
    import pyfits

ROOT = os.path.dirname(os.path.abspath(__file__))

# read in the image
xray_name=os.path.join(ROOT, "pspc_skyview.fits")
f_xray = pyfits.open(xray_name)

try:
    import pywcsgrid2
    ax=pywcsgrid2.subplot(111, header=f_xray[0].header)
except ImportError:
    ax=plt.subplot(111)

ax.imshow(f_xray[0].data,
          cmap=cm.gray, vmin=0., vmax=0.00038, origin="lower")

reg_name = os.path.join(ROOT, "test.reg")
r = pyregion.open(reg_name).as_imagecoord(f_xray[0].header)

patch_list, text_list = r.get_mpl_patches_texts()
for p in patch_list:
    ax.add_patch(p)
for t in text_list:
    ax.add_artist(t)

plt.savefig('test1.png')

