from astropy.io.fits import Header
import matplotlib.pyplot as plt
import pyregion


# read in the image
def demo_header():
    return Header.fromtextfile("sample_fits02.header")


header = demo_header()  # sample fits header
shape = (header["NAXIS1"], header["NAXIS2"])

reg_name = "test.reg"
r = pyregion.open(reg_name).as_imagecoord(header)
m = r.get_mask(shape=shape)

fig = plt.figure(1, figsize=(7, 5))
ax = plt.subplot(121)
plt.imshow(m, origin="lower")

patch_list, text_list = r.get_mpl_patches_texts()
for p in patch_list:
    ax.add_patch(p)
for t in text_list:
    ax.add_artist(t)

# another region

reg_name = "test02.reg"
r = pyregion.open(reg_name).as_imagecoord(header)
m = r.get_mask(shape=shape)

ax = plt.subplot(122)
plt.imshow(m, origin="lower")

patch_list, text_list = r.get_mpl_patches_texts()
for p in patch_list:
    ax.add_patch(p)
for t in text_list:
    ax.add_artist(t)

plt.show()
