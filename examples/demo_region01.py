import matplotlib.pyplot as plt
import pyregion

import math

import pyfits

def demo_header():
    cards = pyfits.CardList()
    for l in open("test.header"):
        card = pyfits.Card()
        card.fromstring(l.strip())
        cards.append(card)
    h = pyfits.Header(cards)
    return h


def show_region(fig, region_list):
    h = demo_header()

    n = len(region_list)
    nx = int(math.ceil(n**.5))
    ny = int(math.ceil(1.*n/nx))


    nrows_ncols = (ny, nx)

    grid = [plt.subplot(ny, nx, i+1) for i in range(n)]

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


if 1:

    region_list = ["test01_fk5_sexagecimal.reg",
                   "test01_gal.reg",
                   "test01_img.reg",
                   "test01_ds9_physical.reg",
                   "test01_fk5_degree.reg",
                   "test01_mixed.reg",
                   "test01_ciao.reg",
                   "test01_ciao_physical.reg",
                   ]

    fig = plt.figure(1, figsize=(6,5))
    fig.clf()

    ax_list = show_region(fig, region_list)
    for ax in ax_list:
        ax.set_xlim(596, 1075)
        ax.set_ylim(585, 1057)

    plt.draw()
    plt.show()
