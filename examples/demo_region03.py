import pyfits
import matplotlib.pyplot as plt
import pyregion

import math
import sys

try:
    import pywcsgrid2
except:
    print "You require matplotlib 0.99 and later that include axes_grid toolkit"
    sys.exit(0)

try:
    from mpl_toolkits.axes_grid.axes_grid import AxesGrid
except ImportError:
    print "You require pywcsgrid2."
    sys.exit(0)

def get_test_header():
    cards = pyfits.CardList()
    for l in open("sample_fits01.header"):
        card = pyfits.Card()
        card.fromstring(l.strip())
        cards.append(card)
    h = pyfits.Header(cards)
    return h

if 1:

    region_list = ["test_text.reg", "test_context.reg"]

    h = get_test_header()

    n = len(region_list)
    nx = int(math.ceil(n**.5))
    ny = int(math.ceil(1.*n/nx))


    fig = plt.figure(1, figsize=(7,5))
    fig.clf()
    nrows_ncols = (ny, nx)
    grid= AxesGrid(fig, 111, nrows_ncols,
                   ngrids=n,  add_all=True, share_all=True,
                   axes_class=(pywcsgrid2.Axes, dict(header=h)))

    ax = grid[0]
    ax.set_xlim(300, 1300)
    ax.set_ylim(300, 1300)
    ax.set_aspect(1)

    #plt.imshow(d, origin="lower", cmap=plt.cm.gray_r)

    from mpl_toolkits.axes_grid.anchored_artists import AnchoredText

    for ax, reg_name in zip(grid, region_list):
        r = pyregion.open(reg_name).as_imagecoord(h)

        patch_list, text_list = r.get_mpl_patches_texts()
        for p in patch_list:
            ax.add_patch(p)
        for t in text_list:
            ax.add_artist(t)


        atext = AnchoredText(reg_name.replace("_", r"\_"),
                             loc=2)
        ax.add_artist(atext)

    plt.draw()
    plt.show()
