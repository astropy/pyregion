import matplotlib.pyplot as plt
from demo_helper import show_region

region_list = [
    "test_annuli.reg",
    "test_annuli_wcs.reg",
    "test_annuli_ciao.reg",
]

fig = plt.figure(figsize=(6, 6))

ax_list = show_region(fig, region_list)
for ax in ax_list:
    ax.set_xlim(596, 1075)
    ax.set_ylim(585, 1057)

plt.draw()
plt.show()
