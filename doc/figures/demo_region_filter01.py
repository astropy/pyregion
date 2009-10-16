import sys

try:
    import pyfits
except ImportError:
    print "This example requires the pyfits module installed"
    sys.exit(0)

import matplotlib.pyplot as plt

import pyregion

# read in the image
xray_name="pspc_skyview.fits"
f_xray = pyfits.open(xray_name)

reg_name = "test.reg"
r = pyregion.open(reg_name).as_imagecoord(f_xray[0].header)
m = r.get_mask(shape=f_xray[0].data.shape)


fig = plt.figure(1, figsize=(7,5))
ax = plt.subplot(121)
plt.imshow(m, origin="lower")

patch_list, text_list = r.get_mpl_patches_texts()
for p in patch_list:
    ax.add_patch(p)
for t in text_list:
    ax.add_artist(t)

# another region

reg_name = "test02.reg"
r = pyregion.open(reg_name).as_imagecoord(f_xray[0].header)
m = r.get_mask(shape=f_xray[0].data.shape)

ax = plt.subplot(122)
plt.imshow(m, origin="lower")

patch_list, text_list = r.get_mpl_patches_texts()
for p in patch_list:
    ax.add_patch(p)
for t in text_list:
    ax.add_artist(t)

plt.show()

