import math
import matplotlib.pyplot as plt
import pyregion


def demo_header():
    from astropy.io.fits import Header
    return Header.fromtextfile("sample_fits01.header")


def show_region(fig, region_list):
    h = demo_header()

    n = len(region_list)
    nx = int(math.ceil(n ** .5))
    ny = int(math.ceil(1. * n / nx))

    nrows_ncols = (ny, nx)

    grid = [plt.subplot(ny, nx, i + 1) for i in range(n)]

    for ax, reg_name in zip(grid, region_list):
        ax.set_aspect(1)

        r = pyregion.open(reg_name).as_imagecoord(h)

        patch_list, text_list = r.get_mpl_patches_texts()
        for p in patch_list:
            ax.add_patch(p)
        for t in text_list:
            ax.add_artist(t)

        if plt.rcParams["text.usetex"]:
            reg_name = reg_name.replace("_", r"\_")
        ax.set_title(reg_name, size=10)
        for t in ax.get_xticklabels() + ax.get_yticklabels():
            t.set_visible(False)

    return grid
