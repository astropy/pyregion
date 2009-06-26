import pyfits
import matplotlib.pyplot as plt
import pywcsgrid2
from pyregion.parser_ds9 import read_region_as_imagecoord
from pyregion.mpl_helper import as_mpl_patches

import math
from mpl_toolkits.axes_grid.axes_grid import AxesGrid

if 1:

    region_list = ["test01_fk5_sexagecimal.reg",
                   "test01_gal.reg",
                   "test01_img.reg",
                   "test01_ciao.reg",
                   "test01_fk5_degree.reg",
                   "test01_mixed.reg"]

    f = pyfits.open("test01.fits")
    h, d = f[0].header, f[0].data

    n = len(region_list)
    nx = int(math.ceil(n**.5))
    ny = int(math.ceil(1.*n/nx))


    fig = plt.figure(1, figsize=(6,5))
    fig.clf()
    nrows_ncols = (ny, nx)
    grid= AxesGrid(fig, 111, nrows_ncols,
                   ngrids=n,  add_all=True, share_all=True,
                   axes_class=(pywcsgrid2.Axes, dict(header=h)))

    ax = grid[0]
    ax.set_xlim(596, 1075)
    ax.set_ylim(585, 1057)
    ax.set_aspect(1)

    #plt.imshow(d, origin="lower", cmap=plt.cm.gray_r)

    from mpl_toolkits.axes_grid.anchored_artists import AnchoredText

    for ax, reg_name in zip(grid, region_list):
        r = read_region_as_imagecoord(open(reg_name).read(), header=h)

        for p in as_mpl_patches(r):
            ax.add_patch(p)

        atext = AnchoredText(reg_name.replace("_", r"\_"),
                             loc=2)
        ax.add_artist(atext)

    plt.draw()
    plt.show()
