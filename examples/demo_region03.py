import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
from astropy.io.fits import Header
from astropy.wcs import WCS
from astropy.visualization.wcsaxes import WCSAxes
import pyregion

region_list = [
    "test_text.reg",
    "test_context.reg",
]

# Create figure
fig = plt.figure(figsize=(8, 4))

# Parse WCS information
header = Header.fromtextfile('sample_fits01.header')
wcs = WCS(header)

# Create axes
ax1 = WCSAxes(fig, [0.1, 0.1, 0.4, 0.8], wcs=wcs)
fig.add_axes(ax1)
ax2 = WCSAxes(fig, [0.5, 0.1, 0.4, 0.8], wcs=wcs)
fig.add_axes(ax2)

# Hide labels on y axis
ax2.coords[1].set_ticklabel_position('')

for ax, reg_name in zip([ax1, ax2], region_list):

    ax.set_xlim(300, 1300)
    ax.set_ylim(300, 1300)
    ax.set_aspect(1)

    r = pyregion.open(reg_name).as_imagecoord(header)

    patch_list, text_list = r.get_mpl_patches_texts()

    for p in patch_list:
        ax.add_patch(p)

    for t in text_list:
        ax.add_artist(t)

    atext = AnchoredText(reg_name, loc=2)

    ax.add_artist(atext)

plt.draw()
plt.show()
