import matplotlib.pyplot as plt
from demo_helper import show_region

region_list = [
    "test01_fk5_sexagecimal.reg",
    "test01_gal.reg",
    "test01_img.reg",
    "test01_ds9_physical.reg",
    "test01_fk5_degree.reg",
    "test01_mixed.reg",
    "test01_ciao.reg",
    "test01_ciao_physical.reg",
]

fig = plt.figure(1, figsize=(6, 5))
fig.clf()

ax_list = show_region(fig, region_list)
for ax in ax_list:
    ax.set_xlim(596, 1075)
    ax.set_ylim(585, 1057)

plt.draw()
plt.show()
