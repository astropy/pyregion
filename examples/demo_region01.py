import matplotlib.pyplot as plt
from pyregion import read_region_as_imagecoord
from pyregion.mpl_helper import as_mpl_artists

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

        r = read_region_as_imagecoord(open(reg_name).read(), header=h)

        patch_list, text_list = as_mpl_artists(r)
        for p in patch_list:
            ax.add_patch(p)
        for t in text_list:
            ax.add_artist(t)

        ax.set_title(reg_name.replace("_", r"\_"), size=10)
        for t in ax.get_xticklabels() + ax.get_yticklabels():
            t.set_visible(False)

    return grid


if __name__ == "__main__":

    region_list = ["test01_fk5_sexagecimal.reg",
                   "test01_gal.reg",
                   "test01_img.reg",
                   "test01_ciao.reg",
                   "test01_fk5_degree.reg",
                   "test01_mixed.reg"]

    fig = plt.figure(1, figsize=(6,5))
    fig.clf()

    ax_list = show_region(fig, region_list)
    for ax in ax_list:
        ax.set_xlim(596, 1075)
        ax.set_ylim(585, 1057)

    plt.draw()
    plt.show()
